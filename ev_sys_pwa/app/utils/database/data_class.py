import hashlib
from enum import Enum
from flask_login import UserMixin
from datastore_entity import DatastoreEntity, EntityValue


class UserStatus(Enum):
    Active = 1
    Inactive = 0


class Authority(Enum):
    Administrator = 0
    Manager = 10
    Viewer = 20
    Member = 30


class User(DatastoreEntity, UserMixin):
    __kind__ = "ev_sys_user"
    username = EntityValue(None)
    password = EntityValue(None)
    password_raw = EntityValue(None)
    status = EntityValue(UserStatus.Active.value)
    authority = EntityValue(Authority.Member.value)
    projects = EntityValue([])

    def set_parameters(self, **kwargs):
        self.username = kwargs.get("username", self.username)
        password = kwargs.get("password")
        if password:
            self.password = hashlib.md5(password.encode()).hexdigest()
            self.password_raw = password
        self.status = kwargs.get("status", self.status)
        self.authority = kwargs.get("authority", self.authority)
        self.projects = kwargs.get("projects", self.projects)

    def authenticated(self, password):
        hashed_pass = hashlib.md5(password.encode()).hexdigest()
        return True if hashed_pass == self.password else False


class Project(DatastoreEntity):
    __kind__ = "ev_sys_project"
    id = EntityValue("id")
    name = EntityValue("name")
