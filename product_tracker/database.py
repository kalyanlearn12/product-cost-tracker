"""
MongoDB database module for Product Cost Tracker
Handles both local MongoDB and MongoDB Atlas cloud connections
"""

import os
import json
from typing import List, Dict, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductDatabase:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.fallback_file = 'scheduled_products.json'
        self.connected = False
        
        # Environment variables
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.mongodb_database = os.getenv('MONGODB_DATABASE', 'product_tracker')
        self.environment = os.getenv('ENVIRONMENT', 'development')
        
        self._connect()
    
    def _connect(self):
        """Establish MongoDB connection with fallback to JSON file"""
        try:
            # Create MongoDB client with timeout
            self.client = MongoClient(
                self.mongodb_uri,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            # Get database and collection
            self.db = self.client[self.mongodb_database]
            self.collection = self.db.scheduled_products
            
            self.connected = True
            logger.info(f"✅ MongoDB connected successfully to {self.mongodb_database}")
            
            # Migrate existing JSON data if this is first time setup
            self._migrate_json_to_mongo()
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning(f"⚠️ MongoDB connection failed: {e}")
            logger.info(f"📁 Falling back to JSON file storage: {self.fallback_file}")
            self.connected = False
    
    def _migrate_json_to_mongo(self):
        """Migrate existing JSON data to MongoDB on first setup"""
        if not self.connected or not os.path.exists(self.fallback_file):
            return
            
        # Check if MongoDB is empty
        if self.collection.count_documents({}) > 0:
            return  # Already has data
            
        try:
            with open(self.fallback_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    json_data = json.loads(content)
                    if json_data:
                        self.collection.insert_many(json_data)
                        logger.info(f"✅ Migrated {len(json_data)} products from JSON to MongoDB")
        except Exception as e:
            logger.error(f"❌ Failed to migrate JSON to MongoDB: {e}")
    
    def get_all_products(self) -> List[Dict]:
        """Get all scheduled products"""
        if self.connected:
            try:
                # Convert MongoDB cursor to list and remove MongoDB _id field
                products = list(self.collection.find({}, {'_id': 0}))
                logger.info(f"📖 Retrieved {len(products)} products from MongoDB")
                return products
            except Exception as e:
                logger.error(f"❌ MongoDB read error: {e}, falling back to JSON")
                self.connected = False
        
        # Fallback to JSON file
        return self._load_from_json()
    
    def save_products(self, products: List[Dict]) -> bool:
        """Save all products (replaces existing data)"""
        if self.connected:
            try:
                # Clear existing data and insert new
                self.collection.delete_many({})
                if products:
                    self.collection.insert_many(products)
                logger.info(f"💾 Saved {len(products)} products to MongoDB")
                
                # Also save to JSON as backup
                self._save_to_json(products)
                return True
            except Exception as e:
                logger.error(f"❌ MongoDB save error: {e}, falling back to JSON")
                self.connected = False
        
        # Fallback to JSON file
        return self._save_to_json(products)
    
    def add_product(self, product: Dict) -> bool:
        """Add a single product"""
        if self.connected:
            try:
                self.collection.insert_one(product)
                logger.info(f"➕ Added product to MongoDB: {product.get('product_url', 'Unknown')}")
                
                # Also update JSON backup
                products = self.get_all_products()
                self._save_to_json(products)
                return True
            except Exception as e:
                logger.error(f"❌ MongoDB add error: {e}, falling back to JSON")
                self.connected = False
        
        # Fallback to JSON
        products = self._load_from_json()
        products.append(product)
        return self._save_to_json(products)
    
    def remove_product(self, product_url: str) -> bool:
        """Remove a product by URL"""
        if self.connected:
            try:
                result = self.collection.delete_one({'product_url': product_url})
                if result.deleted_count > 0:
                    logger.info(f"🗑️ Removed product from MongoDB: {product_url}")
                    
                    # Also update JSON backup
                    products = self.get_all_products()
                    self._save_to_json(products)
                    return True
                return False
            except Exception as e:
                logger.error(f"❌ MongoDB remove error: {e}, falling back to JSON")
                self.connected = False
        
        # Fallback to JSON
        products = self._load_from_json()
        original_count = len(products)
        products = [p for p in products if p.get('product_url') != product_url]
        if len(products) < original_count:
            self._save_to_json(products)
            return True
        return False
    
    def _load_from_json(self) -> List[Dict]:
        """Load products from JSON file"""
        if os.path.exists(self.fallback_file):
            try:
                with open(self.fallback_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        products = json.loads(content)
                        logger.info(f"📁 Loaded {len(products)} products from JSON file")
                        return products
            except Exception as e:
                logger.error(f"❌ JSON read error: {e}")
        
        logger.info("📁 No JSON file found, returning empty list")
        return []
    
    def _save_to_json(self, products: List[Dict]) -> bool:
        """Save products to JSON file"""
        try:
            with open(self.fallback_file, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Saved {len(products)} products to JSON file")
            return True
        except Exception as e:
            logger.error(f"❌ JSON save error: {e}")
            return False
    
    def get_connection_status(self) -> Dict:
        """Get current database connection status"""
        return {
            'connected': self.connected,
            'mongodb_uri': self.mongodb_uri if self.connected else None,
            'database': self.mongodb_database if self.connected else None,
            'environment': self.environment,
            'fallback_file': self.fallback_file,
            'product_count': len(self.get_all_products())
        }
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("🔌 MongoDB connection closed")

# Global database instance
db = ProductDatabase()

# Convenience functions for backward compatibility
def load_scheduled() -> List[Dict]:
    """Load scheduled products from database"""
    return db.get_all_products()

def save_scheduled(products: List[Dict]) -> bool:
    """Save scheduled products to database"""
    return db.save_products(products)

def add_scheduled_product(product: Dict) -> bool:
    """Add a scheduled product to database"""
    return db.add_product(product)

def remove_scheduled_product(product_url: str) -> bool:
    """Remove a scheduled product from database"""
    return db.remove_product(product_url)

def get_database_status() -> Dict:
    """Get database connection status"""
    return db.get_connection_status()
