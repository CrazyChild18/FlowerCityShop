import datetime
import os
import time
from operator import or_

from flask import render_template, request, current_app, url_for, redirect, flash, json, jsonify
from flask_login import current_user, login_required

from config import Config
from . import main
from ..models import *
from flask_babel import _


@main.route('/')
@main.route('/index')
def home():
    if request.method == 'GET':
        flower_in_db_new = Flower.query.filter(Flower.on_sale == True).order_by(Flower.time_in.desc()).limit(5)
        flower_in_db_best = Flower.query.filter(Flower.on_sale == True).order_by(Flower.grade.desc()).limit(5)
        flower_in_db_feature = Flower.query.filter(Flower.on_sale == True).limit(5)
        if current_user.is_authenticated:
            flower_in_cart = Cart.query.filter(Cart.cart_user == current_user).all()
            number = 0
            for flower in flower_in_cart:
                number = number + flower.flower_cart.price * flower.number
        if current_user.is_authenticated:
            if current_user.isAdmin:
                return render_template('index.html', isAdmin=True, flower_new=flower_in_db_new, flower_best=flower_in_db_best, flower_feature=flower_in_db_feature)
            else:
                return render_template('index.html', isAdmin=False, flower_new=flower_in_db_new, flower_best=flower_in_db_best, flower_feature=flower_in_db_feature, flower_in_cart=flower_in_cart, number=number)
        else:
            return render_template('index.html', flower_new=flower_in_db_new, flower_best=flower_in_db_best, flower_feature=flower_in_db_feature)
    elif request.method == 'POST':
        return render_template('index.html')


@main.route('/cart')
def cart():
    if current_user.is_authenticated:
        if current_user.isAdmin:
            return render_template('cart.html', isAdmin=True)
        else:
            item = Cart.query.filter(Cart.customer_id == current_user.id).all()
            total = 0
            for flower in item:
                total = total + flower.flower_cart.price * flower.number
            return render_template('cart.html', isAdmin=False, items=item, total=total)
    else:
        return render_template('cart.html')



@main.route('/wishlist')
def wishlist():
    if request.method == 'GET':
        if current_user.is_authenticated:
            flower_in_cart = Cart.query.filter(Cart.cart_user == current_user).all()
            number = 0
            for flower in flower_in_cart:
                number = number + flower.flower_cart.price * flower.number

            wishes = Wishlist.query.filter(Wishlist.customer_id == current_user.id).all()
            if current_user.isAdmin:
                return render_template('wishlist.html', isAdmin=True)
            else:
                return render_template('wishlist.html', isAdmin=False, flower_in_cart=flower_in_cart, number=number, wishes=wishes)
        else:
            return render_template('wishlist.html')
    elif request.method == 'POST':
        return render_template('wishlist.html')


@main.route('/about')
def about():
    if request.method == 'GET':
        if current_user.is_authenticated:
            if current_user.isAdmin:
                return render_template('about.html', isAdmin=True)
            else:
                return render_template('about.html', isAdmin=False)
        else:
            return render_template('about.html')
    elif request.method == 'POST':
        return render_template('about.html')


@main.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'GET':
        flower_in_cart = Cart.query.filter(Cart.cart_user == current_user).all()
        number = 0
        for flower in flower_in_cart:
            number = number + flower.flower_cart.price * flower.number
        if current_user.isVIP:
            number *= 0.9
        if current_user.isAdmin:
            return render_template('checkout.html', isAdmin=True, deposit=current_user.deposit)
        else:
            return render_template('checkout.html', isAdmin=False, number=number, items=flower_in_cart,
                                   deposit=current_user.deposit)


