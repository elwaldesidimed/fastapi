from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# مفتاح سري لتوقيع التوكن (غيره في مشروعك الحقيقي!)
SECRET_KEY = "secret-key-jwt-1234567890"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# نقطة النهاية الخاصة بتسجيل الدخول
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# بيانات المستخدم داخل التوكن
class TokenData(BaseModel):
    email: Optional[str] = None

# 🔐 توليد توكن
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ✅ تحقق من صحة التوكن
def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return TokenData(email=email)
    except JWTError:
        raise credentials_exception

# 🔒 الحصول على المستخدم من التوكن (لحماية المسارات)
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de vérifier les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de vérifier les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)