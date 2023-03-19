from app import db, app, Supply, SuspendedAccount, User, bcrypt
from sys import argv
from uuid import uuid4
from datetime import datetime

suspension_reasons = {
    "community_guidelines": "You have violated some of our community guidelines.",
    "advertising": "Professional advertising is strictly prohibited, you can share about your product but mass "
                   "advertising is not cool!",
    "other": "You account has been suspended, please contact support for more details."
}

with app.app_context():
    if argv[1] == "create-db":
        db.create_all()

        new_supply = Supply(id=str(uuid4))

        db.session.add(new_supply)
        db.session.commit()

        print("created db")
    elif argv[1] == "drop-db":
        db.drop_all()
        print("dropped db")

    elif argv[1] == "suspend-user":
        new_suspension = SuspendedAccount(id=str(uuid4()), reason_of_suspension=suspension_reasons.get(argv[3]),
                                          suspended_account_fk=argv[2], suspension_date=datetime.today())
        db.session.add(new_suspension)
        db.session.commit()

    elif argv[1] == "remove-suspension":
        db.session.delete(SuspendedAccount.query.filter_by(suspended_account_fk=argv[2]).first())
        db.session.commit()

    elif argv[1] == "make-admin":
        User.query.filter_by(username=argv[2]).first().is_admin = True
        db.session.commit()

    elif argv[1] == "change-username":
        User.query.filter_by(username=argv[2]).first().password = bcrypt.generate_password_hash(argv[3])
        User.query.filter_by(username=argv[2]).first().username = argv[3]
        db.session.commit()
