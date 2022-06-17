import os
from datetime import datetime, timedelta
from operator import or_

from flask import render_template, url_for, redirect, flash, jsonify, json
from flask_login import current_user
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from . import admin
from ..models import *


@admin.route('/admin_main_new')
def admin_main_new():
    order_in_db = Order.query.filter(Order.finish == 0).all()
    users = User.query.filter(User.isAdmin == False).all()
    recent_visit_users = User.query.filter(User.isAdmin == False).order_by(User.last_seen.desc()).all()
    announcement_in_db = Announcement.query.filter(Announcement.time.like(datetime.now().strftime('%Y-%m-%d')+'%')).all()
    if announcement_in_db == []:
        title = 'No Schedule for today'
    else:
        title = announcement_in_db[0].title
    return render_template('admin_new/index.html', order_send=order_in_db, users=users, recent_visit_users=recent_visit_users, items=announcement_in_db, title=title)


@admin.route('/admin_product_new')
def admin_product_new():
    page1 = request.args.get('page', 1, type=int)
    item_in_db = Flower.query
    items = item_in_db.paginate(
        page1, per_page=10,
        error_out=False)
    flowers = items.items
    return render_template('admin_new/product-list-new.html', flowers=flowers, items=items)


@admin.route('/admin_order_new/<text>')
def admin_order_new(text):
    return render_template('admin_new/order-list-new.html', items=text)


@admin.route('/search_order', methods=['GET', 'POST'])
def search_order():
    datas = request.form.get('data')
    if datas == '%null%':
        data = ''
    else:
        data = datas
    item = '%' + data + '%'
    orders = Order.query.filter(or_(or_(Order.name.like(item), Order.id.like(item)), Order.time.like(item))).all()
    order_list = []
    for post in orders:
        order_list.append(post.to_json())
    return jsonify(order_list)


@admin.route('/admin-profile')
def admin_profile():
    return render_template('admin_new/pages-profile.html')


@admin.route('/admin-chat')
def admin_chat():
    return render_template('admin_new/chat.html')


@admin.route('/admin-announcement')
def admin_announcement():
    return render_template('admin_new/announcement.html')


@admin.route('/add_new', methods=['GET', 'POST'])
def add_new():
    if request.method == 'GET':
        return render_template('admin_new/add.html')
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        # print(item_name)
        item_pic = request.files.get('filesToUpload')
        # print(item_pic)
        item_intro = request.form.get('item_intro')
        item_describe = request.form.get('item_describe')
        # print(item_intro)
        item_price = request.form.get('item_price')
        # print(item_price)
        item_count = request.form.get('item_number')
        # print(item_count)
        item_color = request.form.get('item_color')
        # print(item_color)
        item_application = request.form.getlist('application')
        # print(item_application)
        item_type = request.form.get('item_style')
        # print(item_type)
        if item_name is None or item_pic is None or item_intro is None or item_price is None or item_count is None or item_type is None or item_application is None:
            flash("The item can not be empty!!")
            return redirect(url_for('admin.add_new'))
        application = ''
        for i in item_application:
            application = application + i + ', '
        avatar_dir = Config.AVATAR_UPLOAD_DIR
        avatar_filename = item_name + '_1.jpg'
        item_pic.save(os.path.join(avatar_dir, avatar_filename))
        flower = Flower(name=item_name, intro=item_intro, pic=avatar_filename, amount=item_count, detailed=item_describe, price=item_price, color=item_color, application=application, style=item_type)
        db.session.add(flower)
        db.session.commit()
        return redirect(url_for('admin.admin_product_new'))





# 以下为旧版，未改动
@admin.route('/admin_main')
def admin_main():
    return render_template('admin/admin_main.html')


@admin.route('/admin')
def shop():
    if request.method == 'GET':
        if current_user.is_authenticated:
            if current_user.isAdmin:
                page1 = request.args.get('page', 1, type=int)
                item_in_db = Flower.query
                items = item_in_db.paginate(
                    page1, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                    error_out=False)
                flowers = items.items
                return render_template('auth/admin.html', isAdmin=True, flowers=flowers, items=items)
            else:
                page1 = request.args.get('page', 1, type=int)
                item_in_db = Flower.query
                items = item_in_db.paginate(
                    page1, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                    error_out=False)
                flowers = items.items
                return render_template('auth/admin.html', isAdmin=False, flowers=flowers, items=items)
        else:
            return render_template('admin_main.html')
    if request.method == 'POST':
        return render_template('auth/admin.html')


