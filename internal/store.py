from pymongo import MongoClient
from bson import ObjectId

class Task:
    def __init__(
            self, title, description, linksCompany, 
            linksInternet, helpers, answers, check):
        self.title = title
        self.description = description
        self.linksCompany = linksCompany
        self.linksInternet = linksInternet
        self.helpers = helpers
        self.answers = answers
        self.check = check

class Role:
    def __init__(
            self, title, about, skills: dict, task: Task):
        self.title = title
        self.about = about
        self.skills = skills
        self.task = task


class Store:
    """
    Движок БД
    """
    admins = []
    def __init__(self, connection):
        self.store = MongoClient(connection)["store"]
        self.refresh_admins()

    def get_user(self, uuid, admin=False, force=True):
        """
        Получить пользователя по айди тг
        admin - сделать админом
        force - если нет, то создать
        """
        user = self.store.users.find_one({"uuid": uuid})
        if not user and force:
            data = self.store.users.insert_one({"uuid": uuid, "access": False, "admin": admin, "name": ""})
            user = self.store.users.find_one({"_id": data.inserted_id})
        return user
    def get_user_by_id(self, _id):
        """
        Получить пользователя по айди БД
        """
        return self.store.users.find_one({"_id": ObjectId(_id)})
        
    def get_users(self, with_admins=False):
        return [user for user in self.store.users.find({"admin": with_admins})]

    def refresh_admins(self):
        self.admins = [user["uuid"] for user in self.store.users.find({"admin": True})]

    def update_user(self, user):
        self.store.users.update_one(
            {"uuid": user["uuid"]},
            {"$set": {
                "name": user["name"],
                "about": user["about"],
                }
            },
            upsert=True
        )

    def access(self, uuid, access=True):
        """Дать/Забрать доступ по айди тг"""
        self.store.users.update_one({"uuid": uuid},{"$set": {"access": access}})

    def get_roles(self):
        roles = []
        for r in self.store.roles.find({},{"_id": 1, "title": 1, "about": 1, "skills": 1}):
            roles.append(r)
        return roles

    def get_role_by_id(self, _id):
        return self.store.roles.find_one({"_id": _id})
        
    def create_role(self, role: Role):
        role = self.store.roles.find_one({"title": role.title})
        if role:
            return
        self.store.roles.insert_one(role.__dict__)