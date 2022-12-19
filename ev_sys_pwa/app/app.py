from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta
from functools import wraps

from ev_sys_pwa.app.utils.database.utils import get_func, get_evaluation_results, get_all_evaluation_elements, \
    get_input_number, get_user, create_input_number, create_ev_item_user, get_members, get_all_input_numbers
from ev_sys_pwa.app.utils.database.data_class import User, EvaluationNumber, InputNumberStep, Authority
from ev_sys_pwa.app.settings.const import Message

app = Flask(__name__)

app.secret_key = 'abcdefghijklmn'
app.permanent_session_lifetime = timedelta(minutes=60)


def session_check(func):
    @wraps(func)
    def wrapper():
        if "id" in session:
            return func()
        return render_template("index.html")
    return wrapper


@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        id_ = request.form.get("id")
        password = request.form.get('pass')

        user = get_func(User, "username", id_)
        if user and user.authenticated(password):
            session["id"] = user.username
            return redirect(url_for("login_"))
        else:
            return render_template("index.html")
    else:
        if "id" in session:
            return redirect(url_for("login_"))
        return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
@session_check
def login_():
    user = get_user(session["id"])
    if user.authority in [
        Authority.Administrator.value,
        Authority.Manager.value,
        Authority.Viewer.value,
    ]:
        return render_template("member_list.html",
                               id=session["id"],
                               members=[x.username for x in get_members()]
                               )

    if user.authority in [Authority.Member.value]:
        return redirect(url_for("current_evaluations"))


@app.route("/current_evaluations", methods=["GET"])
@session_check
def current_evaluations():
    user = get_user(session["id"])
    if user.authority <= Authority.Viewer.value:
        target_member = request.args.get('target_member')
    else:
        target_member = session["id"]

    if not target_member:
        return redirect(url_for("login_"))

    latest_input_number = get_input_number(target_member)

    if latest_input_number:
        input_number = latest_input_number
        if latest_input_number.number in [
            InputNumberStep.user_input.value,
            InputNumberStep.manager_input.value,
        ]:
            all_numbers = set(get_all_input_numbers(target_member))
            if user.authority == Authority.Manager.value:
                if not all_numbers & {InputNumberStep.manager_input.value}:
                    input_number = get_input_number(target_member, InputNumberStep.init.value)
            elif user.authority == Authority.Member.value:
                if not all_numbers & {InputNumberStep.user_input.value}:
                    input_number = get_input_number(target_member, InputNumberStep.init.value)
            else:
                input_number = get_input_number(target_member, InputNumberStep.init.value)
    else:
        input_number = create_input_number(get_user(target_member), 0)

    evaluation_results = get_evaluation_results(target_member, input_number)
    ev_results_dict = {}
    role_descriptions = {}
    for key, data in evaluation_results.items():
        role_name = data.get("role", {}).get("disp_name")
        if role_name and role_name not in role_descriptions:
            role_descriptions[role_name] = data.get("role", {}).get("description")
        ev_results_dict.setdefault(role_name, {}).setdefault(
            data.get("section", {}).get("disp_name"), {}).update(
            {
                key: {
                    "description": data.get("description"),
                    "evaluation": data.get("evaluation", EvaluationNumber.bad.value)
                }
            })

    message_args = {
        "target_member": target_member,
    }
    message = Message().get_message(user.authority, input_number.number, **message_args)
    editable = False
    if user.authority == Authority.Member.value:
        if input_number.number == InputNumberStep.init.value:
            editable = True
    elif user.authority == Authority.Manager.value:
        editable = True

    return render_template("current_evaluations.html",
                           id=session["id"],
                           target_member=target_member,
                           evaluations=ev_results_dict,
                           input_number=input_number.number,
                           role_descriptions=role_descriptions,
                           editable=editable,
                           message=message,
                           )


@app.route("/update", methods=["POST"])
@session_check
def update():
    target_member = request.form.get("target_member")

    latest_number = get_input_number(target_member)
    target_user = get_user(target_member)
    if target_member != session["id"]:
        user = get_user(session["id"])
        if not user.authority == Authority.Manager.value:
            return redirect(url_for("login_"))
    if latest_number.number <= InputNumberStep.manager_input.value:
        eval_elements = get_all_evaluation_elements()
        step = InputNumberStep.user_input if target_member == session["id"] else InputNumberStep.manager_input
        input_number = create_input_number(target_user, step.value)
        for form_key in request.form:
            if form_key.startswith("eval-"):
                element_id = int(form_key.replace("eval-", ""))
                element_key = dict(eval_elements.get(element_id, {})).get("key")
                evaluation = int(request.form.get(form_key))
                if element_key:
                    create_ev_item_user(input_number=input_number,
                                        element_key=element_key,
                                        evaluation=evaluation)
    return redirect(url_for("login_"))


@app.route("/logout", methods=["GET"])
@session_check
def logout():
    session.pop('id', None)
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

