from .extensions import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    role = db.Column(db.String(20), nullable=False, default='user')


    def __repr__(self):
        return f"<User {self.email}>"
    
class DeliveryOrder(db.Model): 
    __tablename__ = "delivery_orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_name = db.Column(db.String(120), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    special_instructions = db.Column(db.Text, nullable=True)
    reference_number = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<DeliveryOrder {self.reference_number} for User {self.user_id}>"