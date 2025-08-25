from fastapi import APIRouter, Depends, HTTPException
from models.schemas import Objet
from services.objets_services import ajouter_objet, get_objets_par_utilisateur
from utils.jwt_utils import get_current_user

router = APIRouter(prefix="/objets", tags=["Objets"])

# ✅ Ajouter un objet (protégé)
@router.post("/")
async def create_objet(objet: Objet, current_user: dict = Depends(get_current_user)):
    if not objet.capteurId or not objet.type or not objet.emplacement:
        raise HTTPException(status_code=400, detail="Tous les champs de l'objet sont requis")

    objet.utilisateur = current_user["id"]

    success = await ajouter_objet(objet)
    if not success:
        raise HTTPException(status_code=500, detail="Échec de l'ajout de l'objet")

    return {"message": "Objet ajouté avec succès"}

# ✅ Obtenir les objets d’un utilisateur (protégé)
@router.get("/")
async def get_objets(current_user: dict = Depends(get_current_user)):
    objets = await get_objets_par_utilisateur(current_user["id"])
    if objets is None:
        raise HTTPException(status_code=404, detail="Aucun objet trouvé pour cet utilisateur")
    return objets