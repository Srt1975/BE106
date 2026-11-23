from .extensions import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    role = db.Column(db.String(20), nullable=False, default='user')
    delivery_orders = db.relationship('DeliveryOrder',back_populates='user', lazy=True)


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
    user = db.relationship('User', back_populates='delivery_orders', lazy=True)

    def __repr__(self):
        return f"<DeliveryOrder {self.reference_number} for User {self.user_id}>"