from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from typing import List, Optional
import os
import uuid
from datetime import datetime

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'test_database')

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
products_collection = db.products
cart_collection = db.cart

# Product model structure
def create_product(name: str, category: str, price: float, description: str, 
                  image_url: str, condition: str = "Très bon état", 
                  console: str = None, brand: str = None, stock: int = 1):
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "category": category,
        "price": price,
        "description": description,
        "image_url": image_url,
        "condition": condition,
        "console": console,
        "brand": brand,
        "stock": stock,
        "created_at": datetime.now().isoformat()
    }

# Initialize sample products
@app.on_event("startup")
async def startup_event():
    # Check if products already exist
    if products_collection.count_documents({}) == 0:
        sample_products = [
            # Consoles
            create_product(
                "PlayStation 5",
                "consoles",
                450.00,
                "Console PlayStation 5 d'occasion en excellent état. Inclut la manette DualSense.",
                "https://images.unsplash.com/photo-1507457379470-08b800bebc67",
                "Excellent état",
                "PlayStation 5",
                "Sony",
                2
            ),
            create_product(
                "Xbox One X",
                "consoles", 
                320.00,
                "Console Xbox One X d'occasion. Parfait pour jouer en 4K.",
                "https://images.unsplash.com/photo-1571126770292-d50130a36459",
                "Bon état",
                "Xbox One",
                "Microsoft",
                1
            ),
            create_product(
                "PlayStation 1 Retro",
                "consoles",
                85.00,
                "Console PlayStation 1 vintage avec manette d'origine. Parfait pour les nostalgiques.",
                "https://images.unsplash.com/photo-1531390658120-e06b58d826ea",
                "Bon état",
                "PlayStation 1",
                "Sony",
                1
            ),
            
            # Manettes
            create_product(
                "Manette Xbox Series X",
                "manettes",
                45.00,
                "Manette sans fil Xbox Series X en très bon état. Compatible avec PC et Xbox.",
                "https://images.unsplash.com/photo-1629917629391-47d9209b7c19",
                "Très bon état",
                "Xbox Series X",
                "Microsoft",
                3
            ),
            create_product(
                "Manette DualSense PS5",
                "manettes",
                55.00,
                "Manette DualSense officielle PlayStation 5 avec retour haptique.",
                "https://images.unsplash.com/photo-1571716846319-21f2bf095516",
                "Excellent état",
                "PlayStation 5",
                "Sony",
                2
            ),
            create_product(
                "Manette PlayStation 4",
                "manettes",
                35.00,
                "Manette DualShock 4 pour PlayStation 4. Fonctionne parfaitement.",
                "https://images.pexels.com/photos/32713615/pexels-photo-32713615.jpeg",
                "Bon état",
                "PlayStation 4",
                "Sony",
                4
            ),
            
            # Casques
            create_product(
                "Casque Gaming Pro",
                "casques",
                89.00,
                "Casque gaming haute qualité avec microphone détachable. Son surround 7.1.",
                "https://images.unsplash.com/photo-1677086813101-496781a0f327",
                "Très bon état",
                None,
                "Gaming Pro",
                2
            ),
            create_product(
                "Casque Gaming RGB",
                "casques",
                65.00,
                "Casque gaming avec éclairage RGB et son immersif. Compatible toutes plateformes.",
                "https://images.unsplash.com/photo-1600186279172-fdbaefd74383",
                "Bon état",
                None,
                "RGB Gaming",
                1
            ),
            
            # Claviers
            create_product(
                "Clavier Mécanique RGB",
                "claviers",
                75.00,
                "Clavier mécanique gaming avec switches Blue et rétroéclairage RGB personnalisable.",
                "https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae",
                "Très bon état",
                None,
                "Mechanical Pro",
                2
            ),
            create_product(
                "Clavier Gaming Compact",
                "claviers",
                55.00,
                "Clavier gaming compact 60% avec éclairage RGB. Parfait pour l'esport.",
                "https://images.unsplash.com/photo-1631449061775-c79df03a44f6",
                "Excellent état",
                None,
                "Compact Gaming",
                1
            ),
            
            # Souris
            create_product(
                "Souris Gaming RGB",
                "souris",
                42.00,
                "Souris gaming haute précision avec capteur optique 12000 DPI et éclairage RGB.",
                "https://images.unsplash.com/photo-1628832307345-7404b47f1751",
                "Très bon état",
                None,
                "Gaming RGB",
                3
            ),
            create_product(
                "Souris Esport Pro",
                "souris",
                38.00,
                "Souris gaming professionnelle utilisée par les joueurs esport. Très légère.",
                "https://images.pexels.com/photos/2115256/pexels-photo-2115256.jpeg",
                "Bon état",
                None,
                "Esport Pro",
                2
            ),
            
            # Jeux vidéo
            create_product(
                "Call of Duty Modern Warfare",
                "jeux",
                35.00,
                "Jeu Call of Duty Modern Warfare pour PlayStation 4. Excellent état.",
                "https://images.pexels.com/photos/8307628/pexels-photo-8307628.jpeg",
                "Excellent état",
                "PlayStation 4",
                "Activision",
                1
            ),
        ]
        
        products_collection.insert_many(sample_products)
        print("Sample products inserted successfully!")

# API Routes
@app.get("/")
async def root():
    return {"message": "Gaming Store API"}

@app.get("/api/products")
async def get_products(category: Optional[str] = None, search: Optional[str] = None):
    try:
        query = {}
        
        if category and category != "all":
            query["category"] = category
            
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"brand": {"$regex": search, "$options": "i"}}
            ]
        
        products = list(products_collection.find(query, {"_id": 0}).sort("created_at", -1))
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    try:
        product = products_collection.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories")
async def get_categories():
    try:
        categories = products_collection.distinct("category")
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Cart endpoints
@app.post("/api/cart/add")
async def add_to_cart(product_id: str, quantity: int = 1):
    try:
        # Check if product exists
        product = products_collection.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if item already in cart
        existing_item = cart_collection.find_one({"product_id": product_id})
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item["quantity"] + quantity
            cart_collection.update_one(
                {"product_id": product_id},
                {"$set": {"quantity": new_quantity}}
            )
        else:
            # Add new item
            cart_item = {
                "id": str(uuid.uuid4()),
                "product_id": product_id,
                "quantity": quantity,
                "added_at": datetime.now().isoformat()
            }
            cart_collection.insert_one(cart_item)
        
        return {"message": "Product added to cart successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cart")
async def get_cart():
    try:
        cart_items = list(cart_collection.find({}, {"_id": 0}))
        
        # Get product details for each cart item
        cart_with_products = []
        for item in cart_items:
            product = products_collection.find_one({"id": item["product_id"]}, {"_id": 0})
            if product:
                cart_with_products.append({
                    **item,
                    "product": product
                })
        
        total = sum(item["product"]["price"] * item["quantity"] for item in cart_with_products)
        
        return {
            "items": cart_with_products,
            "total": round(total, 2),
            "count": len(cart_with_products)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/cart/{item_id}")
async def remove_from_cart(item_id: str):
    try:
        result = cart_collection.delete_one({"id": item_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Cart item not found")
        return {"message": "Item removed from cart"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/cart/{item_id}")
async def update_cart_quantity(item_id: str, quantity: int):
    try:
        if quantity <= 0:
            # Remove item if quantity is 0 or negative
            return await remove_from_cart(item_id)
        
        result = cart_collection.update_one(
            {"id": item_id},
            {"$set": {"quantity": quantity}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        return {"message": "Cart updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)