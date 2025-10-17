from services.database_service import get_collection
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

class User:
    collection_name = 'users'

    def __init__(self, username, email, password_hash, role, primary_skill=None, badges=None, wallet_balance=0.0, verification_status="Unverified", _id=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role 
        self.primary_skill = primary_skill
        self.badges = badges if badges is not None else []
        self.wallet_balance = wallet_balance
        self.verification_status = verification_status
        self._id = _id if _id else ObjectId()

    def to_dict(self, include_password=False):
        data = {
            '_id': str(self._id),
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'primary_skill': self.primary_skill,
            'badges': self.badges,
            'wallet_balance': self.wallet_balance,
            'verification_status': self.verification_status
        }
        if include_password:
            data['password_hash'] = self.password_hash
        return data

    @staticmethod
    def from_dict(data):
        return User(
            username=data.get('username'),
            email=data.get('email'),
            password_hash=data.get('password_hash'),
            role=data.get('role'),
            primary_skill=data.get('primary_skill'),
            badges=data.get('badges'),
            wallet_balance=data.get('wallet_balance'),
            verification_status=data.get('verification_status', "Unverified"),
            _id=data.get('_id')
        )

    def save(self):
        users_collection = get_collection(self.collection_name)
        user_data = self.to_dict(include_password=True)
        if '_id' in user_data:
            user_data['_id'] = ObjectId(user_data['_id'])
        
        if users_collection.find_one({'_id': self._id}):
            users_collection.update_one({'_id': self._id}, {'$set': user_data})
        else:
            users_collection.insert_one(user_data)
        return self

    @staticmethod
    def find_by_id(user_id):
        users_collection = get_collection(User.collection_name)
        user_data = users_collection.find_one({'_id': ObjectId(user_id)})
        return User.from_dict(user_data) if user_data else None

    @staticmethod
    def find_by_email(email):
        users_collection = get_collection(User.collection_name)
        user_data = users_collection.find_one({'email': email})
        return User.from_dict(user_data) if user_data else None

    @staticmethod
    def verify_password(hashed_password, password):
        return check_password_hash(hashed_password, password)

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password, method='pbkdf2:sha256')

    def add_badge(self, badge_id):
        if badge_id not in self.badges:
            self.badges.append(badge_id)
            self.save() # Persist the change

    def update_wallet_balance(self, amount):
        self.wallet_balance += amount
        self.save() # Persist the change