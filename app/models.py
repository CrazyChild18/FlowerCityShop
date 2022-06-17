# 数据库表
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
from flask import current_app, request
from app import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True, unique=True)
    name = db.Column(db.String, index=True)
    email = db.Column(db.String, index=True, unique=True)
    phone = db.Column(db.String, index=True, unique=True)

    avatar = db.Column(db.String)
    age = db.Column(db.Integer, index=True)
    gender = db.Column(db.String, index=True)
    country = db.Column(db.String, index=True)
    # 学生、医生、老师、警察、律师、商店老板
    job = db.Column(db.String, index=True)

    password = db.Column(db.String, index=True)
    isAdmin = db.Column(db.Boolean, index=True, default=False)
    confirmed = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime(), default=datetime.now)
    isVIP = db.Column(db.Boolean, index=True, default=False)
    deposit = db.Column(db.Float, index=True, default=0.0)

    customer_order = db.relationship('Order', backref='author', lazy='dynamic')
    customer_wishlist = db.relationship('Wishlist', backref='wish', lazy='dynamic')
    customer_cart = db.relationship('Cart', backref='cart_user', lazy='dynamic', cascade='all, delete-orphan')
    information = db.relationship('Information', backref='information', lazy='dynamic', cascade='all, delete-orphan')
    blog_poster = db.relationship('Blog', backref='poster', lazy='dynamic', cascade='all, delete-orphan')
    blog_comment_user = db.relationship('BlogComment', backref='dynamic', cascade='all, delete-orphan')

    liked_post = db.relationship('Like', back_populates='liker', lazy='dynamic', cascade='all, delete-orphan')

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)
        db.session.commit()

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    def like(self, post):
        if not self.is_liking(post):
            ll = Like(liker=self, liked_post=post)
            db.session.add(ll)

    def dislike(self, post):
        ll = self.liked_post.filter_by(liked_post_id=post.id).first()
        if ll:
            db.session.delete(ll)

    def is_liking(self, post):
        if post.id is None:
            return False
        return self.liked_post.filter_by(
            liked_post_id=post.id).first() is not None

    def total_consumption(self):
        orders = Order.query.filter(Order.customer_id == self.id).all()
        total = 0.0
        for order in orders:
            total += order.total
        return total

    # 该方法是用于帮助用户重置密码
    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

class Flower(db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True)
    name = db.Column(db.String, index=True, unique=True)
    pic = db.Column(db.String, index=True, unique=True)
    price = db.Column(db.Float, index=True)
    intro = db.Column(db.String)
    amount = db.Column(db.INTEGER, index=True)
    style = db.Column(db.String, index=True)
    grade = db.Column(db.Float, index=True, default=6)
    time_in = db.Column(db.DateTime, index=True, default=datetime.now())
    on_sale = db.Column(db.Boolean, index=True, default=True)
    application = db.Column(db.String, index=True)
    color = db.Column(db.String, index=True)
    hit_number = db.Column(db.Integer, index=True, default=0)
    detailed = db.Column(db.Text)
    wish = db.relationship('Wishlist', backref='flower_wish', lazy='dynamic')
    cart = db.relationship('Cart', backref='flower_cart', lazy='dynamic', cascade='all, delete-orphan')
    order_detail = db.relationship('Order_Detail', backref='flower_order_detail', lazy='dynamic')

    def to_json(self):
        dict = self.__dict__
        if '_sa_instance_state' in dict:
            del dict['_sa_instance_state']
        return dict

class Order(db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True)
    time = db.Column(db.DateTime, index=True, default=datetime.now)
    finish = db.Column(db.Integer, nullable=False, default=0)
    name = db.Column(db.String)
    total = db.Column(db.Integer)
    # 储存flower表中信息作为购买项
    # 储存User表中信息作为购买人（一对多）
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    detail = db.relationship('Order_Detail', backref='order_detail', lazy='dynamic', cascade='all, delete-orphan')

    def to_json(self):
        dict = self.__dict__
        if '_sa_instance_state' in dict:
            del dict['_sa_instance_state']
        return dict


class Wishlist(db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True)
    price_in = db.Column(db.Float, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('flower.id'))


class Cart(db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True)
    number = db.Column(db.Integer, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('flower.id'))


