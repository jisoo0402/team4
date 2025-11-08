from base64 import encode
from flask import Flask, render_template, redirect, url_for, session, request, flash
from database import DBhandler
import os
import hashlib

app = Flask(__name__)
app.secret_key = "ewhamarket_secret"

DB = DBhandler()

USER_ID = "ewha"
USER_PW = "1234"

# --------------------------------
# 초기 데이터
# --------------------------------
products = []
reviews = [
    {
        "name": "이화인123",
        "title": "🎀 카페 디저트보다 맛있어요!",
        "product": "배꽃마들렌 6입 쿠키세트",
        "rating": "5",
        "content": "너무 맛있어요! 가족, 지인 선물용으로 샀는데 다들 좋아했어요! 향긋하고 촉촉해서 선물용으로 강추!",
        "image": "배꽃마들렌.jpg"
    },
    {
        "name": "ewha_shop",
        "title": "💚 귀여움 한도 초과!",
        "product": "이화그린5색펜세트",
        "rating": "4",
        "content": "실리콘 재질 부드럽고 로고 각인이 예뻐요. 가볍고 포인트 주기 좋아요!",
        "image": "이화그린5색펜세트.jpg"
    }
]

# --------------------------------
# 홈
# --------------------------------
@app.route('/')
def index():
    return render_template('index.html', logged_in=session.get("logged_in", False))

# --------------------------------
# 상품 등록
# --------------------------------
@app.route('/register', methods=['GET', 'POST'])
def product_register():
    if request.method == 'POST':
        seller = request.form.get('seller')
        name = request.form.get('name')
        location = request.form.get('location')
        category = request.form.get('category')
        price = request.form.get('price')
        condition = request.form.get('condition')
        desc = request.form.get('desc')
        image = request.files.get('image')

        print(f"[상품 등록됨] {name}, {price}")

        image_filename = None
        if image and image.filename != '':
            image_filename = image.filename
            image.save(os.path.join('static', 'image', image_filename))
        else:
            image_filename = "default.png"

        data = request.form    
        DB.insert_item(data['name'], data, image_filename)

        products.append({
            "seller": seller,
            "name": name,
            "location": location,
            "category": category,
            "price": price,
            "condition": condition,
            "desc": desc,
            "image": image_filename
        })

        flash("상품이 등록되었습니다!")
        return redirect(url_for('product_list'))

    return render_template('product_register.html', logged_in=session.get("logged_in", False))
#  상품 상세 페이지 각각 연결
@app.route('/detail/pen')
def detail_pen():
    return render_template('product_detail_pen.html', logged_in=session.get("logged_in", False))

@app.route('/detail/madeline')
def detail_madeline():
    return render_template('product_detail_madeline.html', logged_in=session.get("logged_in", False))

@app.route('/detail/buds')
def detail_buds():
    return render_template('product_detail_buds.html', logged_in=session.get("logged_in", False))

@app.route('/detail/jumper')
def detail_jumper():
    return render_template('product_detail_jumper.html', logged_in=session.get("logged_in", False))

#  상품 목록
@app.route('/list')
def product_list():
    return render_template('product_list.html', products=products, logged_in=session.get("logged_in", False))

#  상품 삭제
@app.route('/delete/<int:index>', methods=['POST'])
def delete_product(index):
    if 0 <= index < len(products):
        deleted_item = products.pop(index)
        print(f"[상품 삭제됨] {deleted_item['name']}")
        flash(f"'{deleted_item['name']}' 상품이 삭제되었습니다.")
    else:
        flash("해당 상품을 찾을 수 없습니다.")
    return redirect(url_for('product_list'))

