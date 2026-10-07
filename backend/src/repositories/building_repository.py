from src.db import db
class BuildingRepository:
    def find_all(self):
        return db["building"]
