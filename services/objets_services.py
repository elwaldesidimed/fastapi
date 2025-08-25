from fastapi import HTTPException
from models.schemas import Objet
from database.mongo import db

# ➕ Ajouter un capteur
async def ajouter_objet(objet: Objet):
    existe = await db["objets"].find_one({"capteurId": objet.capteurId})
    if existe:
        raise HTTPException(status_code=400, detail="⚠ Capteur déjà enregistré")
    
    await db["objets"].insert_one(objet.model_dump())
    return {"status": "✅ Capteur enregistré avec succès"}

# 📥 Voir tous les capteurs d’un utilisateur
async def get_objets_par_utilisateur(utilisateur: str):
    cursor = db["objets"].find({"utilisateur": utilisateur})
    objets = []
    async for obj in cursor:
        obj.pop("_id", None)
        objets.append(obj)
    return objets