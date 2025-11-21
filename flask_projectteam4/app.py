from flask import Flask, render_template, redirect, url_for, session, request, flash, jsonify
from database import DBhandler
import os
import hashlib

app = Flask(__name__)
app.secret_key = "ewhamarket_secret"

DB = DBhandler()

USER_ID = "ewha"
USER_PW = "1234"

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

@app.route('/')
def index():
    return render_template('index.html', logged_in=session.get("logged_in", False), nickname=session.get("nickname", ""))

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

    return render_template('product_register.html', logged_in=session.get("logged_in", False), nickname=session.get("nickname", ""))

@app.route('/list')
def product_list():
    data = DB.get_items()
    items = list(data.items())
    item_count = len(items)

    page = request.args.get("page", 0, type=int)
    per_page = 6
    per_row = 3

    start_idx = page * per_page
    end_idx = start_idx + per_page
    page_items = items[start_idx:end_idx]

    row1 = page_items[:per_row]
    row2 = page_items[per_row:per_page]
    page_count = (item_count - 1) // per_page + 1

    return render_template('product_list.html', row1=row1, row2=row2, total=item_count, page=page, page_count=page_count, logged_in=session.get("logged_in", False), nickname=session.get("nickname", ""))

@app.route('/product_detail/<name>/')
def view_item_detail(name):
    data = DB.get_item_byname(str(name))
    return render_template("product_detail.html", name=name, data=data, logged_in=session.get("logged_in", False), nickname=session.get("nickname", ""))
@app.route('/reg_review_init/<product_name>/')
def reg_review_init(product_name):
    recent = reviews[-3:][::-1]
    return render_template(
        'review_write.html',
        reviews=recent,
        logged_in=session.get("logged_in", False),
        nickname=session.get("nickname", ""),  # 작성자(로그인한 사람)
        product_name=product_name              # 상품명 (URL로 받은 거)
    )

@app.route('/show_heart/<name>/', methods=['GET'])
def show_heart(name):
    my_heart = DB.get_heart_byname(session['user_id'], name)
    return jsonify({'my_heart': my_heart})

@app.route('/like/<name>/', methods=['POST'])
def like(name):
    my_heart = DB.update_heart(session['user_id'], 'Y', name)
    return jsonify({'msg': '좋아요 완료!'})

@app.route('/unlike/<name>/', methods=['POST'])
def unlike(name):
    my_heart = DB.update_heart(session['user_id'], 'N', name)
    return jsonify({'msg': '좋아요 취소!'})

@app.route('/delete/<int:index>', methods=['POST'])
def delete_product(index):
    if 0 <= index < len(products):
        deleted_item = products.pop(index)
        flash(f"'{deleted_item['name']}' 상품이 삭제되었습니다.")
    else:
        flash("해당 상품을 찾을 수 없습니다.")
    return redirect(url_for('product_list'))

@app.route('/review')
@app.route('/review/write')
def review_main():
    recent = reviews[-3:][::-1]
    return render_template(
        'review_write.html',
        reviews=recent,
        logged_in=session.get("logged_in", False),
        nickname=session.get("nickname", ""),
        product_name=""
    )



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
    page = request.args.get("page", 0, type=int)  # 현재 페이지 번호
    per_page = 6  # 한 페이지에 보여줄 리뷰 개수

    total_reviews = len(reviews)
    # 최신순 정렬 후 페이지 슬라이싱
    sorted_reviews = reviews[::-1]
    start = page * per_page
    end = start + per_page
    paged_reviews = sorted_reviews[start:end]

    # 총 페이지 수 계산
    page_count = (total_reviews - 1) // per_page + 1 if total_reviews > 0 else 1

    return render_template(
        'review_list.html',
        reviews=paged_reviews,
        page=page,
        page_count=page_count,
        logged_in=session.get("logged_in", False),
        nickname=session.get("nickname", "")
    )

@app.route('/review/detail/<int:index>')
def review_detail(index):
    if 0 <= index < len(reviews):
        return render_template('review_detail.html', review=reviews[index], logged_in=session.get("logged_in", False), nickname=session.get("nickname", ""))
    flash("해당 리뷰를 찾을 수 없습니다.")
    return redirect(url_for('review_list'))

@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html", logged_in=session.get("logged_in", False))

@app.route("/signup_post", methods=["POST"])
def signup_post():
    user_id = request.form.get("id", "").strip()
    pw = request.form.get("pw", "").strip()
    email = request.form.get("email", "").strip()
    nickname = request.form.get("nickname", "").strip()

    if not all([user_id, pw, email, nickname]):
        flash("모든 항목을 입력해주세요.")
        return redirect(url_for("signup"))

    pw_hash = hashlib.sha256(pw.encode("utf-8")).hexdigest()

    data = {
        "id": user_id,
        "pw": pw_hash,
        "email": email,
        "nickname": nickname
    }

    ok = DB.insert_user(data, pw_hash)

    if ok:
        flash("회원가입이 완료되었습니다. 로그인해 주세요.")
        return redirect(url_for("login"))
    else:
        flash("이미 존재하는 아이디입니다.")
        return redirect(url_for("signup"))
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form.get("userid", "").strip()
        pw = request.form.get("password", "").strip()
        remember = request.form.get("remember")

        pw_hash = hashlib.sha256(pw.encode("utf-8")).hexdigest()
        user = DB.find_user(user_id, pw_hash)

        if user:  # user는 딕셔너리
            session["logged_in"] = True
            session["user_id"] = user_id
            session["nickname"] = user.get("nickname", "")
            if remember:
                session.permanent = True

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

    return render_template("login.html", logged_in=session.get("logged_in", False))

@app.route("/logout")
def logout():
    session.clear()
    flash("로그아웃 되었습니다.")
    return redirect(url_for("index"))

if __name__ == '__main__':
    print("현재 실행 경로:", os.getcwd())
    app.run(debug=True)