@main.route('/checkout2', methods=['GET', 'POST'])
def checkout2():
    if request.method == 'GET':
        buy_direct = Buy.query.filter(Buy.customer_id == current_user.id).first()
        flower = Flower.query.filter(Flower.id == buy_direct.item_id).first()
        number = buy_direct.number * flower.price
        if current_user.isVIP:
            number *= 0.9
        if current_user.isAdmin:
            return render_template('checkout_buy.html', isAdmin=True, deposit=current_user.deposit)
        else:
            return render_template('checkout_buy.html', isAdmin=False, number=buy_direct.number,
                                   item=flower, total=number, deposit=current_user.deposit)


@main.route('/payment', methods=['GET', 'POST'])
def payment():
    total = float(request.args.get("total"))
    current_user.deposit -= total
    db.session.commit()
    return 'success'


@main.route('/buy_direct', methods=['GET', 'POST'])
def buy_direct():
    id = request.form.get('id')
    number = request.form.get('number')
    buy = Buy.query.filter(Buy.customer_id == current_user.id).first()
    if buy is None:
        buy_direct = Buy(item_id=id, number=number, customer_id=current_user.id)
        db.session.add(buy_direct)
    else:
        buy.item_id = id
        buy.number = number
    db.session.commit()
    return 'success'


@main.route('/product_detail/<id>', methods=['GET', 'POST'])
def product_detail(id):
    if request.method == 'GET':
        flower_in_db = Flower.query.filter(Flower.id == id).first()
        style = flower_in_db.style
        flower_relative = Flower.query.filter(Flower.style == style).limit(5)
        comments = Order_Detail.query.filter(Order_Detail.item_id == id).all()
        if current_user.is_authenticated:
            wishlist = Wishlist.query.filter(Wishlist.item_id == id, Wishlist.customer_id == current_user.id).first()
            flower_in_cart = Cart.query.filter(Cart.cart_user == current_user).all()
            number = 0
            in_wishlist = False
            if wishlist is not None:
                in_wishlist = True
            for flower in flower_in_cart:
                number = number + flower.flower_cart.price * flower.number
            if current_user.isAdmin:
                return render_template('shop-single-variable.html', id=id, isAdmin=True, flower_in_db=flower_in_db, flower_relative=flower_relative, quantity=1, comments=comments)
            else:
                return render_template('shop-single-variable.html', id=id, isAdmin=False, flower_in_db=flower_in_db, flower_relative=flower_relative, quantity=1, number=number, flower_in_cart=flower_in_cart, in_wishlist=in_wishlist, comments=comments)
        else:
            return render_template('shop-single-variable.html', id=id, flower_in_db=flower_in_db, flower_relative=flower_relative, quantity=1, in_wishlist=False , comments=comments)
    elif request.method == 'POST':
        return render_template('shop-single-variable.html', id=id, quantity=1)


@main.route('/delete_cart/<id>')
def delete_cart(id):
    flower_delete = Cart.query.filter(Cart.item_id == id, Cart.customer_id == current_user.id).first()
    db.session.delete(flower_delete)
    db.session.commit()
    return redirect(url_for('main.cart'))


@main.route('/list_add_cart/<id>')
def list_add_cart(id):
    str = id.split('%%')
    id = str[0]
    text = str[1]
    cart = Cart.query.filter(Cart.customer_id == current_user.id, Cart.item_id == id).first()
    if cart is not None:
        cart.number = cart.number + 1
        db.session.commit()
    else:
        item_in_cart = Cart(number=1, item_id=id, customer_id=current_user.id)
        db.session.add(item_in_cart)
        db.session.commit()
    return redirect(url_for('main.shop_list_new', text=text))


@main.route('/detail_add_cart', methods=['GET', "POST"])
def detail_add_cart():
    id = request.form.get('id')
    number = request.form.get('quantity')
    cart = Cart.query.filter(Cart.customer_id == current_user.id, Cart.item_id == id).first()
    if cart is not None:
        cart.number = cart.number + int(number)
        db.session.commit()
    else:
        item_in_cart = Cart(number=number, item_id=id, customer_id=current_user.id)
        db.session.add(item_in_cart)
        db.session.commit()
    return 'success'


