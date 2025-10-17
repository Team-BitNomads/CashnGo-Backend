from flask import Blueprint, request, jsonify, current_app
from models.gig import Gig
from models.user import User
from models.quiz import Quiz
from routes.auth_routes import token_required, role_required
from services.ai_service import generate_quiz, AIServiceError
from bson.objectid import ObjectId

gig_bp = Blueprint('gig_bp', __name__)

# Post Gig
@gig_bp.route('/', methods=['POST'])
@token_required
@role_required(['Employer'])
def post_gig(current_user):
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid JSON data.'}), 400

    title = data.get('title')
    description = data.get('description')
    price = data.get('price')
    required_skill_tag = data.get('required_skill_tag')

    if not all([title, description, price, required_skill_tag]):
        return jsonify({'message': 'Missing required fields: title, description, price, required_skill_tag'}), 400
    
    try:
        price = float(price)
        if price <= 0:
            return jsonify({'message': 'Price must be a positive number.'}), 400
    except ValueError:
        return jsonify({'message': 'Price must be a valid number.'}), 400

    new_gig = Gig(
        title=title,
        description=description,
        price=price,
        required_skill_tag=required_skill_tag,
        employer_id=str(current_user._id)
    )
    new_gig.save()
    return jsonify({'message': 'Gig posted successfully!', 'gig': new_gig.to_dict()}), 201

# Get Gigs
@gig_bp.route('/', methods=['GET'])
@token_required
def get_gigs(current_user):
    gigs = Gig.find_all()

    gigs_data = []
    for gig in gigs:
        gig_dict = gig.to_dict()
        if current_user.role == 'Student':
            gig_dict['is_unlocked'] = any(badge.lower() in gig.required_skill_tag.lower() for badge in current_user.badges)
        else:
            gig_dict['is_unlocked'] = True
        gigs_data.append(gig_dict)

    return jsonify(gigs_data), 200

# Get Gig Details
@gig_bp.route('/<gig_id>', methods=['GET'])
@token_required
def get_gig_details(current_user, gig_id):
    gig = Gig.find_by_id(gig_id)
    if not gig:
        return jsonify({'message': 'Gig not found.'}), 404

    gig_dict = gig.to_dict()
    if current_user.role == 'Student':
        gig_dict['is_unlocked'] = any(badge.lower() in gig.required_skill_tag.lower() for badge in current_user.badges)
    else:
        gig_dict['is_unlocked'] = True

    return jsonify(gig_dict), 200

# Gig Application
@gig_bp.route('/<gig_id>/apply', methods=['POST'])
@token_required
@role_required(['Student'])
def apply_for_gig(current_user, gig_id):
    gig = Gig.find_by_id(gig_id)
    if not gig:
        return jsonify({'message': 'Gig not found.'}), 404

    if not any(badge.lower() in gig.required_skill_tag.lower() for badge in current_user.badges):
        return jsonify({'message': 'You do not have the required skill badge for this gig.'}), 403

    if gig.status != 'POSTED':
        return jsonify({'message': 'Gig is not available for application.'}), 400
    
    if str(current_user._id) in gig.applied_students:
        return jsonify({'message': 'You have already applied for this gig.'}), 409

    # Comment made to identify where the employer approval check would come in, for now set to auto claim during application
    gig.claimed_by = str(current_user._id)
    gig.status = 'ESCROWED'
    gig.save()

    return jsonify({'message': 'Successfully applied for and claimed gig!', 'gig': gig.to_dict()}), 200

# Gig Completion Approval
@gig_bp.route('/<gig_id>/approve', methods=['POST'])
@token_required
@role_required(['Employer'])
def approve_payment(current_user, gig_id):
    gig = Gig.find_by_id(gig_id)
    if not gig:
        return jsonify({'message': 'Gig not found.'}), 404

    if gig.employer_id != str(current_user._id):
        return jsonify({'message': 'You are not the employer for this gig.'}), 403

    if gig.status != 'ESCROWED':
        return jsonify({'message': 'Gig is not in an escrowed state for approval.'}), 400
    
    if not gig.claimed_by:
        return jsonify({'message': 'No student has claimed this gig yet.'}), 400

    student = User.find_by_id(gig.claimed_by)
    if not student:
        return jsonify({'message': 'Assigned student not found.'}), 404

    student.update_wallet_balance(gig.price)
    gig.status = 'PAID'
    gig.save()

    return jsonify({
        'message': f'Payment of {gig.price} approved and transferred to {student.username}.',
        'gig': gig.to_dict(),
        'student_wallet_balance': student.wallet_balance
    }), 200

# AI Service Integration (BE-4) & Skill-Synth Trigger (P1 Feature)
# Quiz Generation
@gig_bp.route('/skill-synth/generate-quiz', methods=['POST'])
@token_required
@role_required(['Student'])
def trigger_skill_synth_quiz(current_user):
    
    if not current_user.primary_skill:
        return jsonify({'message': 'Your profile must have a primary skill to generate a quiz.'}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid JSON data.'}), 400
    
    target_skill_gap = data.get('target_skill_gap')
    if not target_skill_gap:
        return jsonify({'message': 'Missing required field: target_skill_gap.'}), 400

    try:
        # AI service (AI Micro-Quiz Generation - P1 Feature)
        quiz_data = generate_quiz(
            student_skills=[current_user.primary_skill],
            target_skill_gap=target_skill_gap
        )

        quiz = Quiz(
            skill_name=quiz_data['skill_name'],
            questions=quiz_data['questions'],
            student_id=str(current_user._id)
        )
        quiz.save()

        quiz_data['quiz_id'] = str(quiz._id)

        return jsonify(quiz_data), 200
    except AIServiceError as e:
        current_app.logger.error(f"AI Service Error: {e}")
        return jsonify({'message': f'Failed to generate quiz: {e}'}), 500
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred during quiz generation: {e}")
        return jsonify({'message': 'An unexpected error occurred while generating the quiz.'}), 500

# Quiz Submission
@gig_bp.route('/skill-synth/submit-quiz', methods=['POST'])
@token_required
@role_required(['Student'])
def submit_skill_synth_quiz(current_user):
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid JSON data.'}), 400

    quiz_id = data.get('quiz_id')
    skill_name = data.get('skill_name')
    answers = data.get('answers')

    if not all([quiz_id, skill_name, answers]):
        return jsonify({'message': 'Missing required fields: quiz_id, skill_name, answers.'}), 400
    if not isinstance(answers, list) or len(answers) != 3:
        return jsonify({'message': 'Answers must be a list of 3 indices.'}), 400

    quiz = Quiz.find_by_id(quiz_id)
    if not quiz:
        return jsonify({'message': 'Quiz not found.'}), 404

    if quiz.student_id != str(current_user._id):
        return jsonify({'message': 'You are not authorized to submit this quiz.'}), 403

    if quiz.skill_name != skill_name:
        return jsonify({'message': 'Skill name mismatch.'}), 400

    correct_answers = [q['correct_answer_index'] for q in quiz.questions]
    if answers == correct_answers:
        current_user.add_badge(skill_name)
        return jsonify({'message': f'Quiz submitted successfully! You have earned the {skill_name} badge.', 'badges': current_user.badges}), 200
    else:
        return jsonify({'message': 'Quiz failed. You did not earn the badge. Try again.'}), 200