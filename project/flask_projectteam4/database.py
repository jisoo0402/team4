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
    
    #데이터베이스에 사용자 가입 데이터 넘기기
    def insert_user(self, data, pw):
         user_info={
              "id":data['id'],
              "pw":pw,
              "email":data['email'],
              "nickname":data['nickname']
         }
         if self.user_duplicate_check(str(data['id'])):
              self.db.child("user").child(data['id']).set(user_info)
              print(data)
              return True
         else:
              return False
    
    #아이디 중복 체크
    def user_duplicate_check(self, id_string):
        users=self.db.child("user").get()
        print("users###", users.val())
        if users.val() is None: return True
        else:
            for res in users.each():
                value=res.val()
                if value['id'] == id_string:
                     return False
            return True
    
    #사용자 정보 받기
    def get_user(self, id_string):
        users=self.db.child("user").get()
        if not users.val():
            return None
        for res in users.each():
            value=res.val()
            if value['id']==id_string:
                return value
        return None

    #로그인할 때 데이터베이스에 있는 계정인지 찾기
    def find_user(self, id, pw):
        users=self.db.child("user").get()
        target_value=[]

        if not users.val():
            return False
        for res in users.each():
            value=res.val()
            if value.get('id')==id and value.get('pw')==pw:
                return True
        return False
    
    # 상품 등록 테이블에서 데이터 가져오기
    def get_items(self):
        items = self.db.child("item").get().val()
        return items
    
    # 상품이름으로 item 테이블에서 정보 가져오기
    def get_item_byname(self, name):
        items = self.db.child("item").get()
        target_value=""
        print("########", name)
        for res in items.each():
            key_value = res.key()
            
            if key_value== name:
                target_value=res.val()
        return target_value    