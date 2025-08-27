from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from bson import ObjectId
from database.mongo import db

# ⚙ Configuration JWT
SECRET_KEY = "votre-cle-secrete-super-longue-et-complexe-2024-iot-jwt"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ⚙ Configuration sécurité
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔐 Génération du token JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Créer un token d'accès JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 🔒 Hash du mot de passe
def hash_password(password: str) -> str:
    """Hasher le mot de passe avec bcrypt"""
    return pwd_context.hash(password)

# ✅ Vérifier le mot de passe
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifier si le mot de passe correspond au hash"""
    return pwd_context.verify(plain_password, hashed_password)

# 👤 Récupérer l'utilisateur actuel depuis le token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Récupérer l'utilisateur connecté depuis le token JWT
    Cette fonction sera utilisée avec Depends() dans vos routes protégées
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Décoder le token JWT
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Récupérer l'utilisateur depuis MongoDB
    try:
        user = await db["users"].find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise credentials_exception
        
        # Convertir ObjectId en string pour les réponses JSON
        user["id"] = str(user["_id"])
        return user
    except Exception:
        raise credentials_exception