@admin.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    flower_delete = Flower.query.filter(Flower.id == id).first()
    db.session.delete(flower_delete)
    db.session.commit()
    return redirect(url_for('admin.shop'))


@admin.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'GET':
        return render_template('auth/add.html')
    if request.method == 'POST':
        item_name = request.form['item_name']
        item_pic = request.files['item_pic']
        item_intro = request.form['item_intro']
        item_price = request.form['item_price']
        item_count = request.form['item_count']
        item_type = request.form['item_type']
        if item_name is None or item_pic is None or item_intro is None or item_price is None or item_count is None or item_type is None:
            flash("The item can not be empty!!")
            return redirect(url_for('admin.add_item'))
        avatar_dir = Config.AVATAR_UPLOAD_DIR
        avatar_filename = item_name + 'AVATAR.jpg'
        item_pic.save(os.path.join(avatar_dir, avatar_filename))
        flower = Flower(name=item_name, intro=item_intro, pic=avatar_filename, amount=item_count, price=item_price, style=item_type)
        db.session.add(flower)
        db.session.commit()
        return redirect(url_for('admin.product_list'))


@admin.route('/change/<id>', methods=['GET', 'POST'])
def change(id):
    if request.method == 'GET':
        flower_in_db = Flower.query.filter(Flower.id == id).first()
        return render_template('auth/change.html', flower=flower_in_db)
    else:
        item_name = request.form['item_name']
        item_pic = request.files['item_pic']
        item_intro = request.form['item_intro']
        item_price = request.form['item_price']
        item_count = request.form['item_count']
        item_type = request.form['item_type']
        avatar_dir = Config.AVATAR_UPLOAD_DIR
        avatar_filename = item_name + 'AVATAR.jpg'
        item_pic.save(os.path.join(avatar_dir, avatar_filename))
        flower_in_db = Flower.query.filter(Flower.id == id).first()
        db.session.delete(flower_in_db)
        db.session.commit()
        flower_change = Flower(name=item_name, intro=item_intro, pic=avatar_filename, amount=item_count, price=item_price, style=item_type)
        db.session.add(flower_change)
        db.session.commit()
        return redirect(url_for('admin.shop'))


@admin.route('/product_list')
def product_list():
    items = Flower.query.all()
    return render_template('/admin/pages/table/data.html', flowers=items)


@admin.route('/off_shelves', methods=['GET', 'POST'])
def off_shelves():
    flower = Flower.query.filter(Flower.id == request.form.get('id')).first()
    flower.on_sale = False
    db.session.commit()
    return 'success'


@admin.route('/on_shelves', methods=['GET', 'POST'])
def on_shelves():
    flower = Flower.query.filter(Flower.id == request.form.get('id')).first()
    flower.on_sale = True
    db.session.commit()
    return 'success'


@admin.route('/order_list')
def order_list():
    items = Order.query.all()
    return render_template('/admin/pages/table/order_table.html', items=items)


@admin.route('/send', methods=['GET', 'POST'])
def send():
    order = Order.query.filter(Order.id == request.form.get('id')).first()
    order.finish = 1
    db.session.commit()
    return 'success'


@admin.route('/refund', methods=['GET', 'POST'])
def refund():
    order = Order.query.filter(Order.id == request.form.get('id')).first()
    order.finish = 4
    db.session.commit()
    return 'success'


