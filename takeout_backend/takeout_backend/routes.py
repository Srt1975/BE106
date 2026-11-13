from flask import Blueprint

orders_bp = Blueprint('orders', __name__)

@orders_bp.get('/health')
def health_check():
    return {'status': 'healthy'}