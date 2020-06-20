from flask import Blueprint

orders_manager = Blueprint('orders_manager', __name__)

from . import routes
