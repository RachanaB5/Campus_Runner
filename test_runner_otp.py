#!/usr/bin/env python
"""Test script to send runner OTP notifications"""
import sys
sys.path.insert(0, 'backend')

from backend.utils import send_runner_otp_notification
from backend.app import app

# Test data
runner_email = "kumarsrinidhi246@gmail.com"  # Test runner email
runner_name = "Amit"
order_number = "ORD-2026-04-13-001"
pickup_otp = "5847"
delivery_otp = "3921"
pickup_location = "Main Canteen, Block A"
delivery_address = "Room 234, North Block, Campus"

print("Sending Runner OTP Notification...")
result = send_runner_otp_notification(
    runner_email=runner_email,
    runner_name=runner_name,
    order_number=order_number,
    pickup_otp=pickup_otp,
    delivery_otp=delivery_otp,
    pickup_location=pickup_location,
    delivery_address=delivery_address,
    app=app
)

print(f"Result: {result}")
