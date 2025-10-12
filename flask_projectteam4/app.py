from flask import Flask, render_template, redirect, url_for, session, request, flash

app = Flask(__name__)
app.secret_key = "ewhamarket_secret"

# 테스트용 임시 계정
USER_ID = "ewha"
USER_PW = "1234"

# --------------------------------
# 기본 페이지
# --------------------------------
@app.route('/')
def index():
    return render_template('index.html', logged_in=session.get("logged_in", False))

@app.route('/list')
def product_list():
    return render_template('product_list.html', logged_in=session.get("logged_in", False))

@app.route('/detail/<item>')
def product_detail(item):
    if item == "pen":
        return render_template('product_detail_pen.html', logged_in=session.get("logged_in", False))
    elif item == "madeline":
        return render_template('product_detail_madeline.html', logged_in=session.get("logged_in", False))
    elif item == "buds":
        return render_template('product_detail_buds.html', logged_in=session.get("logged_in", False))
    elif item == "jumper":
        return render_template('product_detail_jumper.html', logged_in=session.get("logged_in", False))
    else:
        return render_template('product_list.html', logged_in=session.get("logged_in", False))

@app.route('/register')
def product_register():
    return render_template('product_register.html', logged_in=session.get("logged_in", False))

# ✅ 새로 추가된 리뷰 목록 라우트
@app.route('/review/list')
def review_list():
    return render_template('review_list.html', logged_in=session.get("logged_in", False))

@app.route('/review/write')
def review_write():
    return render_template('review_write.html', logged_in=session.get("logged_in", False))

@app.route('/review/detail')
def review_detail():
    return render_template('review_detail.html', logged_in=session.get("logged_in", False))


# --------------------------------
# 로그인 / 로그아웃
# --------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['userid']
        user_pw = request.form['password']

        if user_id == USER_ID and user_pw == USER_PW:
            session['logged_in'] = True
            session['user_id'] = user_id
            flash('로그인 성공!')
            return redirect(url_for('index'))
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.')
            return redirect(url_for('login'))
    else:
        return render_template('login.html', logged_in=session.get("logged_in", False))

@app.route('/logout')
def logout():
    session.clear()
    flash('로그아웃 되었습니다.')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
