"""Verify we can reach the MongoDB server. Run this first.

    python scripts/ping.py
"""
from db import MONGODB_URI, get_client
from pymongo.errors import ServerSelectionTimeoutError


def main() -> None:
    client = get_client()
    try:
        info = client.admin.command("ping")
        version = client.server_info()["version"]
        print(f"Connected to {MONGODB_URI}")
        print(f"MongoDB server version: {version}")
        print(f"Databases: {client.list_database_names()}")
        print(f"ping -> {info}")
    except ServerSelectionTimeoutError as e:
        print(f"Could NOT reach a MongoDB server at {MONGODB_URI}")
        print("Compass is only a GUI -- it needs a running server. Is the")
        print("container up? Check with `docker ps`, and if not:")
        print("  colima start                    # if the VM isn't running")
        print("  docker start mongo-playground")
        print(f"Details:\n  {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