@main.route('/test2', methods=['GET', "POST"])
def test2():
    quantity = request.form.get('quantity')
    name = request.form.get('name').strip()
    flower = Flower.query.filter(Flower.name == name).first()
    cart = Cart.query.filter(Cart.item_id == flower.id, Cart.customer_id == current_user.id).first()
    cart.number = int(quantity)
    db.session.commit()
    # test = request.form.get('target')
    return '11'


@main.route('/list_add_wishlist/<id>')
def list_add_wishlist(id):
    str = id.split('%%')
    id = str[0]
    text = str[1]
    wishlist = Wishlist.query.filter(Wishlist.customer_id == current_user.id, Wishlist.item_id == id).first()
    if wishlist is not None:
        flash("You have added this to your wish list before!")
        return redirect(url_for('main.shop_list_new', text=text))
    else:
        flower = Flower.query.filter(Flower.id == id).first()
        item_in_wishlist = Wishlist(price_in=flower.price, item_id=id, customer_id=current_user.id)
        db.session.add(item_in_wishlist)
        db.session.commit()
        return redirect(url_for('main.shop_list_new', text=text))


@main.route('/detail_add_wishlist', methods=['GET', "POST"])
def detail_add_wishlist():
    id = request.form.get('id')
    wishlist = Wishlist.query.filter(Wishlist.customer_id == current_user.id, Wishlist.item_id == id).first()
    if wishlist is not None:
        flash("You have added this to your wish list before!")
        return ''
    else:
        flower = Flower.query.filter(Flower.id == id).first()
        item_in_wishlist = Wishlist(price_in=flower.price, item_id=id, customer_id=current_user.id)
        db.session.add(item_in_wishlist)
        db.session.commit()
        return ''


@main.route('/delete_wishlist/<id>')
def delete_wishlist(id):
    flower_delete = Wishlist.query.filter(Wishlist.item_id == id, Wishlist.customer_id == current_user.id).first()
    db.session.delete(flower_delete)
    db.session.commit()
    return redirect(url_for('main.wishlist'))


@main.route('/check')
def check():
    return redirect(url_for('main.checkout'))


@main.route('/shop_list_new/<text>')
def shop_list_new(text):
    if request.method == 'GET':
        if current_user.is_authenticated:
            flower_in_cart = Cart.query.filter(Cart.cart_user == current_user).all()
            number = 0
            for flower in flower_in_cart:
                number = number + flower.flower_cart.price * flower.number
            if current_user.isAdmin:
                return render_template('shop-grid-left-sidebar.html', isAdmin=True, items=text)
            else:
                return render_template('shop-grid-left-sidebar.html', isAdmin=False, flower_in_cart=flower_in_cart, items=text, number=number)
        else:
            return render_template('shop-grid-left-sidebar.html', items=text)


@main.route('/detail_delete_wishlist/<id>')
def detail_delete_wishlist(id):
    flower_delete = Wishlist.query.filter(Wishlist.item_id == id, Wishlist.customer_id == current_user.id).first()
    db.session.delete(flower_delete)
    db.session.commit()
    return redirect(url_for('main.product_detail', id=id))


@main.route('/list_delete_wishlist/<id>')
def list_delete_wishlist(id):
    flower_delete = Wishlist.query.filter(Wishlist.item_id == id, Wishlist.customer_id == current_user.id).first()
    db.session.delete(flower_delete)
    db.session.commit()
    return redirect(url_for('main.shop_list', id=id))