class Information(db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True)
    name = db.Column(db.String)
    nation = db.Column(db.Text)
    city = db.Column(db.String)
    address = db.Column(db.Text)
    phone = db.Column(db.String)
    default = db.Column(db.Boolean, default=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_json(self):
        dict = self.__dict__
        if '_sa_instance_state' in dict:
            del dict['_sa_instance_state']
        return dict


class Order_Detail(db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True)
    number = db.Column(db.Integer, index=True)
    content = db.Column(db.Text)
    time = db.Column(db.DateTime, default=datetime.now())
    grade = db.Column(db.Integer, default=0)
    time = db.Column(db.DateTime, index=True, default=datetime.now())
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('flower.id'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 用来存储信息
class Message(db.Model):
    __tablename__ = 'message'
    msg_id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Integer)
    receiver = db.Column(db.Integer)
    system_time = db.Column(db.String(32))
    message = db.Column(db.Text)
    status = db.Column(db.Integer,default=0)


# 信息转化，用来显示信息
class ChatMessage(db.Model):
    __tablename__ = 'chatMessage'
    msg_id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(32))
    receiver = db.Column(db.String(32))
    system_time = db.Column(db.String)
    message = db.Column(db.Text)

    def to_json(self):
        dict = self.__dict__
        if '_sa_instance_state' in dict:
            del  dict['_sa_instance_state']
        return dict


# 用来添加好友用  默认只有好友之间才能进行communicate
# 同时用来判断消息传输
# 这里对于同一对id键2条record用来方便查询消息发送
class Friends(db.Model):
    __tablename__ = 'friends'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    receiver = db.Column(db.Integer)
    sender = db.Column(db.Integer)
    status = db.Column(db.Integer, default=0)

    def to_json(self):
        dict = self.__dict__
        if '_sa_instance_state' in dict:
            del  dict['_sa_instance_state']
        return dict


# 这个class用来显示用户的状态 如果用户的状态是1那么在chat list 会显示为绿色 反之为黑色
class SenderInfo(db.Model):
    __tablename__ = 'senderInfo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer)
    name = db.Column(db.String(32))
    picture = db.Column(db.String(256))
    status = db.Column(db.Integer)

    def to_json(self):
        dict = self.__dict__
        if '_sa_instance_state' in dict:
            del  dict['_sa_instance_state']
        return dict


# blog
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    describe = db.Column(db.Text)
    content = db.Column(db.Text)
    time = db.Column(db.DateTime, default=datetime.now)
    like = db.Column(db.Integer, default=0)
    post_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment_poster = db.relationship('BlogComment', backref='poster', lazy='dynamic', cascade='all, delete-orphan')
    post_pic = db.relationship('BlogPic', backref='blog_pic', lazy='dynamic', cascade='all, delete-orphan')
    liker = db.relationship('Like', back_populates='liked_post', lazy='dynamic', cascade='all')

    def to_json(self):
        dict = self.__dict__
        if '_sa_instance_state' in dict:
            del  dict['_sa_instance_state']
        return dict

    def like(self, user):
        if not self.is_liked_by(user):
            ll = Like(liker=user, liked_post=self)
            db.session.add(ll)

    def dislike(self, user):
        ll = self.liker.filter_by(liker_id=user.id).first()
        if ll:
            db.session.delete(ll)

    def is_liked_by(self, user):
        if user.id is None:
            return False
        return self.liker.filter_by(
            liker_id=user.id).first() is not None


class Like(db.Model):
    liker_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    liked_post_id = db.Column(db.Integer, db.ForeignKey('blog.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    liker = db.relationship('User', back_populates='liked_post', lazy='joined')
    liked_post = db.relationship('Blog', back_populates='liker', lazy='joined')


# blog comment
class BlogComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=datetime.now)
    comment = db.Column(db.Text)
    comment_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment_post = db.Column(db.Integer, db.ForeignKey('blog.id'))




class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    content = db.Column(db.Text)
    time = db.Column(db.DateTime, default=datetime.now)


class Buy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer)
    customer_id = db.Column(db.Integer)
    number = db.Column(db.Integer)


class BlogPic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pic = db.Column(db.String, index=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))