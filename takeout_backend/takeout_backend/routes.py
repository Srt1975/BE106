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
        return {
            "code": "FORBIDDEN",
            "message": "You do not have permission to access this resource."
            }, 403
    return {'status': 'admin healthy'}

@orders_bp.post('/orders')
@require_auth
def create_delivery_order():
    data = request.get_json()
    if not data:
        return {'code': 'VALIDATION_ERROR',
                'message': 'There were validation errors',
                'fields': {
                    "restaurant_name": "Restaurant name is required.",
                    "total_price": "Total price is required.",
                    "reference_number": "Reference number is required."
                }}, 400
    
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
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=4, type=int)
    
    if per_page is None or per_page < 1 or per_page > 15:
        return {
            "code": "VALIDATION_ERROR",
            "message": "There were validation errors.",
            "fields": {
                "per_page": "Must be between 1 and 15."
            }
        }, 400
    
    if page is None or page < 1:
        return {
            "code": "VALIDATION_ERROR",
            "message": "There were validation errors.",
            "fields": {
                "page": "Must be greater than 0."
            }
        }, 400


    orders_query = DeliveryOrder.query.filter_by(user_id=g.current_user_id).order_by(DeliveryOrder.id)
    paginated_orders = orders_query.paginate(page=page, per_page=per_page, error_out=False)
    orders_list = []
    for order in paginated_orders.items:
        orders_list.append({
            'id': order.id,
            'restaurant_name': order.restaurant_name,
            'total_price': order.total_price,
            'reference_number': order.reference_number
        })
    response = {
        'pages': paginated_orders.pages,
        'data': orders_list,
        'page': paginated_orders.page,
        'per_page': paginated_orders.per_page,
        'total': paginated_orders.total
    }
    return response, 200

@orders_bp.get('/orders/<int:order_id>')
@require_auth
def get_delivery_order(order_id):
    order = DeliveryOrder.query.get(order_id)
    if not order:
        return {"code": "NOT_FOUND", "message": "Delivery order not found"}, 404
    if order.user_id != g.current_user_id:
        return {"code": "NOT_FOUND", "message": "Delivery order not found"}, 404
    response = {
        'id': order.id,
        'restaurant_name': order.restaurant_name,
        'total_price': order.total_price,
        'reference_number': order.reference_number
    }
    return {'data': response}, 200

@orders_bp.patch('/orders/<int:order_id>')
@require_auth
def update_delivery_order(order_id):
    order = DeliveryOrder.query.get(order_id)
    if not order:
        return {"code": "NOT_FOUND", "message": "Delivery order not found"}, 404
    data = request.get_json(silent=True)
    if data is None:
        return {"code": "INVALID_JSON", "message": "Invalid JSON body"}, 400
    if order.user_id != g.current_user_id:
        return {"code": "NOT_FOUND", "message": "Delivery order not found"}, 404
    restaurant_name = data.get('restaurant_name')
    total_price = data.get('total_price')
    reference_number = data.get('reference_number')
    if restaurant_name:
        order.restaurant_name = restaurant_name
    if total_price:
        order.total_price = total_price
    if reference_number:
        order.reference_number = reference_number
    db.session.commit()
    response = {
        'id': order.id,
        'restaurant_name': order.restaurant_name,
        'total_price': order.total_price,
        'reference_number': order.reference_number
    }
    return {'message': 'Delivery order updated successfully', 'data': response}, 200

@orders_bp.delete('/orders/<int:order_id>')
@require_auth
def delete_delivery_order(order_id):
    order = DeliveryOrder.query.get(order_id)
    if not order:
        return {"code": "NOT_FOUND", "message": "Delivery order not found"}, 404
    if order.user_id != g.current_user_id:
        return {"code": "NOT_FOUND", "message": "Delivery order not found"}, 404
    db.session.delete(order)
    db.session.commit()
    return {'message': 'Delivery order deleted successfully'}, 200

