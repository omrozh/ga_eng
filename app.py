import random

import flask
import openai.error
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
from uuid import uuid4
from flask_bcrypt import Bcrypt
from utils.validation_utils import validate_form_submit, most_frequent, remove_all
from utils.payment_utils import create_charge, create_token, get_card_info
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from string import ascii_letters
from utils.txt_generation import gen_text
from flask_mail import Mail, Message
from os.path import exists
from flask_migrate import Migrate

app = flask.Flask(__name__)

app.config["SECRET_KEY"] = "8ujs-fjeud-jdv&e3-fgeu3id-3jfsu2tf+!0"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

db = SQLAlchemy(app=app)
login_manager = LoginManager(app)

bcrypt = Bcrypt(app)
migrate = Migrate(app, db)


class Supply(db.Model):
    id = db.Column(db.String, primary_key=True)
    total_supply = db.Column(db.Integer, default=10000000000)
    remaining_supply = db.Column(db.Integer, default=10000000000)
    price_per_coin = db.Column(db.Float, default=0.005)


class Notification(db.Model):
    id = db.Column(db.String, primary_key=True)
    user_fk = db.Column(db.String)
    notification_head = db.Column(db.String)
    notification_body = db.Column(db.String)
    onclick_link = db.Column(db.String)
    is_read = db.Column(db.Boolean)


class User(db.Model, UserMixin):
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String, unique=True)
    follower_count = db.Column(db.Integer, default=0)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    balance = db.Column(db.Integer, default=0)
    phone_number = db.Column(db.String)
    did_verify_phone_number = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean)
    fullname = db.Column(db.String)
    latest_ip = db.Column(db.String)


class Test(db.Model):
    id = db.Column(db.String, primary_key=True)
    outcomes = db.Column(db.String)
    post_fk = db.Column(db.String)
    is_poll_bet = db.Column(db.Boolean)
    end_date = db.Column(db.Date)


class Question(db.Model):
    id = db.Column(db.String, primary_key=True)
    question_body = db.Column(db.String)
    question_type = db.Column(db.String)
    answer_choices = db.Column(db.String)
    answer_points = db.Column(db.String)
    test_fk = db.Column(db.String)


class ListPoint(db.Model):
    id = db.Column(db.String, primary_key=True)
    post_fk = db.Column(db.String)
    text_body = db.Column(db.String)


class CardToken(db.Model):
    token = db.Column(db.String, primary_key=True)
    user_fk = db.Column(db.String)


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


class Advert(db.Model):
    id = db.Column(db.String, primary_key=True)
    total_budget = db.Column(db.Float)
    budget_spent = db.Column(db.Float, default=0)
    bid_target = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    creators_alike = db.Column(db.String)
    advert_type = db.Column(db.String)
    total_views = db.Column(db.Integer, default=0)
    advert_clicks = db.Column(db.Integer, default=0)


class AuthenticationSMS(db.Model):
    id = db.Column(db.String, primary_key=True)
    user_fk = db.Column(db.String)
    sms_code = db.Column(db.String)


class Compliant(db.Model):
    id = db.Column(db.String, primary_key=True)
    reason = db.Column(db.String)
    post_fk = db.Column(db.String)


class Referral(db.Model):
    id = db.Column(db.String, primary_key=True)
    referrer = db.Column(db.String)
    referred_account = db.Column(db.String)


class PostView(db.Model):
    id = db.Column(db.String, primary_key=True)
    viewer_fk = db.Column(db.String)
    post_fk = db.Column(db.String)


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


class Election(db.Model):
    id = db.Column(db.String, primary_key=True)
    type = db.Column(db.String)
    election_start_date = db.Column(db.Date)
    election_end_date = db.Column(db.Date)
    election_title = db.Column(db.String)
    election_context = db.Column(db.String)


class Committee(db.Model):
    id = db.Column(db.String, primary_key=True)
    election_fk = db.Column(db.String)
    term_ending = db.Column(db.Date)


class Representative(db.Model):
    id = db.Column(db.String, primary_key=True)
    active_work = db.Column(db.Boolean)
    committee_fk = db.Column(db.String)
    user_fk = db.Column(db.String)
    photo_uri = db.Column(db.String)


class RepresentativeCandidate(db.Model):
    id = db.Column(db.String, primary_key=True)
    election_fk = db.Column(db.String)
    user_fk = db.Column(db.String)
    total_votes = db.Column(db.Integer)


class FollowUser(db.Model):
    id = db.Column(db.String, primary_key=True)
    followed_fk = db.Column(db.String)
    follower_fk = db.Column(db.String)


class PollAnswer(db.Model):
    id = db.Column(db.String, primary_key=True)
    question_fk = db.Column(db.String)
    user_fk = db.Column(db.String)
    given_answer = db.Column(db.String)


def id_gen():
    ret_id = "".join([random.choice(ascii_letters) for i in range(8)])
    while Post.query.get(ret_id):
        ret_id = "".join([random.choice(ascii_letters) for i in range(8)])
    return ret_id


def get_coin_price():
    supply = Supply.query.first()
    return (supply.total_supply * 0.05) / supply.remaining_supply


app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'no-reply@grandassembly.net'
app.config["MAIL_PASSWORD"] = 'kdyjtaofikbkbhff'

