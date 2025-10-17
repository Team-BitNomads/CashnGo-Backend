import requests
import json
from flask import current_app

class AIServiceError(Exception):
    pass

def generate_quiz(student_skills: list, target_skill_gap: str) -> dict:
    ai_service_url = f"{current_app.config['AI_SERVICE_BASE_URL']}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "student_skills": student_skills,
        "target_skill_gap": target_skill_gap
    }

    try:
        response = requests.post(ai_service_url, headers=headers, json=payload, timeout=10)

        response.raise_for_status()
        
        quiz_data = response.json()

        # Data Validation
        required_keys = ['quiz_id', 'skill_name', 'questions']
        if not all(key in quiz_data for key in required_keys):
            raise AIServiceError("AI service returned malformed quiz data: missing required keys.")
        if not isinstance(quiz_data['questions'], list) or not len(quiz_data['questions']) == 3:
            raise AIServiceError("AI service returned malformed quiz data: questions array is invalid.")
        for q in quiz_data['questions']:
            if not all(k in q for k in ['text', 'options', 'correct_answer_index']):
                raise AIServiceError("AI service returned malformed quiz data: question object invalid.")
            if not isinstance(q['options'], list) or not len(q['options']) == 4:
                raise AIServiceError("AI service returned malformed quiz data: question options invalid.")
            if not isinstance(q['correct_answer_index'], int) or not (0 <= q['correct_answer_index'] < 4):
                raise AIServiceError("AI service returned malformed quiz data: correct_answer_index invalid.")

        return quiz_data

    except requests.exceptions.Timeout:
        raise AIServiceError("AI service call timed out.")
    except requests.exceptions.ConnectionError:
        raise AIServiceError("Could not connect to the AI service. Is it running?")
    except requests.exceptions.RequestException as e:
        raise AIServiceError(f"Error calling AI service: {e}")
    except json.JSONDecodeError:
        raise AIServiceError("AI service returned invalid JSON response.")
    except Exception as e:
        raise AIServiceError(f"An unexpected error occurred processing AI service response: {e}")