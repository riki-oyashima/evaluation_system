import json
from pathlib import Path

from ev_sys_pwa.app.utils.database.data_class import DatastoreKind, User, Project,\
    EvItemRole, EvItemSection, EvItemElement, EvItemInputNumber, EvItemUser, Authority


def get_func(class_, key, value, new_instance=False):
    instance = class_().get_obj(key, value)
    if not instance and new_instance:
        instance = class_()
    return instance


def create_user(username, password, authority):
    user = get_func(User, "username", username, new_instance=True)
    user.set_parameters(username=username, password=password, status=1, authority=authority)
    user.save()


def create_project(name):
    project = get_func(Project, "disp_name", name, new_instance=True)
    project.set_parameters(display=name)
    project.save()


def create_initial_evaluation_items():
    parent = Path(__file__).resolve().parent
    filepath = parent.joinpath("data/initial_evaluation_items.json")
    with open(filepath, 'r') as f:
        json_data = json.load(f)
        for role_data in json_data:
            role = get_func(EvItemRole, "display", role_data.get("display"))
            if not role:
                role = EvItemRole()
                role.set_parameters(display=role_data.get("display"), description=role_data.get("description"))
                role.save()
                role = role.get_obj("disp_name", role_data.get("display"))
            for section_data in role_data.get("sections", []):
                section = get_func(EvItemSection, "disp_name", section_data.get("display"))
                if not section:
                    section = EvItemSection()
                    section.set_parameters(display=section_data.get("display"))
                    section.save()
                    section = section.get_obj("disp_name", section_data.get("display"))
                for element_data in section_data.get("elements"):
                    element = get_func(EvItemElement, "description", element_data)
                    if not element:
                        element = EvItemElement()
                        element.set_parameters(description=element_data,
                                               role=role.key,
                                               section=section.key)
                        element.save()


def delete_all_evaluation_items():
    client = EvItemRole().get_client()
    for kind in [
        DatastoreKind.item_element.value,
        DatastoreKind.item_section.value,
        DatastoreKind.item_role.value,
    ]:
        query = client.query(kind=kind)
        for data in query.fetch():
            client.delete(data.key)


def get_all_roles():
    query = EvItemRole().get_client().query(kind=DatastoreKind.item_role.value)
    res = {}
    for data in query.fetch():
        res[data.key] = {x: y for x, y in data.items()}
    return res


def get_all_sections():
    query = EvItemSection().get_client().query(kind=DatastoreKind.item_section.value)
    res = {}
    for data in query.fetch():
        res[data.key] = {x: y for x, y in data.items()}
    return res


def get_all_evaluation_elements():
    roles = get_all_roles()
    sections = get_all_sections()
    query = EvItemElement().get_client().query(kind=DatastoreKind.item_element.value)
    res = {}
    for data in query.fetch():
        data_dict = {"key": data.key}
        for key, value in data.items():
            if key == "role":
                data_dict[key] = roles.get(value)
            elif key == "section":
                data_dict[key] = sections.get(value)
            else:
                data_dict[key] = value
        res[data.key.id] = data_dict
    return res


def get_input_number(username, number=-1):
    res = None
    user = get_func(User, "username", username)
    if not user:
        return res
    filters = [
        ("user", "=", user.key),
    ]
    if number >= 0:
        filters.append(("number", "=", number))
    query = EvItemInputNumber().get_client().query(kind=DatastoreKind.item_input_number.value, filters=filters)
    for data in query.fetch():
        value = dict(data.items()).get("number", 0)
        if res is None or value > dict(res.items()).get("number", 0):
            res = data
    return EvItemInputNumber(res.key, **dict(res.items())) if res else None


def get_all_input_numbers(username):
    res = []
    user = get_func(User, "username", username)
    if not user:
        return res
    filters = [
        ("user", "=", user.key),
    ]
    query = EvItemInputNumber().get_client().query(kind=DatastoreKind.item_input_number.value, filters=filters)
    for data in query.fetch():
        res.append(dict(data.items()).get("number", 0))
    return res


def get_evaluation_results(username, input_number=None):
    res = get_all_evaluation_elements()
    if input_number is None:
        input_number = get_input_number(username)
    if input_number:
        filters = [
            ("input_number", "=", input_number.key),
        ]
        query = EvItemUser().get_client().query(kind=DatastoreKind.item_user.value, filters=filters)
        for data in query.fetch():
            item_user = dict(data.items())
            if item_user.get("element").id in res:
                res.get(item_user.get("element").id).update({"evaluation": item_user.get("evaluation")})
    return res


def create_input_number(user, number):
    input_number = EvItemInputNumber()
    input_number.set_parameters(user=user.key, number=number)
    input_number.save()

    filters = [
        ("user", "=", user.key),
        ("number", "=", number),
    ]
    query = EvItemInputNumber().get_client().query(kind=DatastoreKind.item_input_number.value, filters=filters)
    data = None
    for data in query.fetch():
        break
    return EvItemInputNumber(data.key, **dict(data.items()))


def create_ev_item_user(input_number, element_key, evaluation):
    ev_item_user = EvItemUser()
    ev_item_user.set_parameters(input_number=input_number.key, element=element_key, evaluation=evaluation)
    ev_item_user.save()


def get_user(username):
    return get_func(User, "username", username)


def get_members():
    query = User().get_client().query(kind=DatastoreKind.user.value)
    query.add_filter("authority", "=", 30)
    return [User(x.key, **dict(x.items())) for x in query.fetch()]
