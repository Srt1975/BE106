from flask import Blueprint, g
from .auth_utils import require_auth

orders_bp = Blueprint('orders', __name__)

@orders_bp.get('/health')
@require_auth
def health_check():
    return {'status': 'healthy'}

@orders_bp.get('/admin/health')
@require_auth
def admin_health_check():
    if g.current_user_role != 'admin':
        return {'error': 'Unauthorized'}, 403
    return {'status': 'admin healthy'}