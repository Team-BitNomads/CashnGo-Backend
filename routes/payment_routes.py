from flask import Blueprint, jsonify, request
from routes.auth_routes import token_required, role_required
from models.gig import Gig

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

@payment_bp.route('/wallet/<action>', methods=['POST'])
@token_required
@role_required(['Student', 'Employer'])
def update_wallet(current_user, action):

    data = request.get_json()

    amount = data.get('amount')
    if not amount:
        return jsonify({'message': 'Amount is required for wallet top-up.'}), 400
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'message': 'Top-up amount must be a positive number.'}), 400
    except ValueError:
        return jsonify({'message': 'Amount must be a valid number.'}), 400
    
    if action == 'topup':
        current_user.wallet_balance += amount
        current_user.save()
        return jsonify({'message': 'Top-up successful!', 'new_balance': current_user.wallet_balance}), 200

    elif action == 'withdraw':
        if amount > float(current_user.wallet_balance):
            return jsonify({'message': 'Insufficient wallet balance for withdrawal.'}), 400

        if current_user.role == 'Employer':
            employer_gigs_price = 0
            employer_gigs = Gig.find_by_employer(current_user._id)
            for gig in employer_gigs:
                if gig.status in ['POSTED', 'ESCROWED']:
                    employer_gigs_price += gig.price
            available_balance = float(current_user.wallet_balance) - employer_gigs_price
            if amount > available_balance:
                return jsonify({'message': 'Insufficient available balance for withdrawal due to posted/escrowed gigs.'}), 400

        current_user.wallet_balance -= amount
        current_user.save()
        return jsonify({'message': 'Withdrawal successful!', 'new_balance': current_user.wallet_balance}), 200
    
    else:
        return jsonify({'message': 'Invalid action. Use "topup" or "withdraw".'}), 400