#  상품 상세 보기 (고정 상품 + 등록 상품)
@app.route('/detail/<item>')
def product_detail(item):
    # 고정 상품
    if item == "pen":
        product = {
            "name": "이화그린5색펜세트",
            "price": "₩10,000",
            "desc": "이화 상징 색상을 담은 5색 펜 세트입니다.",
            "image": "이화그린5색펜세트.jpg"
        }
    elif item == "madeline":
        product = {
            "name": "배꽃마들렌 6입 쿠키2입세트",
            "price": "₩15,000",
            "desc": "이화의 상징 배꽃을 모티브로 한 고급 디저트 세트입니다.",
            "image": "배꽃마들렌.jpg"
        }
    elif item == "buds":
        product = {
            "name": "이화컬렉션 버즈케이스",
            "price": "₩20,000",
            "desc": "로고 각인 디자인이 돋보이는 실리콘 버즈 케이스.",
            "image": "이화버즈.jpg"
        }
    elif item == "jumper":
        product = {
            "name": "이화야구점퍼",
            "price": "₩50,000",
            "desc": "봄·가을에 입기 좋은 야구 점퍼, 이화 로고가 포인트!",
            "image": "봄가을야구점퍼.jpg"
        }
    else:
        for p in products:
            if p["name"] == item:
                product = p
                break
        else:
            flash("해당 상품을 찾을 수 없습니다.")
            return redirect(url_for('product_list'))

    return render_template('product_detail.html', product=product, logged_in=session.get("logged_in", False))

# --------------------------------
# 리뷰 기능
# --------------------------------
@app.route('/review')
@app.route('/review/write')
def review_main():
    recent = reviews[-3:][::-1]
    return render_template('review_write.html', reviews=recent, logged_in=session.get("logged_in", False))

@app.route('/review/submit', methods=['POST'])
def review_submit():
    name = request.form.get('name')
    title = request.form.get('title')
    product = request.form.get('product')
    rating = request.form.get('rating')
    content = request.form.get('content')
    image = request.files.get('image')

    image_filename = None
    if image and image.filename != '':
        image_filename = image.filename
        image.save(os.path.join('static', 'image', image_filename))

    reviews.append({
        "name": name,
        "title": title,
        "product": product,
        "rating": rating,
        "content": content,
        "image": image_filename
    })

    flash("리뷰가 등록되었습니다!")
    return redirect(url_for('review_main'))

@app.route('/review/list')
def review_list():
    return render_template('review_list.html', reviews=reviews[::-1], logged_in=session.get("logged_in", False))

@app.route('/review/detail/<int:index>')
def review_detail(index):
    if 0 <= index < len(reviews):
        review = reviews[index]
        return render_template('review_detail.html', review=review, logged_in=session.get("logged_in", False))
    else:
        flash("해당 리뷰를 찾을 수 없습니다.")
        return redirect(url_for('review_list'))

# --------------------------------
# 로그인 / 로그아웃
# --------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['userid']
        user_pw = request.form['password']
        pw_hash=hashlib.sha256(user_pw.encode('utf-8')).hexdigest()

        if user_id == USER_ID and user_pw == USER_PW:
            session['logged_in'] = True
            session['user_id'] = user_id
            flash('로그인 성공!')
            return redirect(url_for('index'))
        elif DB.find_user(user_id, pw_hash):
            session['user_id'] = user_id
            session['logged_in']=True
            flash('로그인 성공!')
            return redirect(url_for('product_list'))
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.')
            return redirect(url_for('login'))
    else:
        return render_template('login.html', logged_in=session.get("logged_in", False))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --------------------------------
# 회원가입
# --------------------------------
#회원가입 페이지
@app.route('/signup')
def signup():
    return render_template('signup.html', logged_in=session.get("logged_in", False))

#회원가입 폼 제출
@app.route('/signup_post', methods=['POST'])
def register_user():
    id = request.form.get('text')
    pw = request.form.get('password')
    email = request.form.get('email')
    nickname = request.form.get('nickname')
    pw_hash=hashlib.sha256(pw.encode('utf-8')).hexdigest()

    data = {
        'id':id,
        'pw':pw,
        'email':email,
        'nickname':nickname
    }

    if not all([data["id"], data["email"], data["nickname"], pw]):
        flash("모든 항목을 입력해주세요.")
        return redirect('/signup')
    
    print("DEBUG form", dict(request.form))
    ok=DB.insert_user(data, pw_hash)
    print("DEBUG saved?", ok)

    if ok:
        flash("회원가입이 완료되었습니다. 로그인하십시오.")
        return redirect('/login')
    else:
        flash("이미 존재하는 아이디입니다.")
        return redirect('/signup')

# --------------------------------
# 실행
# --------------------------------
if __name__ == '__main__':
    print("📂 현재 실행 경로:", os.getcwd())
    app.run(debug=True)
