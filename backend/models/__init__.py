from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .food import Food
from .order import Order, OrderItem
from .delivery import Delivery
from .runner import Runner
from .reward_points import RewardPoints, RewardTransaction
from .token import Token
from .cart import Cart, CartItem
from .checkout import Checkout
from .otp import OrderOTP
from .payment import Payment
from .saved_payment_method import SavedPaymentMethod
from .notification import Notification
from .review import Review

__all__ = [
    'db', 'User', 'Food', 'Order', 'OrderItem', 'Delivery', 'Runner',
    'RewardPoints', 'RewardTransaction', 'Token', 'Cart', 'CartItem',
    'Checkout', 'OrderOTP', 'Payment', 'SavedPaymentMethod',
    'Notification', 'Review'
]
