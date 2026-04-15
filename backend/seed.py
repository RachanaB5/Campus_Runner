#!/usr/bin/env python3
"""
Seed script to populate the database with the real RV University canteen menu.
Run: python seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db
from models import Food, Review, User
import uuid
from datetime import datetime, timedelta

MENU_ITEMS = [
    # ── MEALS ─────────────────────────────────────────────────────────
    {"name": "North Mini Meals", "category": "Meals", "price": 70,
     "description": "A wholesome North Indian mini thali with dal, sabzi, roti and rice",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&h=300&fit=crop"},
    {"name": "North Full Meals", "category": "Meals", "price": 120,
     "description": "Full North Indian thali with dal, 2 sabzis, roti, rice, salad and pickle",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&h=300&fit=crop"},
    {"name": "South Mini Meals", "category": "Meals", "price": 50,
     "description": "South Indian mini meals with rice, sambar, rasam and 2 curries",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1567337710282-00832b415979?w=400&h=300&fit=crop"},
    {"name": "South Full Meals", "category": "Meals", "price": 100,
     "description": "Full South Indian banana leaf style meals with rice, sambar, rasam and 3 curries",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1630383249896-424e482df921?w=400&h=300&fit=crop"},

    # ── NORTH INDIAN ──────────────────────────────────────────────────
    {"name": "Poori Chole", "category": "North Indian", "price": 50,
     "description": "Fluffy puris served with spicy chickpea curry",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=400&h=300&fit=crop"},
    {"name": "Chole Batura", "category": "North Indian", "price": 60,
     "description": "Soft bhatura with spiced chole — a North Indian classic",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1626082927389-6cd097cee6a2?w=400&h=300&fit=crop"},
    {"name": "Dal Khichadi", "category": "North Indian", "price": 70,
     "description": "Comfort food — rice cooked with yellow dal, ghee and cumin",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1546549032-9571cd6b27df?w=400&h=300&fit=crop"},

    # ── COMBOS ────────────────────────────────────────────────────────
    {"name": "Jeera Rice with Dal Tadka", "category": "Combos", "price": 70,
     "description": "Aromatic jeera rice paired with smoky dal tadka",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1596797038530-2c107229654b?w=400&h=300&fit=crop"},
    {"name": "Rajma / Chole Rice", "category": "Combos", "price": 70,
     "description": "Steamed rice with rich rajma or chole curry",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1567337710282-00832b415979?w=400&h=300&fit=crop"},
    {"name": "Aloo Paratha with Chole", "category": "Combos", "price": 80,
     "description": "Stuffed potato paratha served with spicy chole",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=400&h=300&fit=crop"},
    {"name": "Paneer Curry Combo", "category": "Combos", "price": 120,
     "description": "Soft paneer in rich tomato gravy with rice or roti",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=400&h=300&fit=crop"},
    {"name": "Veg Chinese Combo", "category": "Combos", "price": 120,
     "description": "Veg fried rice or veg noodles served with Manchurian",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1569050467447-ce54b3bbc37d?w=400&h=300&fit=crop"},
    {"name": "Non Veg Chinese Combo", "category": "Combos", "price": 150,
     "description": "Chicken fried rice or noodles with Manchurian",
     "is_veg": False, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=400&h=300&fit=crop"},
    {"name": "Chicken Curry Combo", "category": "Combos", "price": 120,
     "description": "Tender chicken curry served with rice or 2 rotis",
     "is_veg": False, "prep_time": 20,
     "image_url": "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?w=400&h=300&fit=crop"},
    {"name": "Egg Curry Combo", "category": "Combos", "price": 100,
     "description": "Boiled eggs in spicy onion-tomato gravy with rice or roti",
     "is_veg": False, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1647888162325-346cc541bcc9?w=400&h=300&fit=crop"},

    # ── BIRIYANIS ─────────────────────────────────────────────────────
    {"name": "Veg Hyderabadi Biryani", "category": "Biriyanis", "price": 100,
     "description": "Aromatic basmati rice layered with spiced vegetables and saffron",
     "is_veg": True, "prep_time": 25,
     "image_url": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400&h=300&fit=crop"},
    {"name": "Mushroom Donne Biryani", "category": "Biriyanis", "price": 120,
     "description": "Donne-style biryani with mushrooms served in a leaf bowl",
     "is_veg": True, "prep_time": 25,
     "image_url": "https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=400&h=300&fit=crop"},
    {"name": "Egg Hyderabadi Biryani", "category": "Biriyanis", "price": 110,
     "description": "Fragrant biryani with boiled eggs and dum-cooked spices",
     "is_veg": False, "prep_time": 25,
     "image_url": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&h=300&fit=crop"},
    {"name": "Chicken Hyderabadi Biryani", "category": "Biriyanis", "price": 140,
     "description": "Classic dum biryani with tender chicken marinated in spices",
     "is_veg": False, "prep_time": 30,
     "image_url": "https://images.unsplash.com/photo-1714611626323-5ba6204453be?w=400&h=300&fit=crop"},
    {"name": "Chicken Donne Biryani", "category": "Biriyanis", "price": 140,
     "description": "Donne-style chicken biryani — Bangalore's favourite street style",
     "is_veg": False, "prep_time": 30,
     "image_url": "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=400&h=300&fit=crop"},
    {"name": "Chicken Kabab Biryani", "category": "Biriyanis", "price": 150,
     "description": "Biryani with smoky chicken kabab pieces layered through",
     "is_veg": False, "prep_time": 30,
     "image_url": "https://images.unsplash.com/photo-1633945274417-da79a1f93df2?w=400&h=300&fit=crop"},

    # ── PARATHAS ──────────────────────────────────────────────────────
    {"name": "Aloo Paratha with Curd", "category": "Parathas", "price": 70,
     "description": "Crispy potato-stuffed wheat paratha served with fresh curd",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=400&h=300&fit=crop"},
    {"name": "Aloo Cheese Paratha with Curd", "category": "Parathas", "price": 80,
     "description": "Potato and cheese stuffed paratha with curd on the side",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1604152135912-04a022e23696?w=400&h=300&fit=crop"},
    {"name": "Aloo Paneer Mix Paratha", "category": "Parathas", "price": 80,
     "description": "Mixed aloo and paneer stuffed paratha with curd",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=400&h=300&fit=crop"},
    {"name": "Paneer Paratha with Curd", "category": "Parathas", "price": 90,
     "description": "Cottage cheese stuffed paratha, golden toasted with curd",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&h=300&fit=crop"},
    {"name": "Paneer Cheese Paratha with Curd", "category": "Parathas", "price": 110,
     "description": "Double indulgence — paneer and cheese stuffed paratha with curd",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop"},

    # ── PASTA ─────────────────────────────────────────────────────────
    {"name": "Pasta Creamy Alfredo", "category": "Pasta", "price": 70,
     "description": "Penne in rich white sauce with herbs and cream",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=400&h=300&fit=crop"},
    {"name": "Alfredo with Cheese", "category": "Pasta", "price": 80,
     "description": "Creamy white sauce pasta loaded with extra cheese",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1555949258-eb67b1ef0ceb?w=400&h=300&fit=crop"},
    {"name": "Peri Peri Mac N Cheese", "category": "Pasta", "price": 90,
     "description": "Spicy peri peri flavoured macaroni and cheese",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1543339308-43e59d6b73a6?w=400&h=300&fit=crop"},

    # ── PIZZA & BREAD ─────────────────────────────────────────────────
    {"name": "Chessy Garlic Bread", "category": "Pizza & Bread", "price": 50,
     "description": "Toasted garlic bread loaded with melted cheese",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1573140247632-f8fd74997d5c?w=400&h=300&fit=crop"},
    {"name": "Margherita Pizza", "category": "Pizza & Bread", "price": 100,
     "description": "Classic tomato sauce and mozzarella on a thin crust",
     "is_veg": True, "prep_time": 20,
     "image_url": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400&h=300&fit=crop"},
    {"name": "Tandoori Paneer Pizza", "category": "Pizza & Bread", "price": 120,
     "description": "Pizza with tandoori paneer, capsicum and onion topping",
     "is_veg": True, "prep_time": 20,
     "image_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400&h=300&fit=crop"},
    {"name": "Tandoori Mushroom Pizza", "category": "Pizza & Bread", "price": 120,
     "description": "Mushroom and capsicum pizza with tandoori seasoning",
     "is_veg": True, "prep_time": 20,
     "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400&h=300&fit=crop"},
    {"name": "Bread Paneer Pizza", "category": "Pizza & Bread", "price": 50,
     "description": "Paneer topping on toasted bread pizza base",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1571407970349-bc81e7e96d47?w=400&h=300&fit=crop"},
    {"name": "Bread Mushroom Pizza", "category": "Pizza & Bread", "price": 50,
     "description": "Mushroom and cheese on a toasted bread pizza base",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400&h=300&fit=crop"},

    # ── ROLLS ─────────────────────────────────────────────────────────
    {"name": "Veg Roll", "category": "Rolls", "price": 70,
     "description": "Spiced vegetables wrapped in a crispy paratha roll",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=400&h=300&fit=crop"},
    {"name": "Veg Roll with Cheese", "category": "Rolls", "price": 80,
     "description": "Spiced vegetables, cheese and sauces wrapped in a crispy paratha roll",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=400&h=300&fit=crop"},
    {"name": "Paneer Roll", "category": "Rolls", "price": 90,
     "description": "Grilled paneer with onion and chutney in a paratha wrap",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&h=300&fit=crop"},
    {"name": "Paneer Roll with Cheese", "category": "Rolls", "price": 100,
     "description": "Grilled paneer, melty cheese and chutney in a paratha wrap",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&h=300&fit=crop"},
    {"name": "Egg Roll", "category": "Rolls", "price": 70,
     "description": "Egg omelette with masala and onion in a paratha roll",
     "is_veg": False, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=400&h=300&fit=crop"},
    {"name": "Egg Roll with Cheese", "category": "Rolls", "price": 80,
     "description": "Egg omelette, melted cheese and onion in a paratha roll",
     "is_veg": False, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=400&h=300&fit=crop"},
    {"name": "Chicken Roll", "category": "Rolls", "price": 100,
     "description": "Juicy chicken tikka pieces wrapped in a soft paratha",
     "is_veg": False, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1627308595229-7830a5c91f9f?w=400&h=300&fit=crop"},
    {"name": "Chicken Roll with Cheese", "category": "Rolls", "price": 110,
     "description": "Juicy chicken tikka pieces with cheese wrapped in a soft paratha",
     "is_veg": False, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1627308595229-7830a5c91f9f?w=400&h=300&fit=crop"},
    {"name": "Peri Peri Chicken Roll", "category": "Rolls", "price": 100,
     "description": "Spicy peri peri chicken with mayo in a paratha wrap",
     "is_veg": False, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=400&h=300&fit=crop"},
    {"name": "Peri Peri Chicken Roll with Cheese", "category": "Rolls", "price": 110,
     "description": "Spicy peri peri chicken, cheese and mayo in a paratha wrap",
     "is_veg": False, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=400&h=300&fit=crop"},
    {"name": "BBQ Chicken Roll", "category": "Rolls", "price": 100,
     "description": "BBQ glazed chicken with crunchy slaw in a paratha",
     "is_veg": False, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1551782450-a2132b4ba21d?w=400&h=300&fit=crop"},
    {"name": "BBQ Chicken Roll with Cheese", "category": "Rolls", "price": 110,
     "description": "BBQ glazed chicken, cheese and crunchy slaw in a paratha",
     "is_veg": False, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1551782450-a2132b4ba21d?w=400&h=300&fit=crop"},

    # ── BURGERS ───────────────────────────────────────────────────────
    {"name": "Veg Burger", "category": "Burgers", "price": 60,
     "description": "Crispy veggie patty with fresh lettuce, tomatoes and special sauce",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=400&h=300&fit=crop"},
    {"name": "Veg Burger with Cheese", "category": "Burgers", "price": 70,
     "description": "Crispy veggie patty with cheese, lettuce, tomatoes and special sauce",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=400&h=300&fit=crop"},
    {"name": "Chicken Burger", "category": "Burgers", "price": 70,
     "description": "Juicy chicken patty with crisp lettuce and mayo",
     "is_veg": False, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=300&fit=crop"},
    {"name": "Chicken Burger with Cheese", "category": "Burgers", "price": 80,
     "description": "Juicy chicken patty with cheese, crisp lettuce and mayo",
     "is_veg": False, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=300&fit=crop"},
    {"name": "Peri Peri Chicken Burger", "category": "Burgers", "price": 90,
     "description": "Spicy peri peri chicken fillet with coleslaw",
     "is_veg": False, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=400&h=300&fit=crop"},
    {"name": "Peri Peri Chicken Burger with Cheese", "category": "Burgers", "price": 100,
     "description": "Spicy peri peri chicken fillet with cheese and coleslaw",
     "is_veg": False, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=400&h=300&fit=crop"},
    {"name": "BBQ Chicken Burger", "category": "Burgers", "price": 90,
     "description": "BBQ glazed chicken with pickles and smoky sauce",
     "is_veg": False, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1607013251379-e6eecfffe234?w=400&h=300&fit=crop"},
    {"name": "BBQ Chicken Burger with Cheese", "category": "Burgers", "price": 100,
     "description": "BBQ glazed chicken with cheese, pickles and smoky sauce",
     "is_veg": False, "prep_time": 15,
     "image_url": "https://images.unsplash.com/photo-1607013251379-e6eecfffe234?w=400&h=300&fit=crop"},
    {"name": "Vada Pav", "category": "Burgers", "price": 30,
     "description": "Mumbai's street food classic — spiced potato vada in a soft pav",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=400&h=300&fit=crop"},
    {"name": "Vada Pav with Cheese", "category": "Burgers", "price": 40,
     "description": "Mumbai's street food classic with a cheesy twist",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=400&h=300&fit=crop"},
    {"name": "Bun Samosa", "category": "Burgers", "price": 40,
     "description": "Crispy samosa stuffed inside a pav with chutney",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1697155836252-d7f969108b5a?w=400&h=300&fit=crop"},
    {"name": "Bun Samosa with Cheese", "category": "Burgers", "price": 50,
     "description": "Crispy samosa stuffed inside a pav with chutney and cheese",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1697155836252-d7f969108b5a?w=400&h=300&fit=crop"},

    # ── MAGGI ─────────────────────────────────────────────────────────
    {"name": "Maggi Masala", "category": "Maggi", "price": 35,
     "description": "Classic Maggi noodles cooked with masala",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1569050467447-ce54b3bbc37d?w=400&h=300&fit=crop"},
    {"name": "Peri Peri / Extra Masala Maggi", "category": "Maggi", "price": 45,
     "description": "Spiced-up Maggi with peri peri, extra masala, corn or cheese",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1555949258-eb67b1ef0ceb?w=400&h=300&fit=crop"},
    {"name": "Maggi Special", "category": "Maggi", "price": 50,
     "description": "Maggi with extra masala or peri peri and extra cheese",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1543339308-43e59d6b73a6?w=400&h=300&fit=crop"},

    # ── LASSI ────────────────────────────────────────────────────────
    {"name": "Buttermilk", "category": "Lassi", "price": 25,
     "description": "Chilled salted buttermilk with cumin and curry leaves",
     "is_veg": True, "prep_time": 2,
     "image_url": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop"},
    {"name": "Sweet Lassi", "category": "Lassi", "price": 50,
     "description": "Chilled sweet yoghurt drink",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1571407970349-bc81e7e96d47?w=400&h=300&fit=crop"},
    {"name": "Strawberry Lassi", "category": "Lassi", "price": 65,
     "description": "Thick yoghurt lassi blended with fresh strawberry",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=400&h=300&fit=crop"},
    {"name": "Chocolate Lassi", "category": "Lassi", "price": 65,
     "description": "Creamy lassi blended with chocolate syrup",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=400&h=300&fit=crop"},
    {"name": "Mango Lassi", "category": "Lassi", "price": 65,
     "description": "Thick lassi blended with mango pulp",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=400&h=300&fit=crop"},
    {"name": "Banana Lassi", "category": "Lassi", "price": 65,
     "description": "Creamy banana lassi blended fresh",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=400&h=300&fit=crop"},
    {"name": "Rose Lassi", "category": "Lassi", "price": 65,
     "description": "Rose syrup blended into a chilled yoghurt lassi",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=400&h=300&fit=crop"},

    # ── SODA ─────────────────────────────────────────────────────────
    {"name": "Fresh Lime Soda", "category": "Soda", "price": 35,
     "description": "Zingy fresh lime soda — sweet or salted",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=400&h=300&fit=crop"},
    {"name": "Masala Lemon Soda", "category": "Soda", "price": 40,
     "description": "Spiced masala lemon soda with chaat masala",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=400&h=300&fit=crop"},
    {"name": "Blue Lagoon", "category": "Soda", "price": 50,
     "description": "Cool blue lagoon soda with lemon",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&h=300&fit=crop"},
    {"name": "Mango Soda", "category": "Soda", "price": 50,
     "description": "Chilled mango flavoured soda",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=400&h=300&fit=crop"},
    {"name": "Kala Khatta Soda", "category": "Soda", "price": 50,
     "description": "Tangy kala khatta syrup with chilled soda",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&h=300&fit=crop"},

    # ── FRUIT BOWLS ─────────────────────────────────────────────────
    {"name": "Fresh Fruit Bowl", "category": "Fresh Juices", "price": 50,
     "description": "Seasonal fresh cut fruits served chilled",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=400&h=300&fit=crop"},
    {"name": "Fruit Bowl with Ice Cream", "category": "Fresh Juices", "price": 65,
     "description": "Fresh fruit bowl topped with a scoop of ice cream",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1490474418585-ba9bad8fd0ea?w=400&h=300&fit=crop"},

    # ── TEA & COFFEE ────────────────────────────────────────────────
    {"name": "Regular Tea", "category": "Tea & Coffee", "price": 15,
     "description": "Freshly brewed cutting chai",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1597318181409-cf64d0b5d8a2?w=400&h=300&fit=crop"},
    {"name": "Filter Coffee", "category": "Tea & Coffee", "price": 15,
     "description": "South Indian filter coffee",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400&h=300&fit=crop"},
    {"name": "Fresh Lime Tea", "category": "Tea & Coffee", "price": 15,
     "description": "Hot lime tea with ginger and honey",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=400&h=300&fit=crop"},
    {"name": "Black Tea", "category": "Tea & Coffee", "price": 15,
     "description": "Strong black tea",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1597318181409-cf64d0b5d8a2?w=400&h=300&fit=crop"},
    {"name": "Black Coffee", "category": "Tea & Coffee", "price": 15,
     "description": "Strong black coffee",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400&h=300&fit=crop"},
    {"name": "Ginger Tea", "category": "Tea & Coffee", "price": 17,
     "description": "Warming ginger tea",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&h=300&fit=crop"},
    {"name": "Ginger Coffee", "category": "Tea & Coffee", "price": 17,
     "description": "Ginger-spiced coffee",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400&h=300&fit=crop"},
    {"name": "Hot Badam Milk", "category": "Tea & Coffee", "price": 17,
     "description": "Warm badam milk",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&h=300&fit=crop"},
    {"name": "Café Mocha", "category": "Tea & Coffee", "price": 25,
     "description": "Espresso with steamed milk and chocolate sauce",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400&h=300&fit=crop"},
    {"name": "Horlicks", "category": "Tea & Coffee", "price": 25,
     "description": "Classic malt drink served hot",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&h=300&fit=crop"},
    {"name": "Hot Chocolate", "category": "Tea & Coffee", "price": 25,
     "description": "Rich and creamy hot chocolate",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1506619216599-9d16d0903dfd?w=400&h=300&fit=crop"},
    {"name": "Boost", "category": "Tea & Coffee", "price": 25,
     "description": "Hot boost drink",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&h=300&fit=crop"},

    # ── FRESH JUICES ────────────────────────────────────────────────
    {"name": "Lemon Juice", "category": "Fresh Juices", "price": 25,
     "description": "Fresh squeezed lemon juice",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=400&h=300&fit=crop"},
    {"name": "Watermelon Juice", "category": "Fresh Juices", "price": 40,
     "description": "Chilled fresh watermelon juice",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&h=300&fit=crop"},
    {"name": "Muskmelon Juice", "category": "Fresh Juices", "price": 40,
     "description": "Chilled fresh muskmelon juice",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&h=300&fit=crop"},
    {"name": "Pineapple Juice", "category": "Fresh Juices", "price": 40,
     "description": "Fresh pineapple juice",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1534353473418-4cfa0ac2f85b?w=400&h=300&fit=crop"},
    {"name": "Orange Juice", "category": "Fresh Juices", "price": 40,
     "description": "Fresh orange juice",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400&h=300&fit=crop"},
    {"name": "Mosambi Juice", "category": "Fresh Juices", "price": 40,
     "description": "Fresh mosambi juice",
     "is_veg": True, "prep_time": 3,
     "image_url": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400&h=300&fit=crop"},
    {"name": "Ganga Jamuna", "category": "Fresh Juices", "price": 40,
     "description": "Two layered juice — orange and lime blended together",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1546171753-97d7676e4602?w=400&h=300&fit=crop"},
    {"name": "Mix Fruit Juice", "category": "Fresh Juices", "price": 50,
     "description": "Blend of seasonal fruits for a refreshing glass",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1546171753-97d7676e4602?w=400&h=300&fit=crop"},

    # ── MILK SHAKES ────────────────────────────────────────────────
    {"name": "Vanilla Shake", "category": "Milk Shakes", "price": 50,
     "description": "Classic vanilla milk shake",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=400&h=300&fit=crop"},
    {"name": "Chocolate Shake", "category": "Milk Shakes", "price": 50,
     "description": "Classic chocolate milk shake",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=400&h=300&fit=crop"},
    {"name": "Butterscotch Shake", "category": "Milk Shakes", "price": 50,
     "description": "Creamy butterscotch milk shake",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1615478503562-ec2d8aa0e24e?w=400&h=300&fit=crop"},
    {"name": "Black Currant Shake", "category": "Milk Shakes", "price": 50,
     "description": "Creamy black currant milk shake",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1615478503562-ec2d8aa0e24e?w=400&h=300&fit=crop"},
    {"name": "Strawberry Shake", "category": "Milk Shakes", "price": 50,
     "description": "Fresh strawberry milk shake",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=400&h=300&fit=crop"},
    {"name": "Kiwi Shake", "category": "Milk Shakes", "price": 50,
     "description": "Fresh kiwi milk shake",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=400&h=300&fit=crop"},
    {"name": "Litchi Shake", "category": "Milk Shakes", "price": 50,
     "description": "Fresh litchi milk shake",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=400&h=300&fit=crop"},
    {"name": "Mango Milk Shake", "category": "Milk Shakes", "price": 50,
     "description": "Rich and creamy mango milk shake",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1697642452436-9c40773cbcbb?w=400&h=300&fit=crop"},
    {"name": "Banana Shake", "category": "Milk Shakes", "price": 50,
     "description": "Fresh banana milk shake",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1697642452436-9c40773cbcbb?w=400&h=300&fit=crop"},
    {"name": "Sapota Shake", "category": "Milk Shakes", "price": 50,
     "description": "Sapota milk shake",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1697642452436-9c40773cbcbb?w=400&h=300&fit=crop"},
    {"name": "Apple Shake", "category": "Milk Shakes", "price": 50,
     "description": "Fresh apple milk shake",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1697642452436-9c40773cbcbb?w=400&h=300&fit=crop"},
    {"name": "Muskmelon Milk Shake", "category": "Milk Shakes", "price": 50,
     "description": "Muskmelon milk shake",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1697642452436-9c40773cbcbb?w=400&h=300&fit=crop"},
    {"name": "Cold Coffee", "category": "Milk Shakes", "price": 50,
     "description": "Classic cold coffee",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1530569673472-307dc017a82d?w=400&h=300&fit=crop"},

    # ── SPECIAL SHAKES ─────────────────────────────────────────────
    {"name": "Cold Coffee with Ice Cream", "category": "Special Shakes", "price": 65,
     "description": "Chilled coffee blended with ice cream",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1530569673472-307dc017a82d?w=400&h=300&fit=crop"},
    {"name": "Oreo Shake", "category": "Special Shakes", "price": 65,
     "description": "Blended Oreo cookies with milk and ice cream",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1615478503562-ec2d8aa0e24e?w=400&h=300&fit=crop"},
    {"name": "Chocolate Brownie Shake", "category": "Special Shakes", "price": 65,
     "description": "Chocolate brownie blended into a creamy shake",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=400&h=300&fit=crop"},
    {"name": "KitKat Shake", "category": "Special Shakes", "price": 65,
     "description": "KitKat blended into a creamy milk shake",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1543339308-43e59d6b73a6?w=400&h=300&fit=crop"},
    {"name": "Butterfruit Milk Shake", "category": "Special Shakes", "price": 65,
     "description": "Butterfruit milk shake",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1615478503562-ec2d8aa0e24e?w=400&h=300&fit=crop"},
    {"name": "Rose Milk Shake", "category": "Special Shakes", "price": 65,
     "description": "Rose-flavoured chilled milk shake",
     "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=400&h=300&fit=crop"},

    # ── COLD DRINKS ────────────────────────────────────────────────
    {"name": "Coke", "category": "Cold Drinks", "price": 20, "description": "Chilled Coke bottle", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400&h=300&fit=crop"},
    {"name": "Sprite", "category": "Cold Drinks", "price": 20, "description": "Chilled Sprite bottle", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400&h=300&fit=crop"},
    {"name": "Fanta", "category": "Cold Drinks", "price": 20, "description": "Chilled Fanta bottle", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400&h=300&fit=crop"},
    {"name": "Thums Up", "category": "Cold Drinks", "price": 20, "description": "Chilled Thums Up bottle", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400&h=300&fit=crop"},
    {"name": "Limca", "category": "Cold Drinks", "price": 20, "description": "Chilled Limca bottle", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400&h=300&fit=crop"},
    {"name": "Maaza", "category": "Cold Drinks", "price": 25, "description": "Chilled Maaza mango drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400&h=300&fit=crop"},
    {"name": "Pepsi", "category": "Cold Drinks", "price": 20, "description": "Chilled Pepsi bottle", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400&h=300&fit=crop"},
    {"name": "7up", "category": "Cold Drinks", "price": 20, "description": "Chilled 7up bottle", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400&h=300&fit=crop"},
    {"name": "Mirinda", "category": "Cold Drinks", "price": 20, "description": "Chilled Mirinda bottle", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400&h=300&fit=crop"},
    {"name": "Nimbooz", "category": "Cold Drinks", "price": 20, "description": "Chilled Nimbooz bottle", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400&h=300&fit=crop"},
    {"name": "Slice", "category": "Cold Drinks", "price": 20, "description": "Chilled Slice mango drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400&h=300&fit=crop"},
    {"name": "Mountain Dew", "category": "Cold Drinks", "price": 20, "description": "Chilled Mountain Dew bottle", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400&h=300&fit=crop"},
    {"name": "Gatorade", "category": "Cold Drinks", "price": 20, "description": "Chilled Gatorade sports drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400&h=300&fit=crop"},
    {"name": "Power Up", "category": "Cold Drinks", "price": 10, "description": "Campa power up drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1585252168681-e6b15f87c2a5?w=400&h=300&fit=crop"},
    {"name": "Gluco Energy", "category": "Cold Drinks", "price": 10, "description": "Campa gluco energy drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1585252168681-e6b15f87c2a5?w=400&h=300&fit=crop"},
    {"name": "Jeera Up Masala", "category": "Cold Drinks", "price": 10, "description": "Campa jeera masala soda", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1585252168681-e6b15f87c2a5?w=400&h=300&fit=crop"},
    {"name": "Campa Lemon", "category": "Cold Drinks", "price": 10, "description": "Campa lemon soda", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1585252168681-e6b15f87c2a5?w=400&h=300&fit=crop"},
    {"name": "Campa Orange", "category": "Cold Drinks", "price": 10, "description": "Campa orange soda", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1585252168681-e6b15f87c2a5?w=400&h=300&fit=crop"},
    {"name": "Campa Energy", "category": "Cold Drinks", "price": 10, "description": "Campa energy drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1585252168681-e6b15f87c2a5?w=400&h=300&fit=crop"},
    {"name": "Campa Mango/Apple", "category": "Cold Drinks", "price": 10, "description": "Campa mango or apple drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1585252168681-e6b15f87c2a5?w=400&h=300&fit=crop"},
    {"name": "Mixfruit", "category": "Cold Drinks", "price": 20, "description": "Mixfruit bottled drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1585252168681-e6b15f87c2a5?w=400&h=300&fit=crop"},
    {"name": "Sports Drink", "category": "Cold Drinks", "price": 10, "description": "Sports energy drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1585252168681-e6b15f87c2a5?w=400&h=300&fit=crop"},
    {"name": "Indian Mango", "category": "Cold Drinks", "price": 20, "description": "Indian mango drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1585252168681-e6b15f87c2a5?w=400&h=300&fit=crop"},

    # ── SMOOTH DRINKS / TROPICANA / OTHER ──────────────────────────
    {"name": "Chocolate Milk", "category": "Smooth Drinks", "price": 20, "description": "Smoodh chocolate milk", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop"},
    {"name": "Toffee Caramel", "category": "Smooth Drinks", "price": 20, "description": "Smoodh toffee caramel drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop"},
    {"name": "Chocolate Hazelnut", "category": "Smooth Drinks", "price": 20, "description": "Smoodh chocolate hazelnut drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop"},
    {"name": "Coffee Frappe", "category": "Smooth Drinks", "price": 20, "description": "Smoodh coffee frappe", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop"},
    {"name": "Lassi Drink", "category": "Smooth Drinks", "price": 20, "description": "Smoodh lassi drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop"},
    {"name": "Frooti", "category": "Smooth Drinks", "price": 20, "description": "Chilled Frooti mango drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop"},
    {"name": "Appy Fizz", "category": "Smooth Drinks", "price": 20, "description": "Appy Fizz apple drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop"},
    {"name": "Tropicana Orange", "category": "Tropicana", "price": 20, "description": "Tropicana orange juice", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400&h=300&fit=crop"},
    {"name": "Tropicana Guava", "category": "Tropicana", "price": 20, "description": "Tropicana guava juice", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400&h=300&fit=crop"},
    {"name": "Tropicana Mixed Fruit", "category": "Tropicana", "price": 20, "description": "Tropicana mixed fruit juice", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400&h=300&fit=crop"},
    {"name": "Tropicana Mango", "category": "Tropicana", "price": 20, "description": "Tropicana mango juice", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400&h=300&fit=crop"},
    {"name": "Tropicana Pomegranate", "category": "Tropicana", "price": 20, "description": "Tropicana pomegranate juice", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400&h=300&fit=crop"},
    {"name": "Chia Lemon", "category": "Other Drinks", "price": 15, "description": "Chia lemon drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1546171753-97d7676e4602?w=400&h=300&fit=crop"},
    {"name": "Chia Blueberry", "category": "Other Drinks", "price": 15, "description": "Chia blueberry drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1546171753-97d7676e4602?w=400&h=300&fit=crop"},
    {"name": "Chia Orange", "category": "Other Drinks", "price": 15, "description": "Chia orange drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1546171753-97d7676e4602?w=400&h=300&fit=crop"},
    {"name": "Chia Litchi", "category": "Other Drinks", "price": 15, "description": "Chia litchi drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1546171753-97d7676e4602?w=400&h=300&fit=crop"},
    {"name": "Chia Strawberry", "category": "Other Drinks", "price": 15, "description": "Chia strawberry drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1546171753-97d7676e4602?w=400&h=300&fit=crop"},
    {"name": "Chia Cream Bell", "category": "Other Drinks", "price": 15, "description": "Chia cream bell drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1546171753-97d7676e4602?w=400&h=300&fit=crop"},
    {"name": "Choco Milkshake", "category": "Other Drinks", "price": 35, "description": "Chocolate milkshake", "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=400&h=300&fit=crop"},
    {"name": "Butter Scotch Milkshake", "category": "Other Drinks", "price": 35, "description": "Butterscotch milkshake", "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=400&h=300&fit=crop"},
    {"name": "Coffee Milkshake", "category": "Other Drinks", "price": 30, "description": "Coffee milkshake", "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1530569673472-307dc017a82d?w=400&h=300&fit=crop"},
    {"name": "Kesar Badam Milkshake", "category": "Other Drinks", "price": 30, "description": "Kesar badam milkshake", "is_veg": True, "prep_time": 5,
     "image_url": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&h=300&fit=crop"},
    {"name": "Paper Boat Alphonso Mango", "category": "Paper Boat", "price": 25, "description": "Paper Boat alphonso mango drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1464347744102-11db6282f854?w=400&h=300&fit=crop"},
    {"name": "Paper Boat Lychee", "category": "Paper Boat", "price": 25, "description": "Paper Boat lychee drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1464347744102-11db6282f854?w=400&h=300&fit=crop"},
    {"name": "Paper Boat Apple", "category": "Paper Boat", "price": 25, "description": "Paper Boat apple drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1464347744102-11db6282f854?w=400&h=300&fit=crop"},
    {"name": "Paper Boat Aamras", "category": "Paper Boat", "price": 25, "description": "Paper Boat aamras drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1464347744102-11db6282f854?w=400&h=300&fit=crop"},
    {"name": "Paper Boat Orange", "category": "Paper Boat", "price": 25, "description": "Paper Boat orange drink", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1464347744102-11db6282f854?w=400&h=300&fit=crop"},
    {"name": "Paper Boat Coconut Water", "category": "Paper Boat", "price": 60, "description": "Paper Boat coconut water", "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&h=300&fit=crop"},

    # ── ICE CREAM ─────────────────────────────────────────────────────
    {"name": "Alphonso Mango Ice Cream", "category": "Ice Cream", "price": 25,
     "description": "Dairy Day — Real Alphonso mango ice cream",
     "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1501443762994-82bd5dace89a?w=400&h=300&fit=crop"},
    {"name": "Chocolate / Butterscotch Cone", "category": "Ice Cream", "price": 40,
     "description": "Dairy Day ice cream cone — chocolate or butterscotch",
     "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?w=400&h=300&fit=crop"},
    {"name": "Triple Sundae Ice Cream", "category": "Ice Cream", "price": 60,
     "description": "Ideal — Triple sundae with three scoops and toppings",
     "is_veg": True, "prep_time": 2,
     "image_url": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400&h=300&fit=crop"},
    {"name": "Kulfi Candy", "category": "Ice Cream", "price": 30,
     "description": "Ideal — Traditional Indian kulfi on a stick",
     "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1576618148400-f54bed99fcfd?w=400&h=300&fit=crop"},
    {"name": "Matka Kulfi", "category": "Ice Cream", "price": 50,
     "description": "Ideal — Traditional creamy kulfi served in a clay pot",
     "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1576618148400-f54bed99fcfd?w=400&h=300&fit=crop"},
    {"name": "Kaju Malai Ice Cream", "category": "Ice Cream", "price": 50,
     "description": "Ideal — Rich cashew and cream ice cream",
     "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1488900128323-21503983a07e?w=400&h=300&fit=crop"},
    {"name": "Chikku Almond Ice Cream", "category": "Ice Cream", "price": 50,
     "description": "Ideal — Sapodilla (chikku) and almond ice cream",
     "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=400&h=300&fit=crop"},
    {"name": "Cassata Ice Cream", "category": "Ice Cream", "price": 50,
     "description": "Ideal — Layered cassata with fruit and nut ice cream",
     "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=400&h=300&fit=crop"},
    {"name": "Mini Sundae Chocolate", "category": "Ice Cream", "price": 20,
     "description": "Ideal — Mini chocolate sundae ice cream",
     "is_veg": True, "prep_time": 1,
     "image_url": "https://images.unsplash.com/photo-1501443762994-82bd5dace89a?w=400&h=300&fit=crop"},
]


def sync_menu_catalog(flask_app):
    with flask_app.app_context():
        print(f"Syncing {len(MENU_ITEMS)} menu items...")
        menu_names = set()
        for item_data in MENU_ITEMS:
            menu_names.add(item_data["name"])
            food = Food.query.filter_by(name=item_data["name"]).first()
            if not food:
                food = Food(
                    id=str(uuid.uuid4()),
                    rating=0,
                    review_count=0,
                )
                db.session.add(food)

            food.name = item_data["name"]
            food.category = item_data["category"]
            food.price = item_data["price"]
            food.description = item_data["description"]
            food.is_veg = item_data.get("is_veg", True)
            food.prep_time = item_data.get("prep_time", 15)
            food.image_url = item_data.get("image_url", "")
            food.available = True

        for food in Food.query.all():
            if food.name not in menu_names:
                food.available = False

        db.session.commit()
        seed_sample_reviews()
        print(f"✅ Successfully synced {len(MENU_ITEMS)} menu items!")

        # Print category summary
        from sqlalchemy import func
        categories = db.session.query(Food.category, func.count(Food.id)).group_by(Food.category).all()
        print("\nCategory summary:")
        for cat, count in sorted(categories):
            print(f"  {cat}: {count} items")


def seed_menu(flask_app):
    sync_menu_catalog(flask_app)


def _seed_users():
    seeded_users = [
        ('Campus Foodie', 'foodie@rvu.edu.in'),
        ('Arjun M.', 'arjun.seed@rvu.edu.in'),
        ('Priya S.', 'priya.seed@rvu.edu.in'),
    ]
    created = []
    for name, email in seeded_users:
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                id=str(uuid.uuid4()),
                name=name,
                email=email,
                role='customer',
                is_verified=True,
            )
            user.set_password('seeded-pass-123')
            db.session.add(user)
        created.append(user)
    db.session.flush()
    return created


def _review_templates(food):
    lower_name = food.name.lower()
    if 'biryani' in lower_name:
        return [
            (5, f'Absolutely the best {food.name.lower()} on campus. The aroma and spice balance are spot on.'),
            (4, 'Really satisfying portion and great flavour. I would happily order this again after class.'),
            (5, 'The rice stays fluffy and the masala tastes freshly made every single time.'),
        ]
    if any(keyword in lower_name for keyword in ['coffee', 'tea', 'juice', 'lassi', 'shake', 'soda']):
        return [
            (5, f'{food.name} is super refreshing and arrives chilled even during busy hours.'),
            (4, 'Good taste and not overly sweet. Perfect add-on with a snack.'),
            (5, 'Consistently fresh and exactly what I want between classes.'),
        ]
    if any(keyword in lower_name for keyword in ['burger', 'roll', 'pizza', 'sandwich']):
        return [
            (5, f'{food.name} has a great texture and tastes freshly made.'),
            (4, 'Nicely filling and the flavours work really well together.'),
            (5, 'One of my go-to picks when I want something quick but still satisfying.'),
        ]
    if any(keyword in lower_name for keyword in ['ice cream', 'kulfi', 'dessert', 'halwa']):
        return [
            (5, f'{food.name} is such a good sweet finish after a meal.'),
            (4, 'Good portion and nice flavour without feeling too heavy.'),
        ]
    return [
        (5, f'{food.name} tastes fresh and feels worth the price every time.'),
        (4, 'Really dependable campus comfort food with solid flavour.'),
        (5, 'I keep coming back to this because it is consistently good.'),
    ]


def seed_sample_reviews():
    seeded_users = _seed_users()
    foods = Food.query.all()
    if not foods:
        db.session.commit()
        return

    for food in foods:
        existing_seeded = Review.query.filter_by(food_id=food.id, is_seeded=True).count()
        if existing_seeded >= 2:
            continue

        templates = _review_templates(food)
        for index, (rating, comment) in enumerate(templates):
            seeded_user = seeded_users[index % len(seeded_users)]
            review = Review(
                id=str(uuid.uuid4()),
                user_id=seeded_user.id,
                food_id=food.id,
                rating=rating,
                comment=comment,
                is_seeded=True,
                seeded_name=seeded_user.name,
                created_at=datetime.utcnow() - timedelta(days=(index + 1)),
            )
            db.session.add(review)

    db.session.flush()

    for food in foods:
        reviews = Review.query.filter_by(food_id=food.id).all()
        if not reviews:
            continue
        food.rating = round(sum(review.rating for review in reviews) / len(reviews), 1)
        food.review_count = len(reviews)

    db.session.commit()


if __name__ == "__main__":
    from app import app
    seed_menu(app)
