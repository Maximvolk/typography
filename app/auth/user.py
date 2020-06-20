from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user_id, user_position):
        self.id = user_id
        # self.employee_full_name = user['employee_full_name']
        self.position = user_position
