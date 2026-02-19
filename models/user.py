from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId


class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.password_hash = user_data['password_hash']
        self.email = user_data.get('email', '')
        self.role = user_data.get('role', 'admin')
        self.created_at = user_data.get('created_at')

    @staticmethod
    def create(db, username, password, email=''):
        user_doc = {
            'username': username,
            'password_hash': generate_password_hash(password),
            'email': email,
            'role': 'admin',
            'created_at': datetime.now(timezone.utc),
        }
        result = db.users.insert_one(user_doc)
        user_doc['_id'] = result.inserted_id
        return User(user_doc)

    @staticmethod
    def find_by_username(db, username):
        doc = db.users.find_one({'username': username})
        return User(doc) if doc else None

    @staticmethod
    def find_by_id(db, user_id):
        doc = db.users.find_one({'_id': ObjectId(user_id)})
        return User(doc) if doc else None

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


def load_user_by_id(user_id):
    from app import get_db
    db = get_db()
    return User.find_by_id(db, user_id)
