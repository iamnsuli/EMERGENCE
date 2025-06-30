#!/usr/bin/env python3
import requests
import json
import unittest
import os
import sys

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://c5074add-db37-4a52-ba8e-eeaa3e775d0e.preview.emergentagent.com"
API_URL = f"{BACKEND_URL}/api"

class TestBackendAPI(unittest.TestCase):
    """Test suite for the gaming e-commerce backend API"""

    def setUp(self):
        """Setup for each test"""
        self.product_id = None  # Will be set after getting products
        self.cart_item_id = None  # Will be set after adding to cart

    def test_01_products_endpoint(self):
        """Test GET /api/products endpoint"""
        print("\n=== Testing GET /api/products ===")
        response = requests.get(f"{API_URL}/products")
        
        self.assertEqual(response.status_code, 200, "Failed to get products")
        data = response.json()
        
        self.assertIn("products", data, "Response doesn't contain 'products' key")
        self.assertIsInstance(data["products"], list, "Products should be a list")
        self.assertGreater(len(data["products"]), 0, "No products returned")
        
        # Store a product ID for later tests
        self.product_id = data["products"][0]["id"]
        
        print(f"✅ Found {len(data['products'])} products")
        print(f"Sample product: {data['products'][0]['name']}")
        
        return data["products"]

    def test_02_products_by_category(self):
        """Test GET /api/products with category filter"""
        print("\n=== Testing GET /api/products with category filter ===")
        categories = ["consoles", "manettes", "casques", "claviers", "souris", "jeux"]
        
        for category in categories:
            response = requests.get(f"{API_URL}/products?category={category}")
            self.assertEqual(response.status_code, 200, f"Failed to get products for category {category}")
            
            data = response.json()
            self.assertIn("products", data, f"Response for category {category} doesn't contain 'products' key")
            
            # Verify all returned products have the correct category
            for product in data["products"]:
                self.assertEqual(product["category"], category, 
                                f"Product {product['name']} has category {product['category']} instead of {category}")
            
            print(f"✅ Category '{category}' returned {len(data['products'])} products")

    def test_03_products_search(self):
        """Test GET /api/products with search filter"""
        print("\n=== Testing GET /api/products with search filter ===")
        search_terms = ["PlayStation", "Xbox", "Gaming"]
        
        for term in search_terms:
            response = requests.get(f"{API_URL}/products?search={term}")
            self.assertEqual(response.status_code, 200, f"Failed to search for '{term}'")
            
            data = response.json()
            self.assertIn("products", data, f"Search response for '{term}' doesn't contain 'products' key")
            
            # Verify search works (at least one product should match)
            self.assertGreater(len(data["products"]), 0, f"Search for '{term}' returned no results")
            
            print(f"✅ Search for '{term}' returned {len(data['products'])} products")

    def test_04_product_by_id(self):
        """Test GET /api/products/{id} endpoint"""
        print("\n=== Testing GET /api/products/{id} ===")
        
        # Ensure we have a product ID
        if not self.product_id:
            products = self.test_01_products_endpoint()
            self.product_id = products[0]["id"]
        
        response = requests.get(f"{API_URL}/products/{self.product_id}")
        self.assertEqual(response.status_code, 200, f"Failed to get product with ID {self.product_id}")
        
        product = response.json()
        self.assertEqual(product["id"], self.product_id, "Returned product ID doesn't match requested ID")
        
        print(f"✅ Successfully retrieved product: {product['name']}")
        
        # Test invalid product ID
        invalid_id = "nonexistent-id"
        response = requests.get(f"{API_URL}/products/{invalid_id}")
        self.assertEqual(response.status_code, 404, "Should return 404 for invalid product ID")
        
        print("✅ Correctly returns 404 for invalid product ID")

    def test_05_categories_endpoint(self):
        """Test GET /api/categories endpoint"""
        print("\n=== Testing GET /api/categories ===")
        response = requests.get(f"{API_URL}/categories")
        
        self.assertEqual(response.status_code, 200, "Failed to get categories")
        data = response.json()
        
        self.assertIn("categories", data, "Response doesn't contain 'categories' key")
        self.assertIsInstance(data["categories"], list, "Categories should be a list")
        
        expected_categories = ["consoles", "manettes", "casques", "claviers", "souris", "jeux"]
        for category in expected_categories:
            self.assertIn(category, data["categories"], f"Category '{category}' not found")
        
        print(f"✅ Found {len(data['categories'])} categories: {', '.join(data['categories'])}")

    def test_06_add_to_cart(self):
        """Test POST /api/cart/add endpoint"""
        print("\n=== Testing POST /api/cart/add ===")
        
        # Ensure we have a product ID
        if not self.product_id:
            products = self.test_01_products_endpoint()
            self.product_id = products[0]["id"]
        
        # Add product to cart
        response = requests.post(f"{API_URL}/cart/add?product_id={self.product_id}&quantity=2")
        self.assertEqual(response.status_code, 200, "Failed to add product to cart")
        
        print("✅ Successfully added product to cart")
        
        # Test adding invalid product
        invalid_id = "nonexistent-id"
        response = requests.post(f"{API_URL}/cart/add?product_id={invalid_id}&quantity=1")
        self.assertEqual(response.status_code, 404, "Should return 404 for invalid product ID")
        
        print("✅ Correctly returns 404 when adding invalid product to cart")

    def test_07_get_cart(self):
        """Test GET /api/cart endpoint"""
        print("\n=== Testing GET /api/cart ===")
        
        # First add a product to cart if not already done
        if not hasattr(self, 'test_06_add_to_cart_run'):
            self.test_06_add_to_cart()
            self.test_06_add_to_cart_run = True
        
        response = requests.get(f"{API_URL}/cart")
        self.assertEqual(response.status_code, 200, "Failed to get cart")
        
        data = response.json()
        self.assertIn("items", data, "Response doesn't contain 'items' key")
        self.assertIn("total", data, "Response doesn't contain 'total' key")
        self.assertIn("count", data, "Response doesn't contain 'count' key")
        
        self.assertGreater(len(data["items"]), 0, "Cart is empty after adding product")
        
        # Store cart item ID for later tests
        self.cart_item_id = data["items"][0]["id"]
        
        print(f"✅ Cart contains {data['count']} items with total {data['total']}€")
        print(f"✅ First cart item: {data['items'][0]['product']['name']} (Quantity: {data['items'][0]['quantity']})")

    def test_08_update_cart_quantity(self):
        """Test PUT /api/cart/{item_id} endpoint"""
        print("\n=== Testing PUT /api/cart/{item_id} ===")
        
        # First get cart to get item ID if not already done
        if not self.cart_item_id:
            self.test_07_get_cart()
        
        # Update quantity to 3
        response = requests.put(f"{API_URL}/cart/{self.cart_item_id}?quantity=3")
        self.assertEqual(response.status_code, 200, "Failed to update cart quantity")
        
        # Verify quantity was updated
        response = requests.get(f"{API_URL}/cart")
        data = response.json()
        
        item = next((item for item in data["items"] if item["id"] == self.cart_item_id), None)
        self.assertIsNotNone(item, "Updated item not found in cart")
        self.assertEqual(item["quantity"], 3, f"Quantity not updated correctly. Expected 3, got {item['quantity']}")
        
        print("✅ Successfully updated cart item quantity to 3")
        
        # Test updating invalid cart item
        invalid_id = "nonexistent-id"
        response = requests.put(f"{API_URL}/cart/{invalid_id}?quantity=1")
        self.assertEqual(response.status_code, 404, "Should return 404 for invalid cart item ID")
        
        print("✅ Correctly returns 404 when updating invalid cart item")

    def test_09_remove_from_cart(self):
        """Test DELETE /api/cart/{item_id} endpoint"""
        print("\n=== Testing DELETE /api/cart/{item_id} ===")
        
        # First get cart to get item ID if not already done
        if not self.cart_item_id:
            self.test_07_get_cart()
        
        # Remove item from cart
        response = requests.delete(f"{API_URL}/cart/{self.cart_item_id}")
        self.assertEqual(response.status_code, 200, "Failed to remove item from cart")
        
        # Verify item was removed
        response = requests.get(f"{API_URL}/cart")
        data = response.json()
        
        item = next((item for item in data["items"] if item["id"] == self.cart_item_id), None)
        self.assertIsNone(item, "Item still in cart after removal")
        
        print("✅ Successfully removed item from cart")
        
        # Test removing invalid cart item
        invalid_id = "nonexistent-id"
        response = requests.delete(f"{API_URL}/cart/{invalid_id}")
        self.assertEqual(response.status_code, 404, "Should return 404 for invalid cart item ID")
        
        print("✅ Correctly returns 404 when removing invalid cart item")

    def test_10_sample_products_verification(self):
        """Verify sample products were created properly"""
        print("\n=== Verifying Sample Products ===")
        
        response = requests.get(f"{API_URL}/products")
        self.assertEqual(response.status_code, 200, "Failed to get products")
        
        products = response.json()["products"]
        
        # Verify total count
        self.assertEqual(len(products), 13, f"Expected 13 sample products, found {len(products)}")
        
        # Verify categories and counts
        categories = {}
        for product in products:
            category = product["category"]
            if category in categories:
                categories[category] += 1
            else:
                categories[category] = 1
        
        expected_categories = {
            "consoles": 3,
            "manettes": 3,
            "casques": 2,
            "claviers": 2,
            "souris": 2,
            "jeux": 1
        }
        
        for category, count in expected_categories.items():
            self.assertIn(category, categories, f"Category '{category}' not found")
            self.assertEqual(categories[category], count, 
                            f"Expected {count} products in '{category}', found {categories[category]}")
        
        print("✅ All 13 sample products verified across 6 categories:")
        for category, count in categories.items():
            print(f"  - {category}: {count} products")

if __name__ == "__main__":
    print(f"Testing backend API at: {API_URL}")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)