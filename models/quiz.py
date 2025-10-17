from services.database_service import get_collection
from bson.objectid import ObjectId
import datetime

class Quiz:
    collection_name = 'quizzes'

    def __init__(self, skill_name, questions, student_id, _id=None):
        self.skill_name = skill_name
        self.questions = questions  # List of dicts: [{'text': str, 'options': list, 'correct_answer_index': int}, ...]
        self.student_id = str(student_id)  # Student who generated the quiz
        self.created_at = datetime.datetime.utcnow()
        self._id = _id if _id else ObjectId()

    def to_dict(self):
        return {
            '_id': str(self._id),
            'skill_name': self.skill_name,
            'questions': self.questions,
            'student_id': self.student_id,
            'created_at': self.created_at.isoformat()
        }

    @staticmethod
    def from_dict(data):
        return Quiz(
            skill_name=data.get('skill_name'),
            questions=data.get('questions'),
            student_id=data.get('student_id'),
            _id=data.get('_id')
        )

    def save(self):
        quizzes_collection = get_collection(self.collection_name)
        quiz_data = self.to_dict()
        if '_id' in quiz_data:
            quiz_data['_id'] = ObjectId(quiz_data['_id'])
        
        if quizzes_collection.find_one({'_id': self._id}):
            quizzes_collection.update_one({'_id': self._id}, {'$set': quiz_data})
        else:
            quizzes_collection.insert_one(quiz_data)
        return self

    @staticmethod
    def find_by_id(quiz_id):
        quizzes_collection = get_collection(Quiz.collection_name)
        quiz_data = quizzes_collection.find_one({'_id': ObjectId(quiz_id)})
        return Quiz.from_dict(quiz_data) if quiz_data else None