@main.route('/buy', methods=['GET', "POST"])
def buy():
    carts = Cart.query.filter(Cart.customer_id == current_user.id).all()
    name = request.form.get('name')
    nation = request.form.get('nation')
    city = request.form.get('city')
    phone = request.form.get('phone')
    address = request.form.get('address')
    total = request.form.get('total')
    information = Information.query.filter(Information.name == name, Information.phone == phone, Information.nation == nation, Information.city == city, Information.address == address, Information.customer_id == current_user.id).first()
    names = ''
    for cart in carts:
        names += cart.flower_cart.name + ', '
        if len(names) >= 15:
            names += '...'
            break

    if information is None:
        infor = Information(name=name, nation=nation, phone=phone, address=address, city=city, customer_id=current_user.id)
        db.session.add(infor)
    order = Order(customer_id=current_user.id, total=total, name=names)
    db.session.add(order)
    db.session.commit()
    for cart in carts:
        item = Order_Detail(number=cart.number, item_id=cart.item_id, order_id=order.id)
        flower = Flower.query.filter(Flower.id == cart.item_id).first()
        flower.amount -= cart.number
        db.session.delete(cart)
        db.session.add(item)
    db.session.commit()
    return "success"


@main.route('/buy2', methods=['GET', "POST"])
def buy2():
    buy_direct = Buy.query.filter(Buy.customer_id == current_user.id).first()
    flower = Flower.query.filter(Flower.id == buy_direct.item_id).first()
    name = request.form.get('name')
    nation = request.form.get('nation')
    city = request.form.get('city')
    phone = request.form.get('phone')
    address = request.form.get('address')
    total = request.form.get('total')
    information = Information.query.filter(Information.name == name, Information.phone == phone, Information.nation == nation, Information.city == city, Information.address == address, Information.customer_id == current_user.id).first()
    names = flower.name
    if information is None:
        infor = Information(name=name, nation=nation, phone=phone, address=address, city=city, customer_id=current_user.id)
        db.session.add(infor)
    order = Order(customer_id=current_user.id, total=total, name=names)
    db.session.add(order)
    db.session.commit()
    item = Order_Detail(number=buy_direct.number, item_id=buy_direct.item_id, order_id=order.id)
    db.session.delete(buy_direct)
    db.session.add(item)
    flower = Flower.query.filter(Flower.id == buy_direct.item_id).first()
    flower.amount -= buy_direct.number
    db.session.commit()
    return "success"


@main.route('/information', methods=['GET', 'POST'])
def information():
    information = Information.query.filter(Information.customer_id == current_user.id, Information.default == True).first()
    if information is not None:
        return jsonify(information.to_json())
    else:
        return 'none'



@main.route('/hit', methods=['GET', 'POST'])
def hit():
    id = request.form.get('id')
    flower = Flower.query.filter(Flower.id == id).first()
    flower.hit_number += 1
    db.session.commit()
    return ''


@main.route('/quick_view_add_cart', methods=['GET', 'POST'])
def quick_view_add_cart():
    id = request.form.get('id')
    number = int(request.form.get('number'))
    cart = Cart.query.filter(Cart.item_id == id).first()
    if cart is not None:
        cart.number += number
    else:
        new_cart = Cart(number=number, item_id=id, customer_id=current_user.id)
        db.session.add(new_cart)
    db.session.commit()
    return 'success'



#客服系统
# ajax 长轮询定时查询chat list的状态
@main.route('/refreshChatList', methods=['POST', 'GET'])
def test():
    start = time.time()
    end = time.time()
    interval = end - start
    while interval < 20:
        target = Friends.query.filter(Friends.receiver == current_user.id, Friends.status == 1).first()
        if target is not None:
            return '1'
        time.sleep(10)
        end = time.time()
        interval = end - start
    return '0'


@main.route('/chat', methods=['POST', 'GET'])
def chat():
    return render_template('admin/chat.html', user=current_user.username)


# status 为1 则说明sender 向 receiver 发送了消息且未被读
@main.route('/getChatList', methods=['POST', 'GET'])
def getChatList():
    lists = Friends.query.filter(Friends.receiver == current_user.id).order_by(Friends.status.desc()).all()
    chatList = []
    for list in lists:
        user = User.query.filter(User.id == list.sender).first()
        senderInfo = SenderInfo(uid=user.id, name=user.username, status=list.status)
        chatList.append(senderInfo.to_json())
    return jsonify(chatList)


