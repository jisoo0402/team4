import pyrebase
import json
import os

class DBhandler:
    def __init__(self):
        here = os.path.dirname(os.path.abspath(__file__))
        cfg_path = os.path.join(here, "authentication", "Authentication", "firebase_auth.json")

        with open(cfg_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database() 
        
    def insert_item(self, name, data, img_path):
            item_info = {
                "seller": data['seller'],
                "name": data['name'],
                "location": data['location'],
                "category": data['category'],
                "price": data['price'],
                "condition": data['condition'],
                "desc": data['desc'],
                "image": img_path
            }

            self.db.child("item").child(name).set(item_info)
            print(data, img_path)
            return True