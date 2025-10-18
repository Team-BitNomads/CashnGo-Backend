import requests
import json
import re
from flask import current_app

class AIServiceError(Exception):
    pass


def generate_quiz(student_skills: str, target_skill_gap: str) -> dict:
    """
    Generate a skill-based quiz using OpenRouter (Gemini 2.5 Pro model).
    Enforces a strict JSON-only output and validates structure.
    Retries once if the model output isn't valid JSON.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {current_app.config['OPEN_API_KEY']}",
        "Content-Type": "application/json",
    }

    def build_payload(clarify=False):
        system_prompt = (
            "You are an AI quiz generator. "
            "You must return a valid JSON object ONLY — no explanations, no markdown, no extra text.\n\n"
            "The JSON must follow this schema:\n"
            "{\n"
            '  \"quiz_id\": \"string\",\n'
            '  \"skill_name\": \"string\",\n'
            '  \"questions\": [\n'
            "    {\n"
            '      \"text\": \"string\",\n'
            '      \"options\": [\"string\", \"string\", \"string\", \"string\"],\n'
            '      \"correct_answer_index\": integer (0-3)\n'
            "    }, ... (exactly 3 questions)\n"
            "  ]\n"
            "}\n\n"
            "Return nothing but this JSON."
        )
        if clarify:
            system_prompt += "\n\nREMEMBER: Do NOT wrap JSON in ```json or any code block. Output pure JSON only."

        user_prompt = (
            f"Generate a quiz for a student with skills: {student_skills}. "
            f"The quiz should focus on testing their skill in: {target_skill_gap}."
        )

        return {
            "model": "google/gemini-2.5-pro",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
        }

    def parse_json_response(content: str) -> dict:
        """Try to safely parse JSON, cleaning if wrapped in markdown."""
        content = content.strip()
        if content.startswith("```"):
            content = re.sub(r"^```(json)?", "", content)
            content = re.sub(r"```$", "", content)
        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            content = json_match.group(0)
        return json.loads(content)

    def call_openrouter(payload):
        response = requests.post(url, headers=headers, json=payload, timeout=25)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    try:
        content = call_openrouter(build_payload(clarify=False))
        quiz_data = parse_json_response(content)
    except Exception:
        try:
            content = call_openrouter(build_payload(clarify=True))
            quiz_data = parse_json_response(content)
        except Exception as e:
            raise AIServiceError(f"OpenRouter returned invalid or non-JSON response after retry: {e}")

    # === Data Validation ===
    required_keys = ["quiz_id", "skill_name", "questions"]
    if not all(key in quiz_data for key in required_keys):
        raise AIServiceError("Malformed quiz data: missing required keys.")
    if not isinstance(quiz_data["questions"], list) or len(quiz_data["questions"]) != 3:
        raise AIServiceError("Malformed quiz data: must have exactly 3 questions.")
    for q in quiz_data["questions"]:
        if not all(k in q for k in ["text", "options", "correct_answer_index"]):
            raise AIServiceError("Malformed quiz data: question missing required fields.")
        if not isinstance(q["options"], list) or len(q["options"]) != 4:
            raise AIServiceError("Malformed quiz data: each question must have 4 options.")
        if not isinstance(q["correct_answer_index"], int) or not (0 <= q["correct_answer_index"] < 4):
            raise AIServiceError("Malformed quiz data: invalid correct_answer_index.")

    return quiz_data
