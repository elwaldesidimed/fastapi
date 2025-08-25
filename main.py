from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from routes import auth_routes, data_routes, objets_routes
from utils.security import get_current_user
from database import mongo

app = FastAPI(
    title="API IoT",
    description="API مع توثيق JWT",
    version="1.0",
    swagger_ui_parameters={"persistAuthorization": True}
)

# MongoDB
MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client["iot_BD"]
mongo.db = db

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Routers
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentification"])
app.include_router(objets_routes.router, prefix="/objets", tags=["Objets"])
app.include_router(data_routes.router, prefix="/data", tags=["Données"])

@app.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}

# Route de test
@app.get("/")
def read_root():
    return {"message": "✅ Bienvenue sur la plateforme IoT avec FastAPI"}

@app.get("/test-db")
async def test_b():
    collections = await db.list_collection_names()
    return {"collections": collections}