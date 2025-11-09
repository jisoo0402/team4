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

        image_filename = "default.png"
        if image and image.filename:
            image_filename = image.filename
            save_dir = os.path.join('static', 'image')
            os.makedirs(save_dir, exist_ok=True)
            image.save(os.path.join(save_dir, image_filename))

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

# 상품 목록
@app.route('/list')
def product_list():
    return render_template('product_list.html', products=products, logged_in=session.get("logged_in", False))

# 상품 삭제
@app.route('/delete/<int:index>', methods=['POST'])
def delete_product(index):
    if 0 <= index < len(products):
        deleted_item = products.pop(index)
        print(f"[상품 삭제됨] {deleted_item['name']}")
        flash(f"'{deleted_item['name']}' 상품이 삭제되었습니다.")
    else:
        flash("해당 상품을 찾을 수 없습니다.")
    return redirect(url_for('product_list'))

# 고정 상세(정적 템플릿 사용)
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

# 동적 상세(등록 상품용, 이름으로 매칭)
@app.route('/detail/<item>')
def product_detail(item):
    # 먼저 고정 상품 키워드는 위 정적 라우트로 처리되므로 여기서는 등록상품만 탐색
    for p in products:
        if p["name"] == item:
            return render_template('product_detail.html', product=p, logged_in=session.get("logged_in", False))
    flash("해당 상품을 찾을 수 없습니다.")
    return redirect(url_for('product_list'))

# --------------------------------
# 리뷰
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
    if image and image.filename:
        image_filename = image.filename
        save_dir = os.path.join('static', 'image')
        os.makedirs(save_dir, exist_ok=True)
        image.save(os.path.join(save_dir, image_filename))

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
        return render_template('review_detail.html', review=reviews[index], logged_in=session.get("logged_in", False))
    flash("해당 리뷰를 찾을 수 없습니다.")
    return redirect(url_for('review_list'))

# --------------------------------
# 회원가입
# --------------------------------
@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html", logged_in=session.get("logged_in", False))

@app.route("/signup_post", methods=["POST"])
def signup_post():
    user_id = request.form.get("id","").strip()
    pw = request.form.get("pw","").strip()
    nickname = request.form.get("nickname","").strip()

    if not user_id or not pw or not nickname:
        flash("필수 항목을 모두 입력하세요.")
        return redirect(url_for("signup"))

    pw_hash = hashlib.sha256(pw.encode("utf-8")).hexdigest()
    print(f"[회원가입] id={user_id}, nickname={nickname}, pw_hash={pw_hash[:10]}...")

    flash("회원가입 완료! 로그인해주세요.")
    return redirect(url_for("login"))

# --------------------------------
# 로그인 / 로그아웃
# --------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('userid', '')
        user_pw = request.form.get('password', '')

        if user_id == USER_ID and user_pw == USER_PW:
            session['logged_in'] = True
            session['user_id'] = user_id
            return """
                <script>
                  alert('로그인 성공! 환영합니다 🌿');
                  window.location.href = '/';
                </script>
            """
        else:
            return """
                <script>
                  alert('아이디 또는 비밀번호가 올바르지 않습니다.');
                  window.location.href = '/login';
                </script>
            """
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
    print("현재 실행 경로:", os.getcwd())
    app.run(debug=True)
