from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routes import auth_routes, data_routes, objets_routes
from utils.security import get_current_user
from database.mongo import db

# Configuration de l'application FastAPI
app = FastAPI(
    title="🚀 API IoT Platform",
    description="API IoT complète avec authentification JWT, gestion d'objets et données",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True}
)

# Configuration CORS pour permettre les requêtes cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers avec leurs préfixes
app.include_router(auth_routes.router, prefix="/auth", tags=["🔐 Authentification"])
app.include_router(objets_routes.router, prefix="/objets", tags=["📡 Objets IoT"])
app.include_router(data_routes.router, prefix="/data", tags=["📊 Données & Alertes"])

# Route racine - Page d'accueil de l'API
@app.get("/")
def read_root():
    return {
        "message": "✅ Bienvenue sur la plateforme IoT avec FastAPI",
        "version": "1.0.0",
        "documentation": "/docs",
        "status": "🟢 Opérationnelle"
    }

# Route pour récupérer le profil de l'utilisateur connecté
@app.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Récupérer les informations de l'utilisateur connecté
    Nécessite un token JWT valide
    """
    return {
        "user": {
            "id": current_user["id"],
            "email": current_user["email"],
            "username": current_user["username"]
        },
        "message": "✅ Utilisateur authentifié avec succès"
    }

# Route de test de la base de données
@app.get("/test-db")
async def test_database():
    """
    Tester la connexion à MongoDB et lister les collections
    """
    try:
        collections = await db.list_collection_names()
        return {
            "status": "✅ Connexion MongoDB OK",
            "database": "iot_BD",
            "collections": collections,
            "total_collections": len(collections)
        }
    except Exception as e:
        return {
            "status": "❌ Erreur de connexion MongoDB",
            "error": str(e),
            "solution": "Vérifiez que MongoDB est démarré (mongod)"
        }

# Route de santé de l'API
@app.get("/health")
async def health_check():
    """
    Vérifier l'état de santé de l'API
    """
    return {
        "status": "🟢 Healthy",
        "service": "IoT API Platform",
        "version": "1.0.0"
    }

# Point d'entrée pour le développement
if __name__ == "_main_":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )