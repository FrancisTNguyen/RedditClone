from datetime import datetime
import os
import pytz
from pytz import timezone
import request
from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'logs.db')
db = SQLAlchemy(app)
mar = Marshmallow(app)


def get_time():
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(timezone('US/Pacific'))
    pstTime = date
    return pstTime

# create a class for the user
# holds their information
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    karma = Column(Integer, default=0)
    createtime = Column(DateTime, default=get_time())
    changetime = Column(DateTime, default=get_time())

# create a class for posts
# holds information for posts
class Post(db.Model):
    _table_name = 'post'
    postID = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True, nullable=False)
    title = Column(String(120), nullable=False)
    text = Column(String(500), nullable=False)
    subreddit = Column(String(20), nullable=False)
    createtime = Column(DateTime, default=get_time())
    changetime = Column(DateTime, default=get_time())

    # this function is used to list out the variables without manually returning them all
    # just reference this function to output everything
    def serialize(self):
        return {
            "postID": self.postID,
            "username": self.username,
            "title": self.title,
            "text": self.text,
            "subreddit": self.subreddit,
            "createtime": self.createtime,
            "changetime": self.changetime
        }

# schema for Users
class UserData(mar.Schema):
    class Data:
        fields = ('id', 'username', 'email', 'password', 'karma', 'createtime', 'changetime')

# schema for posts
class PostData(mar.Schema):
    class Data:
        fields = ('id', 'username', 'title', 'text', 'subreddit', 'createtime', 'changetime')


userdata = UserData()
usermultdata = UserData(many=True)

postdata = PostData()
postmultdata = PostData(many=True)


@app.cli.command('create_db')
def create_db():
    db.create_all()
    print('created a database')


@app.cli.command('drop_db')
def drop_db():
    db.drop_all()
    print('dropped the db')


@app.cli.command('seed_db')
def seed_db():
    post = Post(username='FrancisNguyen', title="CSUF goes virtual after coronavirus outbreak",
                text="Most of the classes will go on zoom", subreddit="CSUF")
    db.session.add(post)

    test = User(username='FrancisNguyen', email="test@gmail.com", password='testpass', karma=12)

    db.session.add(test)
    db.session.commit()
    print('DB seeded')


@app.route('/')
def index():
    return 'Hello World'

# Register users
@app.route('/v1/api/user/register', methods=['POST'])
def register():
    email = request.form['email']
    username = request.form['username']
    regis = User.query.filter_by(email=email).first() and User.query.filter_by(username=username).first()
    if regis:
        return jsonify(message='Email or Username Already exists'), 409
    else:
        username = request.form['username']
        password = request.form['password']
        karma = request.form['karma']
        createtime = get_time()
        changetime = get_time()
        user = User(username=username, email=email, password=password,
                    karma=karma, createtime=createtime, changetime=changetime)
        db.session.add(user)

        db.session.commit()
        return jsonify(message='User created'), 201

# increment karma
@app.route('/v1/api/user/add_karma', methods=['PUT'])
def add_karma():
    username = request.form['username']
    user = User.query.filter_by(username=username).first()
    if user:
        user.karma += 1
        db.session.commit()
        return jsonify(message='Added karma'), 202
    else:
        return jsonify('Could not add karma'), 404

# decrement karma
@app.route('/v1/api/user/sub_karma', methods=['PUT'])
def sub_karma():
    username = request.form['username']
    user = User.query.filter_by(username=username).first()
    if user:
        user.karma -= 1
        db.session.commit()
        return jsonify(message='Subtracted karma!'), 202
    else:
        return jsonify('Could not subtract karma'), 404

# update user's email
@app.route('/v1/api/useer/update_email', methods=['PUT'])
def update_email():
    username = request.form['username']
    users = User.query.filter_by(username=username).first()
    if users:
        users.email = request.form['email']
        users.createtime = get_time()
        db.session.commit()
        return jsonify(message='Email updated'), 202
    else:
        return jsonify('This user does not exist'), 404

# delete user's account
@app.route('/v1/api/user/deactivate_acc/<string:username>', methods=['DELETE'])
def deactivate_account(username: str):
    username = User.query.filter_by(username=username).first()
    if username:
        db.session.delete(username)
        db.session.commit()
        return jsonify(message="deleted a user"), 202
    else:
        return jsonify(message="User doesn't exist"), 404

# create a post
@app.route('/v1/api/posts/make_post', methods=['POST'])
def make_post():
    username = request.form['username']
    makep = User.query.filter_by(username=username).first()
    if makep:
        username = request.form['username']
        title = request.form['title']
        text = request.form['text']
        subreddit = request.form['subreddit']
        createtime = get_time()
        changetime = get_time()
        post = Post(username=username, title=title, text=text, subreddit=subreddit,
                    createtime=createtime, changetime=changetime)
        db.session.add(post)
        db.session.commit()
        return jsonify(message='Post created'), 201
    else:
        return jsonify(message='Username does not exist'), 409

# delete a post
@app.route('/v1/api/posts/remove_post/<int:pid>', methods=['DELETE'])
def delete_post(pid: int):
    post = Post.query.filter_by(postID=pid).first()
    if post:
        db.session.delete(post)
        db.session.commit()
        return jsonify(message="Deleted a post"), 202
    else:
        return jsonify(message="Post does not exist"), 404

# retrieve a post
@app.route('/v1/api/posts/retrieve_post/<int:pid>', methods=['GET'])
def get_post(pid: int):
    post = Post.query.filter_by(postID=pid).first()
    if post:
        # references serialize() to list out all fields
        return jsonify(post.serialize())
    else:
        return jsonify(message="Post does not exist"), 404

# list posts by subreddit
@app.route('/v1/api/posts/list_post_sub/<string:subreddit>', methods=['GET'])
def list_post_sub(subreddit: str):
    posts = Post.query.filter_by(subreddit=subreddit).order_by(Post.createtime.desc())
    if posts:
        # serializes every variable in posts and returns them
        return jsonify(posts=[i.serialize() for i in posts])
    else:
        return jsonify(message="Post does not exist"), 404

# list all posts
@app.route('/v1/api/posts/list_all_posts/', methods=['GET'])
def list_all_posts():
    listposts = Post.query.order_by(Post.createtime.desc())
    return jsonify(listposts=[i.serialize() for i in listposts])


if __name__ == '__main__':
    app.run()
