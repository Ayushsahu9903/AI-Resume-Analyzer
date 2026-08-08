import os
import motor.motor_asyncio

MONGO_DETAILS = os.getenv(
    "MONGODB_URL",
    "mongodb://localhost:27017"
)

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client["matchingdb"]
