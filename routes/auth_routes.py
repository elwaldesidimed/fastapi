from fastapi import APIRouter, HTTPException, status
from database.mongo import db
from models.schemas import UserCreate, UserLogin
from utils.security import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register")
async def register(user: UserCreate):
    """
    Inscription d'un nouvel utilisateur
    """
    # Vérifier si l'email existe déjà
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email déjà utilisé"
        )
    
    # Créer l'utilisateur avec mot de passe hashé
    user_dict = user.model_dump()
    user_dict["password"] = hash_password(user.password)
    
    # Insérer dans MongoDB
    result = await db["users"].insert_one(user_dict)
    
    return {
        "message": "Utilisateur créé avec succès",
        "user_id": str(result.inserted_id),
        "email": user.email
    }

@router.post("/login")
async def login(user_credentials: UserLogin):
    """
    Connexion utilisateur - retourne un token JWT
    """
    # Chercher l'utilisateur par email
    user = await db["users"].find_one({"email": user_credentials.email})
    
    # Vérifier email et mot de passe
    if not user or not verify_password(user_credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    
    # Créer le token JWT avec l'ID utilisateur
    access_token = create_access_token(data={"sub": str(user["_id"])})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"]
        }
    }