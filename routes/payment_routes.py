from flask import Blueprint, jsonify
from routes.auth_routes import token_required, role_required

payment_bp = Blueprint('payment_bp', __name__)

@payment_bp.route('/wallet', methods=['GET'])
@token_required
@role_required(['Student', 'Employer'])
def get_wallet_balance(current_user):
    return jsonify({
        'user_id': str(current_user._id),
        'username': current_user.username,
        'wallet_balance': current_user.wallet_balance
    }), 200