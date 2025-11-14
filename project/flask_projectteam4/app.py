from base64 import encode
from flask import Flask, render_template, redirect, url_for, session, request, flash
from database import DBhandler
import os
import hashlib

app = Flask(__name__)
app.secret_key = "ewhamarket_secret"

DB = DBhandler()

#MASTER ACCOUNT
USER_ID = "ewha"
USER_PW = "1234"

products = []
reviews = []

# --------------------------------
# 홈
# --------------------------------
@app.route('/')
def index():
    # return render_template('index.html', logged_in=session.get("logged_in", False))
    return redirect(url_for('product_list'))

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
# 2x3 보여주기
@app.route('/list')
def product_list():
    page = request.args.get("page", 0, type=int)
    per_page = 6
    per_row = 3

    # DB에서 상품 전체 가져오기
    data = DB.get_items()  # dict
    items = list(data.items())  # 리스트로 변환 ([(key, value), ...])

    item_count = len(items)

    # 페이지 범위 슬라이싱
    start_idx = page * per_page
    end_idx = start_idx + per_page
    page_items = items[start_idx:end_idx]  # 현재 페이지의 item 리스트

    # 2줄로 나누기
    row1 = page_items[:per_row]
    row2 = page_items[per_row:per_page]

    # 페이지 수 계산
    page_count = (item_count - 1) // per_page + 1

    return render_template(
        'product_list.html',
        row1=row1,
        row2=row2,
        total=item_count,
        page=page,
        page_count=page_count
    )


# @app.route('/list')
# def product_list():
#     page = request.args.get("page",0, type=int)
#     per_page = 6
#     per_row = 3
#     row_count = int(per_page/per_row)
#     start_idx = per_page*page
#     end_idx = per_page*(page+1)
#     data = DB.get_items()
#     item_counts = len(data)
#     data = dict(list(data.items())[start_idx:end_idx])
#     tot_count = len(data)
#     for i in range(row_count):
#         if(i==row_count-1)and (tot_count%per_row!=0):
#             locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
#         else:
#             locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])                
#     return render_template('product_list.html', datas=data.items(), row1=locals()['data_0'].items(), 
#                            row2=locals()['data_1'].items(),limit=per_page, page=page, 
#                            page_count=int((item_counts/per_page)+1),total=item_counts)

#동적라우팅
@app.route('/dynamicurl/<varible_name>/')
def DynamicUrl(varible_name):
    return str(varible_name)

@app.route('/product_detail/<name>/')
def view_item_detail(name):
    print("###name: ", name)
    data = DB.get_item_byname(str(name))
    print("###data: ", data)
    return render_template("product_detail.html", name=name, data=data)





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




# 리뷰
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
# @app.route("/signup", methods=["GET"])
# def signup():
#     return render_template("signup.html", logged_in=session.get("logged_in", False))

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


