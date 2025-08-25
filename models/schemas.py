# models/schemas.py
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from typing import Any

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate, core_schema.str_schema()
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return str(ObjectId(v))
        raise ValueError("Invalid ObjectId")



class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    username: Optional[str] = None  

# ✅ نموذج تسجيل الدخول
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ✅ نموذج المستخدم كما في قاعدة البيانات
class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    username: str
    email: EmailStr

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


# ✅ نموذج المستخدم مع كلمة مرور مشفرة
class UserInDB(UserModel):
    hashed_password: str


# ✅ نموذج الكائن (Objet)
class Objet(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    nom: str
    type: str
    utilisateur_id: str

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


# ✅ نموذج البيانات (Donnée)
class Donnee(BaseModel):
    capteurId: str
    valeur: float
    timestamp: str


# ✅ نموذج العتبة (Seuil)
class Seuil(BaseModel):
    capteurId: str
    seuil_max: float


# ✅ نموذج التنبيه (Alerte)
class Alerte(BaseModel):
    capteurId: str
    valeur: float
    message: str
    timestamp: str