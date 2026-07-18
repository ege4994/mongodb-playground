"""Shared MongoDB connection helper.

Set MONGODB_URI in your environment to override the default. Compass shows
you this exact string at the top of its connection screen, e.g.:
    mongodb://localhost:27017
"""
import os

from pymongo import MongoClient
from pymongo.database import Database

# Default to a local server on the standard port. Override with:
#   export MONGODB_URI="mongodb://localhost:27017"
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")

# The database we'll experiment in. It's created lazily on first write.
DB_NAME = os.environ.get("MONGODB_DB", "playground")


def get_client() -> MongoClient:
    # serverSelectionTimeoutMS keeps us from hanging for 30s when no server
    # is running -- we fail fast with a clear error instead.
    return MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)


def get_db() -> Database:
    return get_client()[DB_NAME]