@main.route('/getChatMessage', methods=['POST', 'GET'])
def getChatMessage():
    u = current_user.id
    r = request.form.get('person')
    # 得到u和r之间的消息传递记录同时将status标记为0 即消息已读
    record = Friends.query.filter(Friends.receiver==u,Friends.sender==r).first()
    record.status=0
    db.session.commit()
    # 得到他们之间的消息
    messageList  = []
    # 得到u 和 r 直接发送的消息
    messages = Message.query.filter(Message.receiver == u, Message.sender == r).order_by(Message.system_time).all()
    message2 = Message.query.filter(Message.receiver == r, Message.sender == u).order_by(Message.system_time).all()
    for message in messages:
        sender = message.sender
        sender = User.query.filter(User.id == sender).first().username
        receiver = message.receiver
        receiver = User.query.filter(User.id == receiver).first().username
        chatMessage = ChatMessage(msg_id=message.msg_id, sender=sender, receiver=receiver,
                                  system_time=message.system_time, message=message.message)
        messageList.append(chatMessage.to_json())

    for message in message2:
        sender = message.sender
        sender = User.query.filter(User.id == sender).first().username
        receiver = message.receiver
        receiver = User.query.filter(User.id == receiver).first().username
        chatMessage = ChatMessage(msg_id=message.msg_id,sender=sender,receiver=receiver,
                                  system_time=message.system_time,message=message.message)
        messageList.append(chatMessage.to_json())
    # 根据时间排序
    messageList.sort(key=lambda s:s['system_time'])
    # for message in messageList:
    #     print(message)
    return jsonify(messageList)


# status为1 表示sender 对 receiver 发送消息且没被读取
@main.route('/storeMessage', methods=['POST', 'GET'])
def storeMessage():
    sender = current_user.id
    receiver = request.form.get('uid')
    text = request.form.get('text')
    time = datetime.now()
    time = time.strftime('%Y-%m-%d %H:%M:%S')
    message = Message(sender=sender, receiver=receiver, message=text, system_time=time)
    friendRecord = Friends.query.filter(Friends.sender == sender, Friends.receiver == receiver).first()
    friendRecord.status = 1
    db.session.add(message)
    db.session.commit()

    return jsonify(time)

#客服系统



# Blog
@main.route('/blog')
def blog():
    posts = Blog.query.limit(5).all()
    latest_posts = Blog.query.filter().order_by(Blog.time.desc()).limit(4)
    dic = {}
    i = 0
    for post in posts:
        pics = BlogPic.query.filter(BlogPic.blog_id == post.id).all()
        pic_list = []
        for pic in pics:
            pic_list.append(pic.pic)
        dic[post.title] = pic_list
        i = i + 1
    post1 = posts[0]
    posts.remove(post1)
    return render_template('blog/index.html', post1=post1, posts=posts, latest_posts=latest_posts)


@main.route('/blog-about')
def blog_aboutme():
    posts = Blog.query.filter(Blog.post_user == current_user.id).order_by(Blog.time.desc()).all()
    return render_template('blog/03-About-me.html', posts=posts)


@main.route('/blog-detail/<id>')
def blog_detail(id):
    post = Blog.query.filter(Blog.id == id).first()
    post_pics = BlogPic.query.filter(BlogPic.blog_id == post.id).all()
    author = User.query.filter(User.id == post.post_user).first()
    latest_posts = Blog.query.filter().order_by(Blog.time.desc()).limit(4)
    comments = BlogComment.query.filter(BlogComment.comment_post == id).order_by(BlogComment.time.desc()).all()
    return render_template('blog/02-Single-post.html', post=post, post_pics=post_pics, author=author, latest_posts=latest_posts, id=id, comments=comments)


