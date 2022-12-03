from ev_sys_pwa.app.utils.database.data_class import User


def get_user(username):
    return User().get_obj("username", username)


def create_user(username, password, authority):
    user = get_user(username)
    if user is None:
        user = User()
    user.set_parameters(username=username, password=password, status=1, authority=authority)
    user.save()
