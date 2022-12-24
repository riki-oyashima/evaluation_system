import hashlib
from enum import Enum

import pytz
from flask_login import UserMixin
from datastore_entity import DatastoreEntity, EntityValue
from datetime import datetime


class DatastoreKind(Enum):
    user = "ev_sys_user"
    project = "project"
    item_role = "ev_sys_evaluation_items_role"
    item_section = "ev_sys_evaluation_items_section"
    item_element = "ev_sys_evaluation_items_element"
    item_input_number = "ev_sys_evaluation_items_input_number"
    item_user = "ev_sys_evaluation_items_user"
    target_item = "ev_sys_evaluation_target_item"


class UserStatus(Enum):
    Active = 1
    Inactive = 0


class Authority(Enum):
    Administrator = 0
    Manager = 10
    Viewer = 20
    Member = 30


class EvaluationNumber(Enum):
    bad = 0
    good = 1
    great = 2


class InputNumberStep(Enum):
    init = 0
    user_input = 1
    manager_input = 2
    fixed = 3


class User(DatastoreEntity, UserMixin):
    __kind__ = DatastoreKind.user.value
    username = EntityValue(None)
    password = EntityValue(None)
    password_raw = EntityValue(None)
    status = EntityValue(UserStatus.Active.value)
    authority = EntityValue(Authority.Member.value)
    projects = EntityValue([])

    def __init__(self, key=None, **kwargs):
        super().__init__(**kwargs)
        if key:
            self.key = key
            self.username = kwargs.get("username")
            self.password = kwargs.get("password")
            self.password_raw = kwargs.get("password_raw")
            self.status = kwargs.get("status")
            self.authority = kwargs.get("authority")
            self.projects = kwargs.get("projects")

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
    __kind__ = DatastoreKind.project.value
    disp_name = EntityValue(None)

    def set_parameters(self, **kwargs):
        self.disp_name = kwargs.get("display")


class EvItemRole(DatastoreEntity):
    __kind__ = DatastoreKind.item_role.value
    disp_name = EntityValue(None)
    description = EntityValue(None)

    def set_parameters(self, **kwargs):
        self.disp_name = kwargs.get("display")
        self.description = kwargs.get("description")


class EvItemSection(DatastoreEntity):
    __kind__ = DatastoreKind.item_section.value
    disp_name = EntityValue(None)

    def set_parameters(self, **kwargs):
        self.disp_name = kwargs.get("display")


class EvItemElement(DatastoreEntity):
    __kind__ = DatastoreKind.item_element.value
    description = EntityValue(None)
    role = EntityValue(None)
    section = EntityValue(None)

    def set_parameters(self, **kwargs):
        self.description = kwargs.get("description")
        self.role = kwargs.get("role")
        self.section = kwargs.get("section")


class EvItemInputNumber(DatastoreEntity):
    __kind__ = DatastoreKind.item_input_number.value
    user = EntityValue(None)
    number = EntityValue(0)
    date = EntityValue(None)

    def __init__(self, key=None, **kwargs):
        super().__init__(**kwargs)
        if key:
            self.key = key
            self.user = kwargs.get("user")
            self.number = kwargs.get("number")
            self.date = kwargs.get("date")

    def set_parameters(self, **kwargs):
        self.user = kwargs.get("user", self.user)
        self.number = kwargs.get("number", self.number)
        self.date = kwargs.get("date", datetime.now(pytz.utc))


class EvItemUser(DatastoreEntity):
    __kind__ = DatastoreKind.item_user.value
    input_number = EntityValue(None)
    element = EntityValue(None)
    evaluation = EntityValue(EvaluationNumber.bad.value)

    def set_parameters(self, **kwargs):
        self.input_number = kwargs.get("input_number", self.input_number)
        self.element = kwargs.get("element", self.element)
        self.evaluation = kwargs.get("evaluation", self.evaluation)


class EvTargetItem(DatastoreEntity):
    __kind__ = DatastoreKind.target_item.value
    input_number = EntityValue(None)
    element = EntityValue(None)
    detail = EntityValue(None)

    def __init__(self, key=None, **kwargs):
        super().__init__(**kwargs)
        if key:
            self.key = key
            self.input_number = kwargs.get("input_number")
            self.element = kwargs.get("element")
            self.detail = kwargs.get("detail")

    def set_parameters(self, **kwargs):
        self.input_number = kwargs.get("input_number", self.input_number)
        self.element = kwargs.get("element", self.element)
        self.detail = kwargs.get("detail", self.detail)
