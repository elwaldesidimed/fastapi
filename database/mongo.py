from motor.motor_asyncio import AsyncIOMotorClient

# رابط الاتصال بقاعدة بيانات MongoDB
MONGO_URL = "mongodb://localhost:27017"

# إنشاء عميل MongoDB
client = AsyncIOMotorClient(MONGO_URL)

# اختيار قاعدة البيانات التي سنعمل عليها
db = client["iot_BD"]