from fastapi import APIRouter, HTTPException,  Depends
from typing import List
from database.mongo import db
from models.schemas import Donnee, Seuil, Alerte, UserModel
from utils.jwt_utils import get_current_user

router = APIRouter(prefix="/data", tags=["Données"])

# ✅ 1. Enregistrer une donnée (avec alerte si dépasse seuil)
@router.post("/", response_model=dict)
async def save_data(
    payload: Donnee,
    current_user: UserModel = Depends(get_current_user)
):
    # Vérifier si la donnée existe déjà
    existing = await db["donnees"].find_one({
        "capteurId": payload.capteurId,
        "timestamp": payload.timestamp
    })
    if existing:
        raise HTTPException(status_code=400, detail="⚠ Donnée déjà enregistrée")

    data_dict = payload.model_dump()
    data_dict["owner_email"] = current_user.email

    # Enregistrer la donnée
    await db["donnees"].insert_one(data_dict)

    # Vérifier seuil
    seuil_doc = await db["seuils"].find_one({"capteurId": payload.capteurId})
    if seuil_doc:
        seuil_max = seuil_doc.get("seuil_max")
        if payload.valeur > seuil_max:
            alerte = Alerte(
                capteurId=payload.capteurId,
                valeur=payload.valeur,
                message=f"Valeur {payload.valeur} dépasse le seuil ({seuil_max})",
                timestamp=payload.timestamp
            )
            await db["alertes"].insert_one(alerte.model_dump())

    return {"status": "✅ Donnée enregistrée avec succès"}

# ✅ 2. Définir un seuil
@router.post("/seuil", response_model=dict)
async def set_seuil(
    payload: Seuil,
    current_user: UserModel = Depends(get_current_user)
):
    await db["seuils"].update_one(
        {"capteurId": payload.capteurId},
        {"$set": payload.model_dump()},
        upsert=True
    )
    return {"status": "✅ Seuil mis à jour"}

# ✅ 3. Obtenir les données d’un capteur
@router.get("/{capteur_id}", response_model=List[dict])
async def get_data(
    capteur_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    cursor = db["donnees"].find({
        "capteurId": capteur_id,
        "owner_email": current_user.email
    })
    data = []
    async for doc in cursor:
        doc.pop("_id", None)
        data.append(doc)
    return data

# ✅ 4. Obtenir toutes les alertes
@router.get("/alertes", response_model=List[dict])
async def get_alertes(
    current_user: UserModel = Depends(get_current_user)
):
    cursor = db["alertes"].find()
    alertes = []
    async for doc in cursor:
        doc.pop("_id", None)
        alertes.append(doc)
    return alertes