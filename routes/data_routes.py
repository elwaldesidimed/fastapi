from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from database.mongo import db
from models.schemas import Donnee, Seuil, Alerte
from utils.security import get_current_user

router = APIRouter()

@router.post("/")
async def save_data(payload: Donnee, current_user: dict = Depends(get_current_user)):
    """
    Enregistrer une nouvelle donnée de capteur
    Vérifie automatiquement les seuils et crée des alertes
    """
    # Vérifier si la donnée existe déjà
    existing = await db["donnees"].find_one({
        "capteurId": payload.capteurId,
        "timestamp": payload.timestamp
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Donnée déjà enregistrée pour ce timestamp"
        )
    
    # Vérifier que l'utilisateur possède ce capteur
    capteur_exists = await db["objets"].find_one({
        "capteurId": payload.capteurId,
        "utilisateur": current_user["id"]
    })
    if not capteur_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Capteur non trouvé ou non autorisé"
        )
    
    # Préparer les données
    data_dict = payload.model_dump()
    data_dict["owner_id"] = current_user["id"]
    
    # Enregistrer la donnée
    result = await db["donnees"].insert_one(data_dict)
    
    # Vérifier seuil et créer alerte si nécessaire
    seuil_doc = await db["seuils"].find_one({
        "capteurId": payload.capteurId,
        "owner_id": current_user["id"]
    })
    
    alerte_creee = False
    if seuil_doc and payload.valeur > seuil_doc.get("seuil_max", float('inf')):
        alerte = {
            "capteurId": payload.capteurId,
            "valeur": payload.valeur,
            "message": f"⚠ Valeur {payload.valeur} dépasse le seuil ({seuil_doc['seuil_max']})",
            "timestamp": payload.timestamp,
            "owner_id": current_user["id"]
        }
        await db["alertes"].insert_one(alerte)
        alerte_creee = True
    
    return {
        "message": "Donnée enregistrée avec succès",
        "data_id": str(result.inserted_id),
        "alerte_creee": alerte_creee
    }

@router.post("/seuil")
async def set_seuil(payload: Seuil, current_user: dict = Depends(get_current_user)):
    """
    Définir ou mettre à jour un seuil pour un capteur
    """
    # Vérifier que l'utilisateur possède ce capteur
    capteur_exists = await db["objets"].find_one({
        "capteurId": payload.capteurId,
        "utilisateur": current_user["id"]
    })
    if not capteur_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Capteur non trouvé ou non autorisé"
        )
    
    # Mettre à jour ou créer le seuil
    seuil_dict = payload.model_dump()
    seuil_dict["owner_id"] = current_user["id"]
    
    await db["seuils"].update_one(
        {"capteurId": payload.capteurId, "owner_id": current_user["id"]},
        {"$set": seuil_dict},
        upsert=True
    )
    
    return {"message": "Seuil mis à jour avec succès"}

@router.get("/{capteur_id}")
async def get_data(capteur_id: str, current_user: dict = Depends(get_current_user)):
    """
    Récupérer toutes les données d'un capteur
    """
    # Vérifier que l'utilisateur possède ce capteur
    capteur_exists = await db["objets"].find_one({
        "capteurId": capteur_id,
        "utilisateur": current_user["id"]
    })
    if not capteur_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Capteur non trouvé ou non autorisé"
        )
    
    # Récupérer les données
    cursor = db["donnees"].find({
        "capteurId": capteur_id,
        "owner_id": current_user["id"]
    }).sort("timestamp", -1)  # Trier par timestamp décroissant
    
    data = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        data.append(doc)
    
    return {
        "capteur_id": capteur_id,
        "total_donnees": len(data),
        "donnees": data
    }

@router.get("/{capteur_id}/latest")
async def get_latest_data(capteur_id: str, current_user: dict = Depends(get_current_user)):
    """
    Récupérer la dernière donnée d'un capteur
    """
    # Vérifier que l'utilisateur possède ce capteur
    capteur_exists = await db["objets"].find_one({
        "capteurId": capteur_id,
        "utilisateur": current_user["id"]
    })
    if not capteur_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Capteur non trouvé ou non autorisé"
        )
    
    # Récupérer la dernière donnée
    latest = await db["donnees"].find_one(
        {"capteurId": capteur_id, "owner_id": current_user["id"]},
        sort=[("timestamp", -1)]
    )
    
    if not latest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucune donnée trouvée pour ce capteur"
        )
    
    latest["id"] = str(latest.pop("_id"))
    return latest

@router.get("/alertes/all")
async def get_alertes(current_user: dict = Depends(get_current_user)):
    """
    Récupérer toutes les alertes de l'utilisateur
    """
    cursor = db["alertes"].find({"owner_id": current_user["id"]}).sort("timestamp", -1)
    
    alertes = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        alertes.append(doc)
    
    return {
        "total_alertes": len(alertes),
        "alertes": alertes
    }

@router.get("/seuils/all")
async def get_all_seuils(current_user: dict = Depends(get_current_user)):
    """
    Récupérer tous les seuils configurés par l'utilisateur
    """
    cursor = db["seuils"].find({"owner_id": current_user["id"]})
    
    seuils = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        seuils.append(doc)
    
    return {
        "total_seuils": len(seuils),
        "seuils": seuils
    }

@router.delete("/alertes/{alerte_id}")
async def delete_alerte(alerte_id: str, current_user: dict = Depends(get_current_user)):
    """
    Supprimer une alerte
    """
    from bson import ObjectId
    
    try:
        result = await db["alertes"].delete_one({
            "_id": ObjectId(alerte_id),
            "owner_id": current_user["id"]
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alerte non trouvée"
            )
        
        return {"message": "Alerte supprimée avec succès"}
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID d'alerte invalide"
        )