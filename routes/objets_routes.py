from fastapi import APIRouter, Depends, HTTPException, status
from models.schemas import Objet
from utils.security import get_current_user
from database.mongo import db

router = APIRouter()

@router.post("/")
async def create_objet(objet: Objet, current_user: dict = Depends(get_current_user)):
    """
    Ajouter un nouvel objet IoT pour l'utilisateur connecté
    """
    # Vérifier si le capteur existe déjà
    existing = await db["objets"].find_one({"capteurId": objet.capteurId})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Capteur déjà enregistré"
        )
    
    # Préparer les données de l'objet
    objet_dict = objet.model_dump()
    objet_dict["utilisateur"] = current_user["id"]  # Assigner à l'utilisateur connecté
    
    # Insérer dans MongoDB
    result = await db["objets"].insert_one(objet_dict)
    
    return {
        "message": "Objet ajouté avec succès",
        "objet_id": str(result.inserted_id)
    }

@router.get("/")
async def get_objets(current_user: dict = Depends(get_current_user)):
    """
    Récupérer tous les objets de l'utilisateur connecté
    """
    # Récupérer les objets de l'utilisateur
    cursor = db["objets"].find({"utilisateur": current_user["id"]})
    objets = []
    
    async for obj in cursor:
        obj["id"] = str(obj.pop("_id"))  # Convertir _id en id
        objets.append(obj)
    
    return {
        "message": f"Trouvé {len(objets)} objets",
        "objets": objets
    }

@router.get("/{objet_id}")
async def get_objet_by_id(objet_id: str, current_user: dict = Depends(get_current_user)):
    """
    Récupérer un objet spécifique par son ID
    """
    from bson import ObjectId
    
    try:
        # Chercher l'objet par ID et utilisateur
        objet = await db["objets"].find_one({
            "_id": ObjectId(objet_id),
            "utilisateur": current_user["id"]
        })
        
        if not objet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Objet non trouvé"
            )
        
        objet["id"] = str(objet.pop("_id"))
        return objet
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID d'objet invalide"
        )

@router.delete("/{objet_id}")
async def delete_objet(objet_id: str, current_user: dict = Depends(get_current_user)):
    """
    Supprimer un objet de l'utilisateur connecté
    """
    from bson import ObjectId
    
    try:
        # Supprimer l'objet
        result = await db["objets"].delete_one({
            "_id": ObjectId(objet_id),
            "utilisateur": current_user["id"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Objet non trouvé ou non autorisé"
            )
        
        return {"message": "Objet supprimé avec succès"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID d'objet invalide"
        )