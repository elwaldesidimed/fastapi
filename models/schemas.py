from typing import Optional
from pydantic import BaseModel, Field, EmailStr

# ✅ Modèle pour créer un utilisateur (inscription)
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    username: str

# ✅ Modèle pour connexion utilisateur
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ✅ Modèle de réponse utilisateur (sans mot de passe)
class UserResponse(BaseModel):
    id: str
    email: str
    username: str

# ✅ Modèle d'objet IoT
class Objet(BaseModel):
    nom: str
    type: str
    emplacement: str
    capteurId: str
    utilisateur: Optional[str] = None

# ✅ Modèle de données de capteur
class Donnee(BaseModel):
    capteurId: str
    valeur: float
    timestamp: str

# ✅ Modèle de seuil d'alerte
class Seuil(BaseModel):
    capteurId: str
    seuil_max: float

# ✅ Modèle d'alerte
class Alerte(BaseModel):
    capteurId: str
    valeur: float
    message: str
    timestamp: str