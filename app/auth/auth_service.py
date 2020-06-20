from app.common import get_user, DbContext, SECRET_KEY
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user
from .user import User
import jwt


def sign_in(phone, password):
    user = get_user(phone)

    if user is None:
        return 1

    if not check_password_hash(user[10], password):
        return 2

    user_model = User(user[0], user[9])
    login_user(user_model)

    return user_model


def sign_up(data):
    try:
        auth_token_payload = jwt.decode(data['auth_token'].encode('utf-8'), SECRET_KEY, algorithms=['HS256'])
    except Exception as e:
        print(e)
        return 2

    if get_user(auth_token_payload['phone']) is not None:
        return 1

    context = DbContext()

    password_hash = generate_password_hash(data['employee_password'])
    query = "INSERT INTO employee VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    context.update(
        query,
        [
            data['employee_full_name'],
            data['employee_itn'],
            data['employee_passport'],
            data['employee_address'],
            auth_token_payload['phone'],
            data['employee_sex'],
            data['employee_birthdate'],
            data['employee_salary'],
            auth_token_payload['position'],
            password_hash
        ]
    )

    del context
    return 0