@main.route('/blog-add', methods=['GET', 'POST'])
def blog_add():
    if request.method == 'POST':
        user_post = current_user.id
        title = request.form.get('title')
        describe = request.form.get('type')
        content = request.form.get('describe')
        blog_pic = request.files.getlist('filesToUpload')
        if title is None or describe is None or content is None:
            flash("The item can not be empty!!")
            return redirect(url_for('main.blog_add'))
        blog = Blog(title=title, describe=describe, content=content, time=datetime.now(), post_user=user_post)
        db.session.add(blog)
        db.session.commit()

        avatar_dir = Config.BLOG_DIR
        i = 0
        for file in blog_pic:
            filename = title + str(i) + ".jpg"
            upload_path = os.path.join(avatar_dir, filename)
            file.save(upload_path)
            blog_p = BlogPic(pic=filename, blog_id=blog.id)
            db.session.add(blog_p)
            i = i + 1
        db.session.commit()
        return redirect(url_for('main.blog_aboutme'))
    return render_template('blog/Add-post.html')


@main.route('/blog-list/<text>', methods=['GET', 'POST'])
def blog_list(text):
    latest_posts = Blog.query.filter().order_by(Blog.time.desc()).limit(4)
    return render_template('blog/blog_list.html', items=text, latest_posts=latest_posts)


@main.route('/comment/<id>', methods=['GET', 'POST'])
def comment(id):
    content = request.form.get('comment')
    comment = BlogComment(comment=content, comment_user=current_user.id, comment_post=id)
    db.session.add(comment)
    db.session.commit()
    return "success"


@main.route('/blog-interest', methods=['GET', 'POST'])
def blog_interest():
    return render_template('blog/interest_blog.html')


@main.route('/interest_post', methods=['GET', 'POST'])
def interest_post():
    likes = Like.query.filter(Like.liker_id == current_user.id).all()
    post_list = []
    for like in likes:
        post = Blog.query.filter(Blog.id == like.liked_post_id).first()
        post_list.append(post.to_json())
    return jsonify(post_list)


@main.route('/search_post', methods=['GET', 'POST'])
def search_post():
    datas = request.form.get('data')
    if datas == '%null%':
        data = ''
    else:
        data = datas
    item = '%' + data + '%'
    posts = Blog.query.filter(or_(or_(or_(Blog.title.like(item), Blog.content.like(item)), Blog.describe.like(item)), Blog.time.like(item))).all()
    post_list = []
    for post in posts:
        post_list.append(post.to_json())
    return jsonify(post_list)


@main.route('/like/<post_id>')
@login_required
def like(post_id):
    post = Blog.query.filter_by(id=post_id).first()
    if post is None:
        flash('Invalid post.')
        return redirect(url_for('.blog'))
    if current_user.is_liking(post):
        flash('You are already liking this post.')
        return redirect(url_for('.blog'))
    current_user.like(post)
    post.like(current_user)
    post.recent_activity = datetime.utcnow()
    db.session.commit()
    flash('You are now liking this post')
    return redirect(url_for('.blog'))


@main.route('/like_in_post/<post_id>')
@login_required
def like_in_post(post_id):
    post = Blog.query.filter_by(id=post_id).first()
    if post is None:
        flash('Invalid post.')
        return redirect(url_for('.blog_detail', id=post_id))
    if current_user.is_liking(post):
        flash('You are already liking this post.')
        return redirect(url_for('.blog_detail', id=post_id))
    current_user.like(post)
    post.like(current_user)
    db.session.commit()
    flash('You are now liking this post')
    return redirect(url_for('.blog_detail', id=post_id))


@main.route('/dislike/<post_id>')
@login_required
def dislike(post_id):
    post = Blog.query.filter_by(id=post_id).first()
    if post is None:
        flash('Invalid post.')
        return redirect(url_for('.blog'))
    if not current_user.is_liking(post):
        flash('You are not liking this post.')
        return redirect(url_for('.blog'))
    current_user.dislike(post)
    post.dislike(current_user)
    db.session.commit()
    flash('You are not liking this post')
    return redirect(url_for('.blog'))


