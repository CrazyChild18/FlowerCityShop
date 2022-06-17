from datetime import datetime
import os
from flask import Flask, render_template, url_for, redirect, flash, request, current_app
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from . import auth
from .. import db
from ..models import *
from ..email import send_email
from flask_babel import _


@auth.route('/unconfirmed')
def unconfirmed():
    return render_template('auth/unconfirmed.html')

# This method is used to update the last access time of the logged in user
@auth.before_app_request
def before_request():
    # 首先先判断该用户是否登录
    if current_user.is_authenticated:
        # 如果用户提供的登录凭据有效，调用models的ping()方法来刷新用户最后访问时间
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            # 如果用户提供的登录凭据无效，返回auth.login
            return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    if request.method == 'POST':
        # 获得前端数据
        email = request.form['email']
        password = request.form['password']
        user_in_db = User.query.filter(User.email == email).first()
        if not user_in_db:
            flash("Not found this email address, please register first.")
            return redirect(url_for('auth.login'))
        else:
            if check_password_hash(user_in_db.password, password):
                if user_in_db.isAdmin:
                    login_user(user_in_db, True)
                    next = request.args.get('next')
                    if next is None or not next.startswith('/'):
                        next = url_for('admin.admin_main_new')
                        # print('1')
                        return redirect(next)
                else:
                    login_user(user_in_db, True)
                    next = request.args.get('next')
                    if next is None or not next.startswith('/'):
                        next = url_for('main.home')
                        # print(2)
                    return redirect(next)
                # return redirect(url_for("main.home"))
            else:
                flash("Password not correct")
                return redirect(url_for('auth.login'))


@auth.route('/quick_login', methods=['GET', 'POST'])
def quick_login():
    email = request.form.get('email')
    password = request.form.get('password')
    user_in_db = User.query.filter(User.email == email).first()
    if not user_in_db:
        return "Not found this email address, please register first."
    else:
        if check_password_hash(user_in_db.password, password):
            login_user(user_in_db, True)
            return "success"
        else:
            return "Password not correct"


# 登出
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.home'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['pwd']
        password_confirm = request.form['pwdc']
        if password == password_confirm:
            user_in_db = User.query.filter(User.email == email).first()
            if not user_in_db:
                pass_hash = generate_password_hash(password)
                user_in_db = User(username=username, email=email, password=pass_hash)
                db.session.add(user_in_db)
                db.session.commit()

                admin = User.query.filter(User.isAdmin == True).all()
                for a in admin:
                    friend1 = Friends(sender=user_in_db.id, receiver=a.id)
                    friend2 = Friends(receiver=user_in_db.id, sender=a.id)
                    db.session.add(friend1)
                    db.session.add(friend2)
                db.session.commit()
                # 注册时发送邮箱认证
                token = user_in_db.generate_confirmation_token()
                send_email(user_in_db.email, 'Confirm Your Account',
                           'mail/confirm', user=user_in_db, token=token)
                flash('A confirmation email has been sent to you by email.', category='info')
                return redirect(url_for('auth.unconfirmed'))
            else:
                flash("This email is already registered, please Sign in or register using a different email address")
                return redirect(url_for('auth.register'))
        else:
            flash("This confirmed password is not the same as password")
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html')


# 确认邮箱（1）
# 注册之后 确认邮箱的路由（邮箱内部）
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.home'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.home'))


# 确认邮箱（2）
# 再次发送邮件
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'mail/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.home'))


# 重置密码（1）
# 忘记密码时，发送邮件。
@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'mail/reset_pwd',
                       user=user, token=token)
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html')


# 重置密码（2）
# 忘记密码发送的邮件里面，的修改密码的网页。
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        if User.reset_password(token, request.form['password']):
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.home'))
    return render_template('auth/reset_password_inEmail.html')


@auth.route('/myaccount', methods=['GET', 'POST'])
def myaccount():
    if request.method == 'GET':
        if current_user.is_authenticated:
            orders = Order.query.filter(Order.author == current_user).all()
            informations = Information.query.filter(Information.customer_id == current_user.id).all()
        return render_template('auth/my-account.html', orders=orders,
                               informations=informations, current_user=current_user)
    else:
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        country = request.form['country']
        job = request.form['job']
        file = request.files['file']
        if name is None or age is None or gender is None or country is None or job is None or file is None:
            flash("The item can not be empty!!")
            return redirect(url_for('auth.myaccount'))
        avatar_dir = Config.AVATAR_DIR
        avatar_filename = str(current_user.id) + 'AVATAR.jpg'
        file.save(os.path.join(avatar_dir, avatar_filename))
        current_user.name = name
        current_user.age = age
        current_user.gender = gender
        current_user.country = country
        current_user.job = job
        current_user.avatar = avatar_filename
        db.session.commit()
        return redirect(url_for('auth.myaccount'))


@auth.route('/buy/<money>', methods=['GET', 'POST'])
def buy(money):
    money = float(money)
    print("购买了", money)
    current_user.isVIP = True
    current_user.deposit += money
    db.session.commit()
    return redirect(url_for('auth.myaccount'))


@auth.route('/order_detail/<id>')
def order_detail(id):
    details = Order_Detail.query.filter(Order_Detail.order_id == id).all()
    order = Order.query.filter(Order.id == id).first()
    return render_template('auth/order_detail.html', isAdmin=False, items=details, total=order.total)


@auth.route('/view/<id>')
def view(id):
    return redirect(url_for('auth.order_detail', id=id))


@auth.route('/receipt', methods=['GET', 'POST'])
def receipt():
    order = Order.query.filter(Order.id == request.form.get('id')).first()
    order.finish = 2
    db.session.commit()
    return 'success'


@auth.route('/refund', methods=['GET', 'POST'])
def refund():
    order = Order.query.filter(Order.id == request.form.get('id')).first()
    order.finish = 3
    db.session.commit()
    return 'success'


@auth.route('/set_default', methods=['GET', 'POST'])
def set_default():
    information = Information.query.filter(Information.customer_id == current_user.id, Information.default == True).first()
    if information is not None:
        information.default = False
        db.session.commit()
    information2 = Information.query.filter(Information.id == request.form.get('id')).first()
    information2.default = True
    db.session.commit()
    return 'success'


@auth.route('/add_comment', methods=['GET', 'POST'])
def add_comment():

    grade = request.form.get('grade')
    content = request.form.get('content')
    id = request.form.get('id')
    order_detail = Order_Detail.query.filter(Order_Detail.id == id).first()
    order_detail.grade = int(grade)
    order_detail.content = content
    order_detail.time = datetime.now()
    db.session.commit()
    graded = 0.0
    grades = Order_Detail.query.filter(Order_Detail.item_id == order_detail.item_id).all()
    for g in grades:
        graded += g.grade
    grade = graded / len(grades)
    flower = Flower.query.filter(Flower.id == order_detail.item_id).first()
    flower.grade = grade
    print(flower.name)
    print(flower.grade)
    db.session.commit()
    return 'success'