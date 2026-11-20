from flask import Blueprint, g, request
from .auth_utils import require_auth
from .models import DeliveryOrder
from .extensions import db

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

@orders_bp.post('/orders')
@require_auth
def create_delivery_order():
    data = request.get_json()
    if not data:
        return {'code': 'INVALID_JSON'}, 400
    restaurant_name = data.get('restaurant_name')
    total_price = data.get('total_price')
    reference_number = data.get('reference_number')
    if not restaurant_name or not total_price or not reference_number:
        return {'code': 'VALIDATION_ERROR'}, 400
    delivery_order = DeliveryOrder(
        user_id=g.current_user_id,
        restaurant_name=restaurant_name,
        total_price=total_price,
        reference_number=reference_number
    )
    db.session.add(delivery_order)
    db.session.commit()
    response = {
        'id': delivery_order.id,
        'user_id': delivery_order.user_id,
        'restaurant_name': delivery_order.restaurant_name,
        'total_price': delivery_order.total_price,
        'reference_number': delivery_order.reference_number
    }
    
    return {'message': 'Delivery order created successfully', 'data': response}, 201

@orders_bp.get('/orders')
@require_auth
def get_delivery_orders():
    orders = DeliveryOrder.query.filter_by(user_id=g.current_user_id).all()
    orders_list = []
    for order in orders:
        orders_list.append({
            'id': order.id,
            'restaurant_name': order.restaurant_name,
            'total_price': order.total_price,
            'reference_number': order.reference_number
        })
    return {'data': orders_list}, 200

@orders_bp.get('/orders/<int:order_id>')
@require_auth
def get_delivery_order(order_id):
    order = DeliveryOrder.query.get(order_id)
    if not order:
        return {"code": "NOT_FOUND", "message": "Delivery order not found"}, 404
    response = {
        'id': order.id,
        'restaurant_name': order.restaurant_name,
        'total_price': order.total_price,
        'reference_number': order.reference_number
    }
    return {'data': response}, 200