@admin.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('admin_new/register.html')
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['pwd']
        password_confirm = request.form['pwdc']
        if password == password_confirm:
            user_in_db = User.query.filter(User.email == email).first()
            if not user_in_db:
                pass_hash = generate_password_hash(password)
                user_in_db = User(username=username, email=email, password=pass_hash, isAdmin=True)
                user_in_db.confirmed = True
                db.session.add(user_in_db)
                db.session.commit()

                users = User.query.filter(User.isAdmin == True).all()
                for user in users:
                    friend1 = Friends(sender=user_in_db.id, receiver=user.id)
                    friend2 = Friends(receiver=user_in_db.id, sender=user.id)
                    db.session.add(friend1)
                    db.session.add(friend2)
                db.session.commit()
                return redirect(url_for('admin_new.admin_main_new'))
            else:
                flash("This email is already registered, please Sign in or register using a different email address")
                return redirect(url_for('admin.register'))


@admin.route('/chat', methods=['GET', 'POST'])
def chat():
    return render_template('admin/chat.html')


@admin.route('/change_price', methods=['GET', 'POST'])
def change_price():
    id = request.form.get('id')
    price = request.form.get('price')
    flower = Flower.query.filter(Flower.id == id).first()
    flower.price = price
    db.session.commit()
    return 'success'


@admin.route('/change_amount', methods=['GET', 'POST'])
def change_amount():
    id = request.form.get('id')
    amount = request.form.get('amount')
    flower = Flower.query.filter(Flower.id == id).first()
    flower.amount = amount
    db.session.commit()
    return 'success'


@admin.route('/this_week', methods=['GET', 'POST'])
def this_week():
    date_list = []
    sale_list = []
    today = datetime.utcnow()
    i = 6
    while i >= 0:
        delta = timedelta(days=i)
        n_days = today - delta
        date = n_days.strftime('%Y-%m-%d')
        today_orders = Order.query.filter(Order.time.like(date+'%')).all()
        today_sale = 0
        for order in today_orders:
            today_sale += order.total
        i -= 1
        date_list.append(date)
        sale_list.append(today_sale)
    date_dic = {'date_list': date_list, 'sale_list': sale_list}
    return jsonify(date_dic)


@admin.route('/up_to_now_pie', methods=['GET', 'POST'])
def up_to_now_pie():
    flower_list = []
    number_list = []
    items = db.session.query(Order_Detail.item_id, func.sum(Order_Detail.number).label('total_number')).order_by('total_number').group_by('item_id').all()
    datas = [dict(zip(item.keys(), item)) for item in items]
    for data in datas:
        if data['item_id'] is not None:
            flower = Flower.query.filter(Flower.id == data['item_id']).first()
            if flower.on_sale == True:
                flower_list.append(flower.name)
                number_list.append(data['total_number'])
    dic = {'flower_list': flower_list, 'number_list': number_list}
    return jsonify(dic)


@admin.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    name = request.form.get('name')
    phone = request.form.get('phone')
    country = request.form.get('country')
    password = request.form.get('name')
    if name != '' and name != current_user.name:
        current_user.name = name
    if phone != '' and phone != current_user.phone:
        current_user.phone = phone
    if country != '' and country != current_user.country:
        current_user.country = country
    if password != '' and check_password_hash(current_user.password, password):
        current_user.password = generate_password_hash(password)
    db.session.commit()
    return 'success'


@admin.route('/delete_product', methods=['GET', 'POST'])
def delete_product():
    flower = Flower.query.filter(Flower.id == request.form.get('id')).first()
    db.session.delete(flower)
    db.session.commit()
    return 'success'


@admin.route('/multiple_delete_product', methods=['GET', 'POST'])
def multiple_delete_product():
    product_list = request.form.get('id')
    json.loads(product_list)
    for id in product_list:
        if id != '[' and id != '"' and id!= ']' and id != ',':
            flower = Flower.query.filter(Flower.id == int(id)).first()
            db.session.delete(flower)
            db.session.commit()
    return 'success'


@admin.route('/add_announcement', methods=['GET', 'POST'])
def add_announcement():
    lists = request.form.get('list')
    title = request.form.get('title')
    json.loads(lists)
    str = ''
    for i in lists:
        if i != '^':
            str = str + i
        else:
            if str == '["' or str == '","':
                str = ''
            else:
                announcement = Announcement(title=title, content=str, time=datetime.now())
                db.session.add(announcement)
                str = ''
    db.session.commit()
    return 'success'
