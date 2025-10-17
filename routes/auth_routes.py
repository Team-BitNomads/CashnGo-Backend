from flask import Blueprint, request, jsonify, current_app
from models.user import User
import jwt
import datetime
from functools import wraps

auth_bp = Blueprint('auth_bp', __name__)

# Helper decorators
# For Auth Required Endpoints
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.find_by_id(data['public_id'])
            if not current_user:
                return jsonify({'message': 'Token is invalid: User not found!'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            return jsonify({'message': f'An error occurred: {e}'}), 500

        return f(current_user, *args, **kwargs)
    return decorated

# For Role Required Endpoints
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if current_user.role not in allowed_roles:
                return jsonify({'message': 'Access denied: Insufficient role.'}), 403
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

# User Registration
@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid JSON data.'}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    primary_skill = data.get('primary_skill')

    if not all([username, email, password, role]):
        return jsonify({'message': 'Missing required fields: username, email, password, role'}), 400

    if role not in ['Student', 'Employer']:
        return jsonify({'message': 'Invalid role. Must be "Student" or "Employer".'}), 400

    if User.find_by_email(email):
        return jsonify({'message': 'User with this email already exists.'}), 409

    hashed_password = User.hash_password(password)

    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        role=role,
        primary_skill=primary_skill if role == 'Student' else None,
        verification_status="Verified" if current_app.config.get('MOCK_VERIFICATION', False) else "Unverified"
    )
    new_user.save()

    if current_app.config.get('MOCK_VERIFICATION', False):
        new_user.verification_status = "Verified"
        new_user.save()


    return jsonify({'message': 'User created successfully!', 'user_id': str(new_user._id)}), 201

# User Login
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid JSON data.'}), 400

    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'message': 'Missing required fields: email, password'}), 400

    user = User.find_by_email(email)

    if not user or not User.verify_password(user.password_hash, password):
        return jsonify({'message': 'Invalid email or password.'}), 401

    token = jwt.encode(
        {
            'public_id': str(user._id),
            'role': user.role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES_SECONDS'])
        },
        current_app.config['SECRET_KEY'],
        algorithm="HS256"
    )

    return jsonify({'token': token, 'message': 'Logged in successfully!', 'user': user.to_dict()}), 200

# Current User Profile (Get, Update)
@auth_bp.route('/profile', methods=['GET', 'PATCH'])
@token_required
def get_user_profile(current_user):
    if request.method == 'GET':
        return jsonify(current_user.to_dict()), 200
    elif request.method == 'PATCH':
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided.'}), 400

        if 'username' in data:
            current_user.username = data.get('username')
        if 'email' in data:
            new_email = data.get('email')
            if User.find_by_email(new_email) and new_email != current_user.email:
                return jsonify({'message': 'Email already in use.'}), 409
            current_user.email = new_email
        if 'role' in data:
            new_role = data.get('role')
            if new_role not in ['Student', 'Employer']:
                return jsonify({'message': 'Invalid role.'}), 400
            current_user.role = new_role
        if 'primary_skill' in data:
            if current_user.role == 'Student':
                current_user.primary_skill = data.get('primary_skill')
            else:
                return jsonify({'message': 'Primary skill can only be set for Students.'}), 400

        current_user.save()
        return jsonify({'message': 'Profile updated successfully.', 'user': current_user.to_dict()}), 200

# Get Any User Profile
@auth_bp.route('/users/<user_id>', methods=['GET'])
@token_required
@role_required(['Employer', 'Student'])
def get_any_user_profile(current_user, user_id):
    user = User.find_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found.'}), 404
    return jsonify(user.to_dict()), 200

# Update Password
@auth_bp.route('/update_password', methods=['PATCH'])
@token_required
def update_password(current_user):
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided.'}), 400

    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({'message': 'Current password and new password are required.'}), 400

    if not User.verify_password(current_user.password_hash, current_password):
        return jsonify({'message': 'Current password is incorrect.'}), 401

    current_user.password_hash = User.hash_password(new_password)
    current_user.save()

    return jsonify({'message': 'Password updated successfully.'}), 200