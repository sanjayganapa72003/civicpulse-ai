import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

client = MongoClient(MONGODB_URI)

db = client[MONGODB_DATABASE]

demographics_collection = db["demographics"]
citizen_requests_collection = db["citizen_requests"]