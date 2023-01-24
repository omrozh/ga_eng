import random

import flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
from uuid import uuid4
from flask_bcrypt import Bcrypt
from utils.validation_utils import validate_form_submit, most_frequent, remove_all
from utils.payment_utils import create_charge, create_token
from datetime import datetime, timedelta
import requests

app = flask.Flask(__name__)

app.config["SECRET_KEY"] = ""
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

db = SQLAlchemy(app=app)
login_manager = LoginManager(app)

bcrypt = Bcrypt(app)


class Supply(db.Model):
    id = db.Column(db.String, primary_key=True)
    total_supply = db.Column(db.Integer, default=1000000000)
    remaining_supply = db.Column(db.Integer, default=1000000000)
    price_per_coin = db.Column(db.Float, default=0.05)


class User(db.Model, UserMixin):
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String, unique=True)
    follower_count = db.Column(db.Integer, default=0)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    balance = db.Column(db.Integer, default=0)
    phone_number = db.Column(db.String)
    did_verify_phone_number = db.Column(db.Boolean, default=False)


class Post(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    text_body = db.Column(db.String)
    image_uri = db.Column(db.String)
    creator_fk = db.Column(db.String)
    tags = db.Column(db.String)
    net_votes = db.Column(db.Integer, default=0)
    post_date = db.Column(db.Date)


class PostAnalytics(db.Model):
    id = db.Column(db.String, primary_key=True)
    views = db.Column(db.String)
    is_edited = db.Column(db.String)
    post_fk = db.Column(db.String)


class MoonVote(db.Model):
    id = db.Column(db.String, primary_key=True)
    voter_fk = db.Column(db.String)
    post_fk = db.Column(db.String)


class HellVote(db.Model):
    id = db.Column(db.String, primary_key=True)
    voter_fk = db.Column(db.String)
    post_fk = db.Column(db.String)


class Follow(db.Model):
    id = db.Column(db.String, primary_key=True)
    follower_fk = db.Column(db.String)
    followed_fk = db.Column(db.String)


class InterestObj(db.Model):
    id = db.Column(db.String, primary_key=True)
    user_fk = db.Column(db.String)
    last_twenty_interacted_tags = db.Column(db.String)
    following_tags = db.Column(db.String)
    following_creators = db.Column(db.String)
    most_common_keywords = db.Column(db.String)


class AuthenticationSMS(db.Model):
    id = db.Column(db.String, primary_key=True)
    user_fk = db.Column(db.String)
    sms_code = db.Column(db.String)


class Compliant(db.Model):
    id = db.Column(db.String, primary_key=True)
    reason = db.Column(db.String)
    post_fk = db.Column(db.String)


class LoginSession(db.Model):
    id = db.Column(db.String, primary_key=True)
    ip_address = db.Column(db.String)
    user_agent = db.Column(db.String)


class SuspendedAccount(db.Model):
    id = db.Column(db.String, primary_key=True)
    reason_of_suspension = db.Column(db.String)
    suspension_date = db.Column(db.Date)
    suspended_account_fk = db.Column(db.String)


class Comment(db.Model):
    id = db.Column(db.String, primary_key=True)
    commenter = db.Column(db.String)
    is_reply = db.Column(db.String)
    post_fk = db.Column(db.String)
    reply_fk = db.Column(db.String)
    content = db.Column(db.String)


class Tag(db.Model):
    id = db.Column(db.String, primary_key=True)
    tag_name = db.Column(db.String, unique=True)


class ReceiveOut(db.Model):
    id = db.Column(db.String, primary_key=True)
    payment_instructions = db.Column(db.String)


def get_coin_price():
    supply = Supply.query.first()
    return (supply.total_supply * 0.05) / supply.remaining_supply


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def index():
    return flask.render_template("index.html", is_authenticated=current_user.is_authenticated, user=current_user)


@app.route("/account/suspended")
@login_required
def account_suspended():
    suspension = SuspendedAccount.query.filter_by(suspended_account_fk=current_user.username).first()
    return flask.render_template("account/suspended.html", suspension=suspension)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        suspension = SuspendedAccount.query.filter_by(suspended_account_fk=current_user.username).first()
        if suspension:
            if "/account/suspended" not in str(flask.request.url_rule):
                    return flask.redirect("/account/suspended")


@app.route("/post/register", methods=["POST", "GET"])
def register():
    if flask.request.method == "POST":
        values = flask.request.values

        is_validated, reason = validate_form_submit(values, User)

        if not is_validated:
            return reason

        elif is_validated:
            new_user = User(id=str(uuid4()), username=values["username"],
                            password=bcrypt.generate_password_hash(values["password"]), email=values["email"],
                            phone_number=values["phone_number"])

            db.session.add(new_user)
            db.session.commit()

            return reason


@app.route("/account/login", methods=["POST", "GET"])
def login():
    if flask.request.method == "POST":
        values = flask.request.values
        user_login = User.query.filter_by(username=values["username"]).first()

        if bcrypt.check_password_hash(user_login.password, values["password"]):
            login_user(user_login, remember=True)
            return flask.redirect("/")

    return flask.render_template("account/login.html")


@app.route("/account/register")
def register_account_ui():
    return flask.render_template("account/register.html")


@app.route("/account/logout")
def logout():
    logout_user()
    return flask.redirect("/")


@app.route("/styles/<dir_main>/<dir_sub>")
def styles(dir_main, dir_sub):
    return flask.send_file(f"styles/{dir_main}/{dir_sub}")


@app.route("/scripts/<dir_main>/<dir_sub>")
def scripts(dir_main, dir_sub):
    return flask.send_file(f"scripts/{dir_main}/{dir_sub}")


@app.route("/static/<filename>")
def static_host(filename):
    return flask.send_file("static/" + filename)


@app.route("/unauthenticated/load-post-batch")
def load_post_batch_unauthenticated():
    top_posts = Post.query.order_by(Post.net_votes.desc()).all()[:50]
    all_top_posts = [
        {
            "title": i.title,
            "text_body": i.text_body,
            "has_image": True if i.image_uri else False,
            "image_uri": i.image_uri,
            "creator_username": User.query.get(i.creator_fk).username,
            "net_votes": i.net_votes,
            "post_id": i.id
        } for i in top_posts
    ]

    return flask.jsonify(all_top_posts)


@app.route("/authenticated/load-post-batch/<paginate>")
def load_post_batch_authenticated(paginate):
    follows = [i.followed_fk for i in Follow.query.filter_by(follower_fk=current_user.id).all()]

    follow_posts = []

    for i in Post.query.order_by(Post.post_date.desc()).all():
        for c in follows:
            if "#" + c in i.tags.split("&&"):
                follow_posts.append(i)

    follow_posts = set(follow_posts)
    follow_posts = list(follow_posts)

    follow_posts.sort(key=lambda x: x.net_votes, reverse=True)

    all_top_posts = [
        {
            "title": i.title,
            "text_body": i.text_body,
            "has_image": True if i.image_uri else False,
            "image_uri": i.image_uri,
            "creator_username": User.query.get(i.creator_fk).username,
            "net_votes": i.net_votes,
            "post_id": i.id
        } for i in follow_posts[int(paginate):int(paginate) + 50]
    ]

    return flask.jsonify(all_top_posts)


@app.route("/new/post", methods=["POST", "GET"])
@login_required
def new_post():
    if flask.request.method == "POST":
        if current_user.balance < 2:
            return '''
                <script>
                    alert('Insufficient account balance')
                    document.location = '/buy/token'
                <script>
            '''

        values = flask.request.values

        image = flask.request.files["image_file"]

        save_image_uuid = str(uuid4())

        if len(image.filename) > 2:
            image.save("file_content/" + save_image_uuid)

        get_tags = []

        for i in values["text_body"].split("\n"):
            for c in i.split(" "):
                if "#" in c:
                    get_tags.append(c)

        for i in get_tags:
            if i not in [c.tag_name for c in Tag.query.all()]:
                new_tag = Tag(tag_name=i, id=str(uuid4()))
                db.session.add(new_tag)

        new_post_add = Post(id=str(uuid4()), creator_fk=current_user.id, title=values["title"],
                            text_body=values["text_body"],
                            image_uri=str("/file_content/" + save_image_uuid) if len(image.filename) > 2 else None,
                            tags="&&".join(set(get_tags)), post_date=datetime.today())

        current_user.balance -= 2
        Supply.query.first().price_per_coin += 2

        db.session.add(new_post_add)
        db.session.commit()

        return flask.redirect("/")

    return flask.render_template("posts/new_post.html")


@app.route("/view-post/<post_id>", methods=["POST", "GET"])
def view_post(post_id):
    if flask.request.method == "POST":
        new_comment = Comment(post_fk=post_id, content=flask.request.values["comment"], commenter=current_user.username,
                              id=str(uuid4()))
        db.session.add(new_comment)
        db.session.commit()
        return flask.redirect("/view-post/" + post_id)
    post_query = Post.query.get(post_id)
    post = {
        "title": post_query.title,
        "text_body": post_query.text_body,
        "has_image": True if post_query.image_uri else False,
        "image_uri": post_query.image_uri,
        "creator_username": User.query.get(post_query.creator_fk).username,
        "net_votes": post_query.net_votes,
        "post_id": post_query.id,
        "comments": Comment.query.filter_by(post_fk=post_id).all()
    }

    return flask.render_template("posts/post_view.html", post=post, user=current_user,
                                 is_authenticated=current_user.is_authenticated,
                                 comments=Comment.query.filter_by(post_fk=post_id))


@app.route("/moonvote/<post_id>")
@login_required
def moonvote(post_id):
    if current_user.balance < 1:
        return '''
            <script>
                alert("Insufficient account balance")
                document.location = '/buy/token'
            </script>
        '''

    new_moonvote = MoonVote(id=str(uuid4()), post_fk=post_id, voter_fk=current_user.id)
    Post.query.get(post_id).net_votes += 1

    current_user.balance -= 1
    if not current_user.id == User.query.get(Post.query.get(post_id).creator_fk).id:
        User.query.get(Post.query.get(post_id).creator_fk).balance += 1

    db.session.add(new_moonvote)
    db.session.commit()

    return flask.redirect("/")


@app.route("/view-tag/<tag>")
def view_tag(tag):
    posts_in_tag = []

    for i in Post.query.order_by(Post.post_date.desc()).all():
        if i.post_date > datetime.today().date() - timedelta(days=14):
            if "#" + tag in i.tags.split("&&"):
                posts_in_tag.append(i)
        else:
            break

    all_top_posts = [
        {
            "title": i.title,
            "text_body": i.text_body,
            "has_image": True if i.image_uri else False,
            "image_uri": i.image_uri,
            "creator_username": User.query.get(i.creator_fk).username,
            "net_votes": i.net_votes
        } for i in posts_in_tag
    ]

    return flask.jsonify(all_top_posts)


@app.route("/tags/<tag_name>")
def view_tag_ui(tag_name):
    tag_is_followed = tag_name in [i.followed_fk for i in Follow.query.filter_by(follower_fk=current_user.id).all()]
    return flask.render_template("posts/tag_view.html", tag_name=tag_name, user=current_user,
                                 is_authenticated=current_user.is_authenticated, tag_is_followed=tag_is_followed)


@app.route("/tags/search/<search_term>")
def tags_search(search_term):
    return flask.jsonify([i.tag_name for i in Tag.query.filter(Tag.tag_name.like("%" + search_term + "%")).all()])


@app.route("/follow-tag/<tag_name>")
@login_required
def follow_tag(tag_name):
    new_follow = Follow.query.filter_by(followed_fk=tag_name).filter_by(follower_fk=current_user.id).first()
    if new_follow:
        return flask.redirect("/tags/" + tag_name)
    new_follow = Follow(follower_fk=current_user.id, followed_fk=tag_name, id=str(uuid4()))
    db.session.add(new_follow)
    db.session.commit()

    return flask.redirect("/tags/" + tag_name)


@app.route("/unfollow-tag/<tag_name>")
@login_required
def unfollow_tag(tag_name):
    remove_follow = Follow.query.filter_by(followed_fk=tag_name).filter_by(follower_fk=current_user.id).first()
    db.session.delete(remove_follow)
    db.session.commit()
    return flask.redirect("/tags/" + tag_name)


@app.route("/hellvote/<post_id>")
@login_required
def hellvote(post_id):
    if current_user.balance < 1:
        return '''
            <script>
                alert("Insufficient account balance")
                document.location = '/buy/token'
            </script>
        '''

    new_hellvote = HellVote(id=str(uuid4()), post_fk=post_id, voter_fk=current_user.id)
    Post.query.get(post_id).net_votes -= 1

    current_user.balance -= 1

    db.session.add(new_hellvote)
    db.session.commit()

    return flask.redirect("/")


@app.route("/get_trending_tags")
def get_trending_tags():
    posts = Post.query.filter_by(post_date=datetime.today().date()).all()

    for i in Post.query.filter_by(post_date=datetime.today().date() - timedelta(days=1)).all():
        posts.append(i)

    tags = []

    for i in posts:
        for c in i.tags.split("&&"):
            tags.append(c)

    most_seen_tags = []

    if len(set(tags)) < 8:
        for i in set(tags):
            most_seen_tags.append(i)
    else:
        while len(most_seen_tags) < 8:
            most_seen_tags.append(most_frequent(tags))
            tags = remove_all(tags, most_frequent(tags))

    return flask.jsonify(most_seen_tags)


@app.route("/file_content/<filename>")
def file_content(filename):
    return flask.send_file("file_content/" + filename)


@app.route("/verify_sms", methods=["POST", "GET"])
@login_required
def verify_sms():
    if flask.request.method == "POST":
        authentication_code = AuthenticationSMS.query.filter_by(user_fk=current_user.id).first().sms_code
        if authentication_code == flask.request.values["sms_code"]:
            current_user.did_verify_phone_number = True
            current_user.balance += 5

            supply = Supply.query.first()
            supply.total_supply += 5

            db.session.commit()
        return flask.redirect("/")

    if not AuthenticationSMS.query.filter_by(user_fk=current_user.id).first():
        new_authentication = AuthenticationSMS(id=str(uuid4()), user_fk=current_user.id,
                                               sms_code=random.randint(999999, 9999999))
        db.session.add(new_authentication)
        db.session.commit()

        resp = requests.post('https://textbelt.com/text', {
            'phone': current_user.phone_number,
            'message': "You GrandAssembly SMS confirmation code is: " + new_authentication.sms_code,
            'key': '1b4e27fef678a60a3978b559f480204d3dfd7509lfcbJzNhDNesC4QRb47QQw9PH',
        })
    else:
        return flask.redirect("/verify_sms")

    return flask.render_template("account/verify_sms.html")


@app.route("/trading/buy", methods=["POST", "GET"])
@login_required
def buy_token():
    if flask.request.method == "POST":
        values = flask.request.values
        if not bcrypt.check_password_hash(current_user.password, values["password"]):
            return '''
                <script>
                    alert("Password Incorrect")
                    window.location.reload()
                </script>
            '''
        card_info = {
            "number": values["card_number"],
            "cvc": values["cvc"],
            "exp_month": int(values["date"].split("/")[0]),
            "exp_year": int(values["date"].split("/")[1])
        }
        token_id = create_token(card_info).get("id")
        charge = create_charge(token_id=token_id, amount=get_coin_price()*int(values["coin_amount"]))

        current_user.balance += int(values["coin_amount"])
        db.session.commit()

        return flask.redirect("/")
    return flask.render_template("trading/buy_token.html", token_price=get_coin_price())


@app.route("/trading/sell", methods=["POST", "GET"])
@login_required
def sell_token():
    if flask.request.method == "POST":
        values = flask.request.values

        if not bcrypt.check_password_hash(current_user.password, values["password"]):
            return '''
                <script>
                    alert("Password Incorrect")
                    window.location.reload()
                </script>
            '''

        new_payout = ReceiveOut(id=str(uuid4()), payment_instructions=values["payment_info"])

        db.session.add(new_payout)
        db.session.commit()

        return flask.render_template("trading/payout_confirmation.html")
    return flask.render_template("trading/sell_token.html")


@app.route("/trading")
@login_required
def trading_hub():
    return flask.render_template("trading/hub.html")


@app.errorhandler(500)
def handle_internal_server(e):
    return flask.redirect("/")


@app.errorhandler(401)
def handle_unauth(e):
    return flask.redirect("/account/login")