from flask import Blueprint
from .auth_utils import require_auth

orders_bp = Blueprint('orders', __name__)

@orders_bp.get('/health')
@require_auth
def health_check():
    return {'status': 'healthy'}