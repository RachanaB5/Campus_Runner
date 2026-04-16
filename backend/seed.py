#!/usr/bin/env python3
"""
Seed script to populate the database with the real RV University canteen menu.
Run: python seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.models import db, Food, Review, User
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
     "image_url": "https://as1.ftcdn.net/v2/jpg/04/97/03/56/1000_F_497035653_Fh8rJ0Lekz99vYlK6yuso2qXSvrQ2PJp.jpg"},
    {"name": "Chole Batura", "category": "North Indian", "price": 60,
     "description": "Soft bhatura with spiced chole — a North Indian classic",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://tse3.mm.bing.net/th/id/OIP.KD0NfepZxtbJHDw-ZWpT4wHaE8?rs=1&pid=ImgDetMain&o=7&rm=3"},
    {"name": "Dal Khichadi", "category": "North Indian", "price": 70,
     "description": "Comfort food — rice cooked with yellow dal, ghee and cumin",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://tse4.mm.bing.net/th/id/OIP.E9G8iez7S0v6SpCeDKo0VAHaHa?rs=1&pid=ImgDetMain&o=7&rm=3"},

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
     "image_url": "https://th.bing.com/th/id/OIP.J54gdMsTgaD6BXk9pNP5nAHaEK?o=7rm=3&rs=1&pid=ImgDetMain&o=7&rm=3"},
    {"name": "Non Veg Chinese Combo", "category": "Combos", "price": 150,
     "description": "Chicken fried rice or noodles with Manchurian",
     "is_veg": False, "prep_time": 15,
     "image_url": "https://th.bing.com/th/id/OIP.RUTf_GJKdqvIUF4tL0dGAgHaFY?o=7rm=3&rs=1&pid=ImgDetMain&o=7&rm=3"},
    {"name": "Chicken Curry Combo", "category": "Combos", "price": 120,
     "description": "Tender chicken curry served with rice or 2 rotis",
     "is_veg": False, "prep_time": 20,
     "image_url": "https://tse4.mm.bing.net/th/id/OIP.SbwVTn3QHJkveiFkZCkFzQHaHa?rs=1&pid=ImgDetMain&o=7&rm=3"},
    {"name": "Egg Curry Combo", "category": "Combos", "price": 100,
     "description": "Boiled eggs in spicy onion-tomato gravy with rice or roti",
     "is_veg": False, "prep_time": 15,
     "image_url": "https://tse3.mm.bing.net/th/id/OIP.PEICsiA0slOrczax3pTsJwHaFF?rs=1&pid=ImgDetMain&o=7&rm=3"},

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
     "image_url": "https://tse4.mm.bing.net/th/id/OIP.hkXlGSv_xOEEjBX8n2Y2DgHaEH?rs=1&pid=ImgDetMain&o=7&rm=3"},

    # ── PARATHAS ──────────────────────────────────────────────────────
    {"name": "Aloo Paratha with Curd", "category": "Parathas", "price": 70,
     "description": "Crispy potato-stuffed wheat paratha served with fresh curd",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://img.freepik.com/premium-photo/aloo-paratha-indian-potato-stuffed-flatbread-served-with-fresh-curd-isolated-rustic-wooden-background-selective-focus_726363-603.jpg"},
    {"name": "Aloo Cheese Paratha with Curd", "category": "Parathas", "price": 80,
     "description": "Potato and cheese stuffed paratha with curd on the side",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://tse1.mm.bing.net/th/id/OIP.9HE3CrwYOomEfzo_f2GYrQHaFj?rs=1&pid=ImgDetMain&o=7&rm=3"},
    {"name": "Aloo Paneer Mix Paratha", "category": "Parathas", "price": 80,
     "description": "Mixed aloo and paneer stuffed paratha with curd",
     "is_veg": True, "prep_time": 15,
     "image_url": "data:image/webp;base64,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"},
    {"name": "Paneer Paratha with Curd", "category": "Parathas", "price": 90,
     "description": "Cottage cheese stuffed paratha, golden toasted with curd",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://tse4.mm.bing.net/th/id/OIP.MH3twF5iVq4_L1rnRhOrnQHaFX?rs=1&pid=ImgDetMain&o=7&rm=3"},
    {"name": "Paneer Cheese Paratha with Curd", "category": "Parathas", "price": 110,
     "description": "Double indulgence — paneer and cheese stuffed paratha with curd",
     "is_veg": True, "prep_time": 15,
     "image_url": "https://th.bing.com/th/id/OIP.KfW3Qps_810jbd9Y-sB3vwHaE7?o=7rm=3&rs=1&pid=ImgDetMain&o=7&rm=3"},

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
     "image_url": "https://th.bing.com/th/id/OIP.eLsoKgVCFGzk6sX_InuUwAHaHa?w=196&h=196&c=7&r=0&o=7&dpr=2&pid=1.7&rm=3"},
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
     "image_url": "https://wbcdn.in/assets/img/uploads/cache/mywb/uploads/img_7da6ad49d67349e5fe81ba0df42255eaf7cdb929_870_.jpg"},
    {"name": "Veg Roll with Cheese", "category": "Rolls", "price": 80,
     "description": "Spiced vegetables, cheese and sauces wrapped in a crispy paratha roll",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=400&h=300&fit=crop"},
    {"name": "Paneer Roll", "category": "Rolls", "price": 90,
     "description": "Grilled paneer with onion and chutney in a paratha wrap",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://food.ndtv.com/recipe-instant-masala-paneer-roll-958181"},
    {"name": "Paneer Roll with Cheese", "category": "Rolls", "price": 100,
     "description": "Grilled paneer, melty cheese and chutney in a paratha wrap",
     "is_veg": True, "prep_time": 10,
     "image_url": "https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_960,w_960//InstamartAssets/Receipes/potato_paneer_cheese_roll.webp"},
    {"name": "Egg Roll", "category": "Rolls", "price": 70,
     "description": "Egg omelette with masala and onion in a paratha roll",
     "is_veg": False, "prep_time": 10,
     "image_url": "https://dinnersdishesanddesserts.com/wp-content/uploads/2021/12/Vietnamese-Egg-Rolls-square-scaled.jpg"},
    {"name": "Egg Roll with Cheese", "category": "Rolls", "price": 80,
     "description": "Egg omelette, melted cheese and onion in a paratha roll",
     "is_veg": False, "prep_time": 10,
     "image_url": "https://dinnersdishesanddesserts.com/wp-content/uploads/2021/12/Vietnamese-Egg-Rolls-square-scaled.jpg"},
    {"name": "Chicken Roll", "category": "Rolls", "price": 100,
     "description": "Juicy chicken tikka pieces wrapped in a soft paratha",
     "is_veg": False, "prep_time": 15,
     "image_url": "data:image/webp;base64,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"},
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
     "image_url": "https://tse3.mm.bing.net/th/id/OIP.ha4fbIy18MjuJWi-lWScqwHaKX?rs=1&pid=ImgDetMain&o=7&rm=3"},
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
