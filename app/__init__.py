from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
login = LoginManager(app)
app.secret_key = 'you-will-never-guess'

from .auth import auth
app.register_blueprint(auth)

from .admin import admin
app.register_blueprint(admin, url_prefix='/admin')

from .editor import editor
app.register_blueprint(editor, url_prefix='/editor')

from .manager import manager
app.register_blueprint(manager, url_prefix='/manager')

from .orders_manager import orders_manager
app.register_blueprint(orders_manager, url_prefix='/ordersManager')