@main.route('/dislike_in_post/<post_id>')
@login_required
def dislike_in_post(post_id):
    post = Blog.query.filter_by(id=post_id).first()
    if post is None:
        flash('Invalid post.')
        return redirect(url_for('.blog_detail', id=post_id))
    if not current_user.is_liking(post):
        flash('You are not liking this post.')
        return redirect(url_for('.blog_detail', id=post_id))
    current_user.dislike(post)
    post.dislike(current_user)
    db.session.commit()
    flash('You are not liking this post')
    return redirect(url_for('.blog_detail', id=post_id))


@main.route('/collection-card')
def collection_card():
    if request.method == 'GET':
        page1 = request.args.get('page', 1, type=int)
        item_in_db = Flower.query
        items = item_in_db.paginate(
            page1, per_page=8,
            error_out=False)
        flowers = items.items
        if current_user.is_authenticated:
            # 查询用户已经购买的flower
            orders = Order.query.filter(Order.customer_id == current_user.id).all()
            flowers_buy = []
            for order in orders:
                flowers_order = Order_Detail.query.filter(Order_Detail.order_id == order.id).all()
                for flower in flowers_order:
                    flowers_buy.append(flower.flower_order_detail)
            # 购物车中的花
            flower_in_cart = Cart.query.filter(Cart.cart_user == current_user).all()
            number = 0
            for flower in flower_in_cart:
                number = number + flower.flower_cart.price * flower.number

            if current_user.isAdmin:
                return render_template('collection_card.html', flowers=flowers, items=items, isAdmin=True)
            else:
                return render_template('collection_card.html', flowers=flowers, items=items, isAdmin=False,
                                       number=number, flower_in_cart=flower_in_cart, flowers_buy=flowers_buy)
        else:
            return render_template('collection_card.html', flowers=flowers, items=items)


@main.route('/load_flower', methods=['GET', 'POST'])
def load_flower():
    datas = request.form.get('data')
    print(datas)
    str = ''
    if datas == '%null%':
        datas = ''
    else:
        json.loads(datas)
        for data in datas:
            str += data
        str = str.split('["')[1]
        str = str.split('"]')[0]
        datas = str.split('","')
    print(str)
    flowers = Flower.query
    for data in datas:
        item = '%' + data + '%'
        flowers = flowers.filter(or_(Flower.application.like(item), Flower.style.like(item)))
    flowers = flowers.all()
    flower_list = []
    for flower in flowers:
        if flower.on_sale:
            flower_list.append(flower.to_json())
    return jsonify(flower_list)


@main.route('/load_flower_price', methods=['GET', 'POST'])
def load_flower_price():
    from_ = request.form.get('from').split('$')[1]
    to = request.form.get('to').split('$')[1]

    flowers = Flower.query.filter(Flower.price >= from_, Flower.price <= to).all()
    flower_list = []
    for flower in flowers:
        if flower.on_sale:
            flower_list.append(flower.to_json())
    return jsonify(flower_list)


@main.route('/load_flower_color', methods=['GET', 'POST'])
def load_flower_color():
    color = request.form.get('color')
    if color == 'none':
        flowers = Flower.query.all()
    else:
        flowers = Flower.query.filter(Flower.color == color).all()
    flower_list = []
    for flower in flowers:
        if flower.on_sale:
            flower_list.append(flower.to_json())
    return jsonify(flower_list)


@main.route('/search_flower', methods=['GET', 'POST'])
def search_flower():
    datas = request.form.get('data')
    if datas == '%null%':
        data = ''
    else:
        data = datas
    item = '%' + data + '%'
    flowers = Flower.query.filter(Flower.name.like(item), Flower.on_sale == True).all()
    flower_list = []
    for flower in flowers:
        flower_list.append(flower.to_json())
    return jsonify(flower_list)


@main.route('/translate', methods=['GET', 'POST'])
def translate():
    language = request.form.get('language')
    # print(app.config['BABEL_DEFAULT_LOCALE'])
    Config.BABEL_DEFAULT_LOCALE = language
    return 'success'