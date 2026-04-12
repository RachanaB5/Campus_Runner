from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.food import Food
from models.order import Order, OrderItem
from models.delivery import Delivery
from models.runner import Runner
from models.reward_points import RewardPoints, RewardTransaction
from models.token import Token
from models.cart import Cart, CartItem
from models.checkout import Checkout
from models.otp import OrderOTP
from models.payment import Payment
from models.saved_payment_method import SavedPaymentMethod
from models.notification import Notification
from models.review import Review

__all__ = ['db', 'User', 'Food', 'Order', 'OrderItem', 'Delivery', 'Runner', 'RewardPoints', 'RewardTransaction', 'Token', 'Cart', 'CartItem', 'Checkout', 'OrderOTP', 'Payment', 'SavedPaymentMethod', 'Notification', 'Review']