mail = Mail(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def generate_email(email_type, code):
    type_dict = {
        "verification_code": "verification_code",
    }
    with open(f"emails/{type_dict[email_type]}.html") as data:
        return data.read().replace("#link#", code)


def distribute_bets():
    with app.app_context():
        bet_tests = Test.query.filter_by(end_date=datetime.today().date()).filter_by(is_poll_bet=True).all()
        for i in bet_tests:

            i.is_poll_bet = False
            test_questions = Question.query.filter_by(test_fk=i.id).all()

            for j in test_questions:
                p_distribution = {}
                options = [c.split("#")[0] for c in j.answer_choices.split("&&")]
                for c in options:
                    p_distribution[c] = len(
                        PollAnswer.query.filter_by(question_fk=j.id).filter_by(given_answer=c).all())
                highest_val = ""
                for c in p_distribution.keys():
                    if p_distribution.get(c) > p_distribution.get(highest_val, 0):
                        highest_val = c
                total = sum([p_distribution[c] for c in p_distribution.keys()])
                if total == 0:
                    continue
                total_winners = p_distribution[highest_val]
                for c in PollAnswer.query.filter_by(question_fk=j.id).filter_by(given_answer=highest_val).all():
                    User.query.get(c.user_fk).balance += int((total / total_winners) * 5)
                    new_notification = Notification(notification_head="Tebrikler!", notification_body="Token anketinde "
                                                                                                      "tahmininiz doğru "
                                                                                                      "çıktı.",
                                                    is_read=False, onclick_link="/p/" + i.post_fk, user_fk=c.user_fk,
                                                    id=str(uuid4()))
                    db.session.add(new_notification)
                    db.session.commit()
        db.session.commit()


sched = BackgroundScheduler(daemon=True)
sched.add_job(distribute_bets, 'interval', days=1)
sched.start()


@app.route("/admin", methods=["POST", "GET"])
@login_required
def admin():
    if not current_user.is_admin:
        return "You do not have the required permissions to view this page."
    return flask.render_template("admin/admin.html", elections=Election.query.all(),
                                 number_of_users=len(User.query.all()), user_list=User.query.all())


@app.route("/admin/delete-user/<user_id>")
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return "You do not have the required permissions to view this page."
    user_to_delete = User.query.get(user_id)
    user_posts = Post.query.filter_by(creator_fk=user_id).all()
    user_comments = Comment.query.filter_by(commenter=user_to_delete.username).all()

    for i in user_posts:
        db.session.delete(i)
    for i in user_comments:
        db.session.delete(i)
    db.session.delete(user_to_delete)
    db.session.commit()
    return flask.redirect("/admin")


def add_bots(number_of_posts):
    for j in range(number_of_posts):
        username, title, text_body = gen_text()
        new_user = User(id=str(uuid4()), username=username,
                        password=bcrypt.generate_password_hash(username), email=username + "@gmail.com",
                        phone_number=random.randint(99999999, 999999999))

        db.session.add(new_user)

        get_tags = []

        for i in text_body.split("\n"):
            for c in i.split(" "):
                if "#" in c:
                    get_tags.append(c)

        for i in text_body:
            if i not in [c.tag_name for c in Tag.query.all()]:
                new_tag = Tag(tag_name=i, id=str(uuid4()))
                db.session.add(new_tag)

        new_post_add = Post(id=str(id_gen()), creator_fk=new_user.id, title=title,
                            text_body=text_body.replace("\n", " &newline& ").replace("\r", ""),
                            image_uri=None,
                            tags="&&".join(set(get_tags)), post_date=datetime.today())

        db.session.add(new_post_add)

        db.session.commit()
    return "Added Text"


@app.route("/admin/notify", methods=["POST", "GET"])
@login_required
def admin_notify():
    if not current_user.is_admin:
        return flask.redirect("/")
    if flask.request.method == "POST":
        subject_post = Post.query.get(flask.request.values["post_id"])
        for i in User.query.all():
            try:
                post_body = " ".join(subject_post.text_body.split(" ")[:10]) + "..."
                new_notification = Notification(notification_head=subject_post.title, notification_body=post_body,
                                                is_read=False, onclick_link="/p/" + subject_post.id, user_fk=i.id,
                                                id=str(uuid4()))
                db.session.add(new_notification)
                db.session.commit()
            except Exception as e:
                continue
        return flask.redirect("/admin")
    return flask.render_template("admin/notify.html")


@app.route("/account/notifications")
@login_required
def notifications():
    all_notifications = Notification.query.filter_by(user_fk=current_user.id).all()
    for i in Notification.query.filter_by(user_fk=current_user.id).all():
        i.is_read = True
    db.session.commit()
    all_notifications.reverse()
    return flask.render_template("account/notifications.html", notifications=all_notifications, user=current_user)


@app.route("/ai/assist", methods=["POST", "GET"])
@login_required
def ai_assist():
    if current_user.balance < 10 and not current_user.is_admin:
        return "Failed"

    try:
        txt_gen, total_usage = gen_text(flask.request.values["content"])
    except openai.error.APIError:
        return "Yapay Zeka Hatası - Tekrar Dene \n " + flask.request.values["content"]

    current_user.balance -= int(int(total_usage) / 75)
    db.session.commit()
    return txt_gen


@app.route("/ai/waitinglist")
@login_required
def ai_rewrite():
    return flask.render_template("waitinglist_confirm.html")


@app.route("/admin/boost_post/<post_id>")
def boost_post(post_id):
    if not current_user.is_admin:
        return flask.redirect("/")

    Post.query.get(post_id).net_votes += 100
    db.session.commit()

    return flask.redirect("/")


@app.route("/admin/create_disposable_account")
def create_mass_account():
    if not current_user.is_admin:
        return "You do not have the required permissions to view this page."

    from random_username.generate import generate_username
    username = generate_username(1)[0]
    new_user = User(id=str(uuid4()), username=username,
                    password=bcrypt.generate_password_hash(username), email=username + "@gmail.com",
                    phone_number=random.randint(99999999, 999999999), balance=1000)

    db.session.add(new_user)
    db.session.commit()
    return username


@app.route("/admin/verify-user", methods=["POST", "GET"])
@login_required
def verify_user():
    if not current_user.is_admin:
        return "You do not have the required permissions to view this page."

    if flask.request.method == "POST":
        new_verification = Compliant(id=str(uuid4()), post_fk=flask.request.values["username"])
        db.session.add(new_verification)
        db.session.commit()
        return flask.redirect("/admin")
    return flask.render_template("admin/verify_user.html")


@app.route("/admin/add-candidate/<election_id>", methods=["POST", "GET"])
def add_candidate_to_election(election_id):
    if not current_user.is_admin:
        return "You do not have the required permissions to view this page."
    if flask.request.method == "POST":
        new_candidate = RepresentativeCandidate(id=str(uuid4()), election_fk=election_id,
                                                user_fk=flask.request.values["username"],
                                                total_votes=0)
        db.session.add(new_candidate)
        db.session.commit()
    return flask.render_template("admin/add_candidate.html")


@app.route("/p/<post_id>")
def redirect_post(post_id):
    return flask.redirect("/view-post/" + post_id)


@app.route("/admin/delete-post", methods=["POST", "GET"])
@login_required
def delete_post():
    if not current_user.is_admin:
        return "You do not have the required permissions to view this page."

    if flask.request.method == "POST":
        db.session.delete(Post.query.get(flask.request.values["post_id"]))
        db.session.commit()
        return flask.redirect("/admin")
    return flask.render_template("admin/delete_post.html")


@app.route("/admin/issue-suspension", methods=["POST", "GET"])
@login_required
def admin_suspend():
    if not current_user.is_admin:
        return "You do not have the required permissions to view this page."
    if flask.request.method == "POST":
        new_suspension = SuspendedAccount(id=str(uuid4()), reason_of_suspension=flask.request.values["reason"],
                                          suspended_account_fk=flask.request.values["username"],
                                          suspension_date=datetime.today())
        db.session.add(new_suspension)
        db.session.commit()
    return flask.render_template("admin/suspend_user.html")


@app.route("/cast_vote/<username>")
@login_required
def cast_vote(username):
    candidate = RepresentativeCandidate.query.filter_by(user_fk=username).first()
    candidate.total_votes += 1
    current_user.balance -= 10
    db.session.commit()

    return flask.redirect("/")


@app.route("/election/<election_id>")
def election(election_id):
    candidates = RepresentativeCandidate.query.filter_by(election_fk=election_id).all()
    return flask.render_template("election.html", election=Election.query.get(election_id), candidates=candidates)


@app.route("/admin/create-election", methods=["POST", "GET"])
@login_required
def create_election():
    if not current_user.is_admin:
        return "You do not have the required permissions to view this page."
    if flask.request.method == "POST":
        values = flask.request.values
        new_election = Election(
            id=str(uuid4()), type=values["type"],
            election_start_date=datetime.today().date() + timedelta(
                days=int(values["campaign_time"])),
            election_end_date=datetime.today().date() + timedelta(
                days=int(values["campaign_time"]) + 7),
            election_title=values["title"],
            election_context=values["context"]
        )

        new_post_elect = Post(id=str(uuid4()), creator_fk=current_user.id, title=values["title"],
                              text_body=values["context"],
                              post_date=datetime.today(), tags="#elections")
        db.session.add(new_post_elect)

        db.session.add(new_election)
        db.session.commit()

        return flask.redirect("/admin")
    return flask.render_template("admin/create_election.html")


@app.route("/whats-popular")
def whats_popular():
    highlights = []
    if current_user.is_authenticated:
        user_follows = FollowUser.query.filter_by(follower_fk=current_user.id).all()

        for i in Post.query.filter_by(post_date=datetime.today().date()).all():
            for c in user_follows:
                if c.followed_fk == i.creator_fk:
                    if i not in highlights:
                        highlights.append(i)

        highlights = [
            {
                "creator_username": User.query.get(i.creator_fk).username,
                "post_title": " ".join(i.title.split(" ")[:5]) + "..." if len(i.title.split(" ")) > 6 else " ".join(
                    i.title.split(" ")[:5]),
                "post_id": i.id
            } for i in highlights
        ]
    highlights_exist = len(highlights) > 0

    return flask.render_template("/posts/whats_popular.html", is_authenticated=current_user.is_authenticated,
                                 user=current_user,
                                 highlights=highlights, highlights_exist=highlights_exist)


@app.route("/")
def index():
    highlights = []
    user_has_new_notification = False
    if current_user.is_authenticated:
        user_has_new_notification = len(
            Notification.query.filter_by(user_fk=current_user.id).filter_by(is_read=False).all()) > 0
        user_follows = FollowUser.query.filter_by(follower_fk=current_user.id).all()

        for i in Post.query.filter_by(post_date=datetime.today().date()).all():
            for c in user_follows:
                if c.followed_fk == i.creator_fk:
                    if i not in highlights:
                        highlights.append(i)

        highlights = [
            {
                "creator_username": User.query.get(i.creator_fk).username,
                "post_title": " ".join(i.title.split(" ")[:5]) + "..." if len(i.title.split(" ")) > 6 else " ".join(
                    i.title.split(" ")[:5]),
                "post_id": i.id
            } for i in highlights
        ]
    else:
        return flask.redirect("/account/register")
    highlights_exist = len(highlights) > 0

    return flask.render_template("index.html", is_authenticated=current_user.is_authenticated, user=current_user,
                                 highlights=highlights, highlights_exist=highlights_exist,
                                 user_has_new_notification=user_has_new_notification)


@app.route("/account/<username>")
def account_view(username):
    user_info = User.query.filter_by(username=username).first()
    posts = Post.query.filter_by(creator_fk=user_info.id).all()
    for i in posts:
        i.text_body = " ".join(i.text_body.split(" ")[:15]).replace("&newline&", "")
    tag_is_followed = user_info.id in [i.followed_fk for i in
                                       FollowUser.query.filter_by(follower_fk=current_user.id).all()]

    number_of_subs = len(FollowUser.query.filter_by(followed_fk=user_info.id).all())

    is_verified = True if Compliant.query.filter_by(post_fk=username).first() else True if user_info.is_admin else False

    return flask.render_template("posts/user_view.html", tag_name=username, user=current_user, posts=posts,
                                 is_authenticated=current_user.is_authenticated, tag_is_followed=tag_is_followed,
                                 user_info=user_info, number_of_subs=number_of_subs, is_verified=is_verified)


@app.route("/account/follow/<user_id>")
@login_required
def follow_user(user_id):
    if FollowUser.query.filter_by(followed_fk=user_id, follower_fk=current_user.id).first():
        return flask.redirect("/")
    new_follow = FollowUser(id=str(uuid4()), followed_fk=user_id, follower_fk=current_user.id)
    db.session.add(new_follow)
    db.session.commit()
    return flask.redirect("/account/" + User.query.get(user_id).username)


@app.route("/post/follow/<user_id>/<post_id>")
@login_required
def follow_user_post(user_id, post_id):
    if FollowUser.query.filter_by(followed_fk=user_id, follower_fk=current_user.id).first():
        return flask.redirect("/")
    new_follow = FollowUser(id=str(uuid4()), followed_fk=user_id, follower_fk=current_user.id)
    db.session.add(new_follow)
    db.session.commit()
    return flask.redirect("/p/" + post_id)


@app.route("/post/unfollow/<user_id>/<post_id>")
@login_required
def unfollow_post_user(user_id, post_id):
    db.session.delete(FollowUser.query.filter_by(followed_fk=user_id, follower_fk=current_user.id).first())
    db.session.commit()
    return flask.redirect("/p/" + post_id)


@app.route("/account/unfollow/<user_id>")
@login_required
def unfollow_user(user_id):
    db.session.delete(FollowUser.query.filter_by(followed_fk=user_id, follower_fk=current_user.id).first())
    db.session.commit()
    return flask.redirect("/account/" + User.query.get(user_id).username)


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
            new_user = User(id=str(uuid4()), username=values["username"].replace(" ", ""),
                            password=bcrypt.generate_password_hash(values["password"]), email=values["email"],
                            fullname=values["phone_number"], latest_ip=flask.request.environ.get('HTTP_X_FORWARDED_FOR', flask.request.remote_addr),
                            balance=100)

            db.session.add(new_user)
            db.session.commit()

            referrer_id = flask.request.cookies.get("referrer")

            if len(referrer_id) > 3:
                new_referrer = Referral(id=str(uuid4()), referrer=referrer_id, referred_account=new_user.id)
                db.session.add(new_referrer)
                db.session.commit()

            login_user(new_user, remember=True)
            return reason


@app.route("/plutus/choose")
@login_required
def choose_account_plutus():
    accounts = []
    for i in flask.request.cookies.keys():
        if "user_cookie" in i:
            try:
                accounts.append({"username": i.split("&&")[1], "password": flask.request.cookies.get(i),
                                 "email": User.query.filter_by(username=i.split("&&")[1]).first().email})
            except AttributeError:
                resp = flask.make_response(flask.redirect("/"))
                resp.delete_cookie(i)
                return resp
    return flask.render_template("account/plutus_connect.html", accounts=accounts)


@app.route("/plutus/connect/<username>/<password>")
def plutus_connect(username, password):
    logout_user()
    user_login = User.query.filter_by(username=username).first()

    if bcrypt.check_password_hash(user_login.password, password):
        user_login.latest_ip = flask.request.environ.get('HTTP_X_FORWARDED_FOR', flask.request.remote_addr)
        db.session.commit()
        login_user(user_login, remember=True)
        return flask.redirect("/plutus/connect/option")

    return flask.redirect("/")


@app.route("/plutus/connect/option", methods=["POST", "GET"])
@login_required
def plutus_connect_option():
    if flask.request.method == "POST":
        try:
            if flask.request.values["convert_tokens"]:
                data_payload = {
                    "username": current_user.username,
                    "email": current_user.email,
                    "password": current_user.password,
                    "ga_balance": current_user.balance,
                    "latest_ip": current_user.latest_ip,
                    "secret_key": app.config["SECRET_KEY"]
                }
                current_user.balance = 0
                db.session.commit()
                requests.post("https://plutus.grandassembly.net/ga_connect", data=data_payload)
            else:
                data_payload = {
                    "username": current_user.username,
                    "email": current_user.email,
                    "password": current_user.password,
                    "ga_balance": 0,
                    "latest_ip": current_user.latest_ip,
                    "secret_key": app.config["SECRET_KEY"]
                }
                requests.post("https://plutus.grandassembly.net/ga_connect", data=data_payload)
        except:
            data_payload = {
                "username": current_user.username,
                "email": current_user.email,
                "password": current_user.password,
                "ga_balance": 0,
                "latest_ip": current_user.latest_ip,
                "secret_key": app.config["SECRET_KEY"]
            }
            requests.post("https://plutus.grandassembly.net/ga_connect", data=data_payload)
    return flask.render_template("account/plutus_option.html", user=current_user)


@app.route("/delete_post/<post_id>")
@login_required
def delete_post_user(post_id):
    post_to_delete = Post.query.get(post_id)
    if post_to_delete.creator_fk == current_user.id or current_user.is_admin:
        db.session.delete(post_to_delete)
        db.session.commit()

    return flask.redirect("/")


@app.route("/account/login", methods=["POST", "GET"])
def login():
    if flask.request.method == "POST":
        values = flask.request.values
        user_login = User.query.filter_by(username=values["username"]).first()

        if bcrypt.check_password_hash(user_login.password, values["password"]):
            user_login.latest_ip = flask.request.environ.get('HTTP_X_FORWARDED_FOR', flask.request.remote_addr)
            db.session.commit()
            login_user(user_login, remember=True)
            resp = flask.make_response(flask.redirect("/"))
            expire_date = datetime.now()
            expire_date = expire_date + timedelta(days=90)
            resp.set_cookie("user_cookie&&" + user_login.username, values["password"], expires=expire_date)
            return resp

    return flask.render_template("account/login.html")


@app.route("/account/choose")
@login_required
def choose_account():
    accounts = []
    for i in flask.request.cookies.keys():
        if "user_cookie" in i:
            try:
                accounts.append({"username": i.split("&&")[1], "password": flask.request.cookies.get(i),
                                 "email": User.query.filter_by(username=i.split("&&")[1]).first().email})
            except AttributeError:
                resp = flask.make_response(flask.redirect("/"))
                resp.delete_cookie(i)
                return resp
    return flask.render_template("account/switch_accounts.html", accounts=accounts)


@app.route("/account/change/<username>/<password>")
def change_account(username, password):
    logout_user()
    user_login = User.query.filter_by(username=username).first()

    if bcrypt.check_password_hash(user_login.password, password):
        user_login.latest_ip = flask.request.environ.get('HTTP_X_FORWARDED_FOR', flask.request.remote_addr)
        db.session.commit()
        login_user(user_login, remember=True)
        return flask.redirect("/")

    return flask.redirect("/")


@app.route("/account/register")
def register_account_ui():
    resp = flask.make_response(flask.render_template("account/register.html"))
    expire_date = datetime.now()
    expire_date = expire_date + timedelta(days=90)
    resp.set_cookie("referrer", flask.request.args.get("referrer", ""), expires=expire_date)
    return resp


@app.route("/account/logout")
def logout():
    logout_user()
    all_accounts = flask.request.cookies.keys()
    resp = flask.make_response(flask.redirect("/"))

    for i in all_accounts:
        resp.delete_cookie(i)

    return resp


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
    allowed_dates = []
    current_dt = datetime.today().date()

    while current_dt > datetime.today().date() - timedelta(days=14):
        allowed_dates.append(current_dt)
        current_dt = current_dt - timedelta(days=1)

    top_posts = Post.query.order_by(Post.net_votes.desc()).all()[:50]
    admins = User.query.filter_by(is_admin=True).all()

    for i in admins:
        temp_adm_post = Post.query.filter_by(creator_fk=i.id).all()
        for c in temp_adm_post:
            if c.post_date in allowed_dates:
                top_posts.insert(0, c)

    top_posts = list(set(top_posts))

    all_top_posts = [
        {
            "title": i.title,
            "text_body": " ".join(i.text_body.split(" ")[:15]).replace("&newline&", ""),
            "has_image": True if i.image_uri else False,
            "image_uri": i.image_uri,
            "creator_username": User.query.get(i.creator_fk).username,
            "net_votes": i.net_votes,
            "post_id": i.id,
            "is_video": False if not i.image_uri else "&video&" in i.image_uri,
            "has_test": Test.query.filter_by(post_fk=i.id).first() is not None
        } for i in top_posts
    ]

    return flask.jsonify(all_top_posts)


@app.route("/top_headers/load-post-batch")
def load_post_batch_headers():
    top_posts = Post.query.order_by(Post.net_votes.desc()).all()[:6]
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

    user_follows = FollowUser.query.filter_by(follower_fk=current_user.id).all()

    relevant_ads = []

    for i in user_follows:
        for c in Advert.query.filter(Advert.total_budget >= 0).all():
            if User.query.get(i.followed_fk).username in c.creators_alike.split("&&"):
                relevant_ads.append(c)

    relevant_ads.sort(key=lambda x: x.bid_target, reverse=True)

    using_ads = relevant_ads[:7]

    if len(follows) < 20:
        for i in user_follows:
            for c in Follow.query.filter_by(follower_fk=i.followed_fk).all():
                follows.append(c.followed_fk)

    allowed_dates = []
    allowed_posts = []

    current_date = datetime.today().date()

    while current_date > datetime.today().date() - timedelta(days=14):
        allowed_dates.append(current_date)
        current_date = current_date - timedelta(days=1)

    for i in allowed_dates:
        for c in Post.query.filter_by(post_date=i):
            allowed_posts.append(c)

    for i in allowed_posts:
        for c in user_follows:
            if c.followed_fk == i.creator_fk:
                if i not in follow_posts:
                    follow_posts.append(i)
        for c in follows:
            if "#" + c in i.tags.split("&&"):
                if i not in follow_posts:
                    follow_posts.append(i)

    follow_posts.sort(key=lambda x: x.net_votes, reverse=True)

    admins = User.query.filter_by(is_admin=True).all()

    if len(set(follow_posts)) < 1000:
        allowed_posts.sort(key=lambda x: x.net_votes, reverse=True)
        for i in allowed_posts:
            if i not in follow_posts:
                follow_posts.append(i)

    pagination_begin = int(paginate) if int(paginate) == 0 else (int(paginate) * 50)
    using_posts = follow_posts[pagination_begin:pagination_begin + 50]
    shift_right = 0

    for i in using_ads:
        i.total_budget -= i.bid_target / 1000
        i.budget_spent += i.bid_target / 1000
        i.total_views += 1

    db.session.commit()

    for i in range(len(using_posts)):
        if i % 3 == 0:
            try:
                using_posts.insert(i + shift_right, Post.query.get(using_ads[shift_right].id))
                shift_right += 1
            except IndexError:
                continue

    all_top_posts = [
        {
            "title": i.title,
            "text_body": " ".join(i.text_body.split(" ")[:15]).replace("&newline&", ""),
            "has_image": True if i.image_uri else False,
            "image_uri": i.image_uri,
            "creator_username": User.query.get(i.creator_fk).username + " - Sponsorlu" if i.id in [ad.id for ad in
                                                                                                   relevant_ads] else User.query.get(
                i.creator_fk).username,
            "net_votes": i.net_votes,
            "post_id": i.id,
            "is_video": False if not i.image_uri else "&video&" in i.image_uri,
            "has_test": Test.query.filter_by(post_fk=i.id).first() is not None
        } for i in using_posts
    ]

    return flask.jsonify(all_top_posts)


@app.route("/new/post", methods=["POST", "GET"])
@login_required
def new_post():
    if flask.request.method == "POST":
        if current_user.balance < 20 and not current_user.is_admin:
            return '''
                <script>
                    alert('Insufficient account balance')
                    document.location = '/trading/buy'
                <script>
            '''

        values = flask.request.values

        image = flask.request.files["image_file"]
        all_files = flask.request.files

        save_image_uuid = str(uuid4()) if not "video" in image.content_type else "&video&" + str(uuid4()) + "." + \
                                                                                 image.filename.split(".")[-1]

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

        new_post_add = Post(id=str(id_gen()), creator_fk=current_user.id, title=values["title"],
                            text_body=values["text_body"].replace("\n", " &newline& ").replace("\r", ""),
                            image_uri=str("/file_content/" + save_image_uuid) if len(image.filename) > 2 else None,
                            tags="&&".join(set(get_tags)), post_date=datetime.today())

        new_post_analytic = PostAnalytics(id=str(uuid4()), is_edited=False, post_fk=new_post_add.id, views=0)

        current_user.balance -= 20

        Supply.query.first().remaining_supply += 20

        db.session.add(new_post_add)
        db.session.add(new_post_analytic)

        if values.get("add_test", False):
            new_test = Test(id=str(uuid4()), outcomes=values["outcomes_and_points"], post_fk=new_post_add.id)
            for i in values["questions"].split("&&&&"):
                try:
                    new_question = Question(id=str(uuid4()), question_body=i.split("&&&")[0],
                                            answer_choices=i.split("&&&")[1], test_fk=new_test.id)

                    q_file = all_files[new_question.question_body]
                    q_file.save("file_content/" + new_question.id)

                    db.session.add(new_question)
                except IndexError:
                    continue
            db.session.add(new_test)
        elif values.get("add_list"):
            for i in values["questions"].split("&&&&"):
                try:
                    if len(i.split("&&&")[0]) < 3:
                        continue
                    new_entry = ListPoint(id=str(uuid4()), text_body=i.split("&&&")[0], post_fk=new_post_add.id)

                    q_file = all_files[new_entry.text_body]
                    q_file.save("file_content/" + new_entry.id)

                    db.session.add(new_entry)
                except IndexError:
                    continue
        elif values.get("add_poll", False):
            new_test = Test(id="poll-" + str(uuid4()), outcomes=values["outcomes_and_points"], post_fk=new_post_add.id)
            for i in values["questions"].split("&&&&"):
                try:
                    new_question = Question(id=str(uuid4()), question_body=i.split("&&&")[0],
                                            answer_choices=i.split("&&&")[1], test_fk=new_test.id)

                    q_file = all_files[new_question.question_body]
                    q_file.save("file_content/" + new_question.id)

                    db.session.add(new_question)
                except IndexError:
                    continue

            db.session.add(new_test)
        elif values.get("add_tok_poll", False):
            new_test = Test(id="poll-" + str(uuid4()), outcomes=values["outcomes_and_points"],
                            post_fk=new_post_add.id, is_poll_bet=True, end_date=datetime.today() + timedelta(days=3))
            for i in values["questions"].split("&&&&"):
                try:
                    new_question = Question(id=str(uuid4()), question_body=i.split("&&&")[0],
                                            answer_choices=i.split("&&&")[1], test_fk=new_test.id)

                    q_file = all_files[new_question.question_body]
                    q_file.save("file_content/" + new_question.id)

                    db.session.add(new_question)
                except IndexError:
                    continue

            db.session.add(new_test)

        db.session.commit()

        return flask.redirect("/")

    return flask.render_template("posts/new_post.html")


@app.route("/interact-poll/q=<question_id>", methods=["POST", "GET"])
@login_required
def answer_poll(question_id):
    get_test = Test.query.get(Question.query.get(question_id).test_fk)
    test_ended = False
    test_bet = get_test.is_poll_bet
    if get_test.is_poll_bet:
        test_ended = datetime.today().date() > get_test.end_date

    existing_answer = PollAnswer.query.filter_by(user_fk=current_user.id).filter_by(question_fk=question_id).first()
    poll_results = {}
    filter_q = Question.query.get(question_id)
    options = []

    for c in filter_q.answer_choices.split("&&"):
        options.append(c.split("##")[0])
    for i in options:
        get_result = len(PollAnswer.query.filter_by(question_fk=question_id).filter_by(given_answer=i).all())
        poll_results[i] = get_result
    if existing_answer:
        return flask.jsonify({
            "given_answer": existing_answer.given_answer,
            "is_answered": "positive",
            "results": poll_results,
            "qq_id": filter_q.question_body
        })

    if flask.request.method == "POST":
        new_poll_answer = PollAnswer(id=str(uuid4()), user_fk=current_user.id, question_fk=question_id,
                                     given_answer=flask.request.values["answer"])

        if test_bet and not test_ended:
            if current_user.balance >= 5:
                current_user.balance -= 5
            else:
                return "Cannot Process"
        db.session.add(new_poll_answer)
        db.session.commit()
        return flask.jsonify({
            "given_answer": new_poll_answer.given_answer,
            "is_answered": "negative",
            "results": poll_results,
            "qq_id": filter_q.question_body
        })

    return flask.jsonify({
        "given_answer": "N/A",
        "is_answered": "positive",
        "results": poll_results,
        "qq_id": filter_q.question_body
    })


@app.route("/advertise/<post_id>", methods=["POST", "GET"])
def advertise(post_id):
    if flask.request.method == "POST":
        values = flask.request.values
        new_advert = Advert(id=post_id, total_budget=values["total_budget"],
                            bid_target=values["bid_target"],
                            creators_alike=values["creators_alike"].replace("@", ""),
                            advert_type=values["advert_type"])
        card_info = {
            "number": values["card_number"],
            "cvc": values["cvc"],
            "exp_month": int(values["date"].split("/")[0]),
            "exp_year": int(values["date"].split("/")[1])
        }
        if int(int(values["bid_target"]) < 10):
            return '''
                <script>
                    alert('Hedef BGBM 10₺den az olamaz.')
                    window.location.reload()
                <script>
            '''
        if int(values["total_budget"]) < 50:
            return flask.redirect("/advertise/" + post_id)
        token_id = create_token(card_info).get("id")
        create_charge(int(values["total_budget"]), token_id)

        db.session.add(new_advert)
        db.session.commit()
        return flask.redirect("/view-post/" + post_id)

    return flask.render_template("advertising/new_advert.html", post=Post.query.get(post_id))


@app.route("/report/<post_id>", methods=["POST", "GET"])
@login_required
def report_post(post_id):
    if flask.request.method == "POST":
        new_mail = Message("Yeni Raporlama | GrandAssembly", sender="no-reply@grandassembly.net",
                           recipients=["omer.ozhan@grandassembly.net"])
        new_mail.body = f"@{current_user.username}, {Post.query.get(post_id).title} başlıklı içeriği şikayet etti. " \
                        f"https://grandassembly.net/p/{post_id} | Gerekçe: {flask.request.values['report_reason']}"
        mail.send(new_mail)

        return flask.redirect("/")

    return flask.render_template("posts/report_post.html")


@app.route("/view-post/<post_id>", methods=["POST", "GET"])
def view_post(post_id):
    view_count = ""
    post_analytics = PostAnalytics.query.filter_by(post_fk=post_id).first()
    if post_analytics and current_user.is_authenticated:
        new_view = PostView(id=str(uuid4()), viewer_fk=current_user.id, post_fk=post_id)

        if True and \
                len(PostView.query.filter_by(post_fk=post_id).filter_by(viewer_fk=current_user.id).all()) < 1:
            views_tmp = int(post_analytics.views)
            post_analytics.views = str(views_tmp + 1)
            if not (views_tmp + 1) == 0 and (views_tmp + 1) % 5 == 0:
                User.query.get(Post.query.get(post_id).creator_fk).balance += 1
            db.session.add(new_view)
            db.session.commit()

        if current_user.id == Post.query.get(post_id).creator_fk:
            views = int(post_analytics.views)
            money_made = int((views - (views % 5)) / 5)
            view_count = str(views) + " Görüntülenme | " + str(money_made) + " Görüntülenme Kazancı"

    if flask.request.method == "POST":
        new_comment = Comment(post_fk=post_id, content=flask.request.values["comment"], commenter=current_user.username,
                              id=str(uuid4()))
        db.session.add(new_comment)
        db.session.commit()
        return flask.redirect("/view-post/" + post_id)
    post_query = Post.query.get(post_id)
    test = Test.query.filter_by(post_fk=post_query.id).first()
    date_delta = ""
    if test:
        test_bet = test.is_poll_bet
        if test_bet:
            date_delta = "Tahminlerin Bitmesine " + str((test.end_date - datetime.today().date()).days) + " Gün Kaldı"
    else:
        test_bet = False
    if test:
        is_poll = test.id.split("-")[0] == "poll"
    else:
        is_poll = False

    questions = []
    qq_safe = []
    outcomes = {}
    if test:
        for outcome in test.outcomes.split("&&&"):
            try:
                outcomes[outcome.split("&&")[1]] = outcome.split("&&")[0]
            except IndexError:
                continue
        filter_q = Question.query.filter_by(test_fk=test.id).all()
        for i in filter_q:
            options = []
            for c in i.answer_choices.split("&&"):
                options.append({
                    "option": c.split("##")[0],
                    "value": c.split("##")[1]
                })
            tf_q = False
            number_of_ones = 0
            correct_option = None
            is_interactive_story = False

            for c in options:
                if "q:" in c.get("value"):
                    is_interactive_story = True

                    for opt in options:
                        opt["value"] = str(int(opt["value"].replace("q:", "")) - 1)

                    break

            for c in options:
                if not c.get("value") == "D" and not c.get("value") == "Y" and not c.get("value") == "":
                    number_of_ones = 9
                    break
                if c.get("value") == "D":
                    number_of_ones += 1
                    correct_option = c

            if number_of_ones == 1:
                tf_q = True

            questions.append({
                "question": i.question_body,
                "options": options,
                "is_last_question": filter_q.index(i) == len(filter_q) - 1,
                "has_image": exists("file_content/" + i.id),
                "id": i.id,
                "tf_q": tf_q,
                "correct_option": correct_option,
                "is_interactive_story": is_interactive_story
            })

            qq_safe.append({
                "id": i.id,
                "question": i.question_body,
            })

    post = {
        "title": post_query.title,
        "text_body": post_query.text_body,
        "has_image": True if post_query.image_uri else False,
        "image_uri": post_query.image_uri,
        "creator_username": User.query.get(post_query.creator_fk).username,
        "net_votes": post_query.net_votes,
        "post_id": post_query.id,
        "comments": Comment.query.filter_by(post_fk=post_id).all(),
        "is_video": False if not post_query.image_uri else "&video&" in post_query.image_uri,
        "tok_poll": test_bet,
        "date_delta": date_delta
    }

    can_delete_post = post_query.creator_fk == current_user.id or current_user.is_admin

    post_list = [{
        "text_body": i.text_body,
        "object_id": i.id,
        "has_image": exists("file_content/" + i.id),
    } for i in ListPoint.query.filter_by(post_fk=post_id).all()]

    creator = User.query.get(post_query.creator_fk)
    if current_user.is_authenticated:
        user_followed = FollowUser.query.filter_by(follower_fk=current_user.id).filter_by(
            followed_fk=creator.id).first() is not None
    else:
        user_followed = False
    is_verified = True if Compliant.query.filter_by(
        post_fk=post.get("creator_username")).first() else True if creator.is_admin else False

    return flask.render_template("posts/post_view.html", post=post, user=current_user, user_followed=user_followed,
                                 is_authenticated=current_user.is_authenticated, is_poll=is_poll, creator=creator,
                                 post_list=post_list,
                                 comments=Comment.query.filter_by(post_fk=post_id), is_verified=is_verified,
                                 qq_safe=qq_safe,
                                 view_count=view_count, questions=questions, outcomes=outcomes,
                                 questions_exist=len(questions) > 0, can_delete_post=can_delete_post)


# To do: Add timed betting to polls


@app.route("/moonvote/<post_id>")
@login_required
def moonvote(post_id):
    if current_user.balance < 1:
        return '''
            <script>
                alert("Insufficient account balance")
                document.location = '/trading/buy'
            </script>
        '''
    if len(MoonVote.query.filter_by(voter_fk=current_user.id).filter_by(post_fk=post_id).all()) > 10:
        return "Already voted"

    new_moonvote = MoonVote(id=str(uuid4()), voter_fk=current_user.id, post_fk=post_id)
    db.session.add(new_moonvote)
    Post.query.get(post_id).net_votes += 1

    current_user.balance -= 1

    db.session.commit()

    return flask.redirect("/view-post/" + post_id)


@app.route("/view-tag/<tag>")
def view_tag(tag):
    posts_in_tag = []

    for i in Post.query.order_by(Post.post_date.desc()).all():
        if i.post_date > datetime.today().date() - timedelta(days=14):
            if "#" + tag in i.tags.split("&&"):
                posts_in_tag.append(i)
        else:
            break

    posts_in_tag.sort(key=lambda x: x.net_votes, reverse=True)

    all_top_posts = [
        {
            "title": i.title,
            "text_body": " ".join(i.text_body.split(" ")[:15]).replace("&newline&", ""),
            "has_image": True if i.image_uri else False,
            "image_uri": i.image_uri,
            "creator_username": User.query.get(i.creator_fk).username,
            "net_votes": i.net_votes,
            "post_id": i.id,
            "is_video": False if not i.image_uri else "&video&" in i.image_uri
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
    tag_search = [i.tag_name for i in Tag.query.filter(Tag.tag_name.like("%" + search_term + "%")).all()]
    similar_users = ["@" + i.username for i in User.query.filter(User.username.like("%" + search_term + "%")).all()]
    for i in similar_users:
        tag_search.append(i)
    return flask.jsonify(tag_search)


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
                document.location = '/trading/buy'
            </script>
        '''
    if len(HellVote.query.filter_by(voter_fk=current_user.id).filter_by(post_fk=post_id).all()) > 10:
        return "Already voted"
    Post.query.get(post_id).net_votes -= 1

    new_hellvote = HellVote(id=str(uuid4()), voter_fk=current_user.id, post_fk=post_id)
    db.session.add(new_hellvote)

    current_user.balance -= 1

    Supply.query.first().remaining_supply += 1

    db.session.commit()

    return flask.redirect("/view-post/" + post_id)


@app.route("/get_trending_tags")
def get_trending_tags():
    posts = Post.query.filter_by(post_date=datetime.today().date()).all()

    for i in Post.query.filter_by(post_date=datetime.today().date() - timedelta(days=1)).all():
        posts.append(i)

    tags = []

    for i in posts:
        for c in i.tags.split("&&"):
            if len(c) > 3:
                tags.append(c)

    most_seen_tags = []

    if len(set(tags)) < 8:
        for i in tags:
            tags = list(set(tags))
            most_seen_tags.append(i)
    else:
        while len(most_seen_tags) < 8:
            chosen_tag = most_frequent(tags)
            most_seen_tags.append(chosen_tag)
            while chosen_tag in tags:
                tags.remove(chosen_tag)
    most_seen_tags = list(set(most_seen_tags))

    return flask.jsonify(most_seen_tags)


@app.route("/ads.txt")
def ads_txt():
    return flask.send_file("ads.txt")


@app.route("/file_content/<filename>")
def file_content(filename):
    return flask.send_file("file_content/" + filename)


@app.route("/verify_sms", methods=["POST", "GET"])
@login_required
def verify_sms():
    if flask.request.method == "POST":
        if current_user.did_verify_phone_number:
            return flask.redirect("/")
        authentication_code = AuthenticationSMS.query.filter_by(user_fk=current_user.id).all()[-1].sms_code
        if authentication_code == flask.request.values["sms_code"]:
            current_user.did_verify_phone_number = True
            current_user.balance += 500

            supply = Supply.query.first()
            supply.total_supply += 500

            get_affiliate = Referral.query.filter_by(referred_account=current_user.id).first()
            if get_affiliate:

                if current_user.latest_ip == User.query.filter_by(username=get_affiliate.referrer).first().latest_ip:
                    notify_referrer = Notification(notification_head="Öneriniz Geçersiz",
                                                   notification_body="Kendi kendinize öneride bulunamazsınız.",
                                                   is_read=False, onclick_link="/", user_fk=User.query.filter_by(username=get_affiliate.referrer).first().id,
                                                   id=str(uuid4()))
                    db.session.add(notify_referrer)
                    db.session.commit()
                else:
                    notify_referrer = Notification(notification_head="Teşekkürler!",
                                                   notification_body="Öneri linkiniz ile kayıt olan bir hesap email "
                                                                     "adresini doğruladı! 25₺ değerinde token kazandınız.",
                                                   is_read=False, onclick_link="/", user_fk=User.query.filter_by(username=get_affiliate.referrer).first().id,
                                                   id=str(uuid4()))
                    db.session.add(notify_referrer)
                    User.query.filter_by(username=get_affiliate.referrer).first().balance += 500

            db.session.commit()
            return flask.redirect("/")

    new_authentication = AuthenticationSMS(id=str(uuid4()), user_fk=current_user.id,
                                           sms_code=random.randint(999999, 9999999))
    db.session.add(new_authentication)
    db.session.commit()

    new_mail = Message("GrandAssembly onay kodunuz.", sender="no-reply@grandassembly.net",
                       recipients=[current_user.email])
    new_mail.html = generate_email("verification_code", new_authentication.sms_code)
    mail.send(new_mail)

    return flask.render_template("account/verify_sms.html")


@app.route("/trading/buy", methods=["POST", "GET"])
@login_required
def buy_token():
    used_cards = [{"last4": get_card_info(i.token).get("card").get("last4"), "card_token": i.token}
                  for i in CardToken.query.filter_by(user_fk=current_user.id).all()]
    if flask.request.method == "POST":
        values = flask.request.values
        card_info = {
            "number": values["card_number"],
            "cvc": values["cvc"],
            "exp_month": int(values["date"].split("/")[0]),
            "exp_year": int(values["date"].split("/")[1])
        }
        token_id = create_token(card_info).get("id")

        charge = create_charge(token_id=token_id, amount=get_coin_price() * int(values["coin_amount"]))

        new_card_token = CardToken(token=token_id, user_fk=current_user.id)
        db.session.add(new_card_token)

        current_user.balance += int(values["coin_amount"])

        db.session.commit()

        return flask.redirect("/")
    return flask.render_template("trading/buy_token.html", token_price=round(get_coin_price(), 5),
                                 current_user=current_user, used_cards=used_cards)


@app.route("/trading/buy_with_token/<token_id>/<amount>")
@login_required
def buy_with_token(token_id, amount):
    charge = create_charge(token_id=token_id, amount=get_coin_price() * int(amount))
    current_user.balance = int(amount)
    db.session.commit()
    return flask.redirect("/")


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

        new_payout = ReceiveOut(id=str(uuid4()), payment_instructions=values["payment_info"] + "/" + values["fullname"])

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


@app.route("/favicon.ico")
def favicon():
    return flask.send_file("static/grandassembly.png")
