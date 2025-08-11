import os
import json

def ensure_data_files():
    """Ensure required data files exist on Render"""
    
    # Create scheduled_products.json if it doesn't exist
    scheduled_file = 'scheduled_products.json'
    if not os.path.exists(scheduled_file):
        with open(scheduled_file, 'w') as f:
            json.dump([], f, indent=2)
        print(f"Created {scheduled_file}")
    
    # Create chat_aliases.json if it doesn't exist
    aliases_file = os.path.join('product_tracker', 'chat_aliases.json')
    if not os.path.exists(aliases_file):
        # Create directory if needed
        os.makedirs(os.path.dirname(aliases_file), exist_ok=True)
        
        # Default aliases
        default_aliases = [
            {"alias": "Kalyan", "chat_id": "249722033"},
            {"alias": "Uma", "chat_id": "258922383"},
            {"alias": "Aravind", "chat_id": "894760582"},
            {"alias": "Naresh", "chat_id": "8200569756"},
            {"alias": "Balu", "chat_id": "704508499"}
        ]
        
        with open(aliases_file, 'w') as f:
            json.dump(default_aliases, f, indent=2)
        print(f"Created {aliases_file}")

if __name__ == "__main__":
    ensure_data_files()
