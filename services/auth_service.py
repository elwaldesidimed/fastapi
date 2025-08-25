from passlib.context import CryptContext
from database.mongo import db
from models.schemas import UserCreate, UserModel
from bson import ObjectId
from database.mongo import db

# ✅ جلب مستخدم حسب الـ ObjectId
async def get_user_by_id(user_id: str):
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        return None  # إذا لم يكن ID صالح

    user = await db["users"].find_one({"_id": obj_id})
    if user:
        user["id"] = str(user["_id"])  # تحويل ObjectId إلى string
    return user
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔐 Hash du mot de passe
def hash_password(password: str):
    return pwd_context.hash(password)

# 🔐 Vérification du mot de passe
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# ✅ Création d’un nouvel utilisateur
async def create_user(user: UserCreate) -> UserModel:
    existing = await db["users"].find_one({"email": user.email})
    if existing:
        raise ValueError("Email déjà utilisé")

    hashed = hash_password(user.password)
    user_dict = user.model_dump()
    user_dict["password"] = hashed

    result = await db["users"].insert_one(user_dict)
    user_dict["_id"] = result.inserted_id

    return UserModel(**user_dict)

# ✅ Authentification d’un utilisateur
async def authenticate_user(email: str, password: str):
    user = await db["users"].find_one({"email": email})
    if not user:
        return None

    if not verify_password(password, user.get("password", "")):
        return None

    user["id"] = str(user["_id"])
    return user