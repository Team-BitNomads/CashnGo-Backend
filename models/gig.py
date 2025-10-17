from services.database_service import get_collection
from bson.objectid import ObjectId
import datetime

class Gig:
    collection_name = 'gigs'

    def __init__(self, title, description, price, required_skill_tag, employer_id, status="POSTED", applied_students=None, claimed_by=None, _id=None):
        self.title = title
        self.description = description
        self.price = float(price)
        self.required_skill_tag = required_skill_tag
        self.employer_id = str(employer_id) # Store as string for simplicity with ObjectId
        self.status = status # POSTED, ESCROWED, PAID, COMPLETED (if an additional state is needed)
        self.applied_students = applied_students if applied_students is not None else [] # List of student_ids
        self.claimed_by = claimed_by # student_id who claimed the gig
        self.created_at = datetime.datetime.utcnow()
        self._id = _id if _id else ObjectId()

    def to_dict(self):
        return {
            '_id': str(self._id),
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'required_skill_tag': self.required_skill_tag,
            'employer_id': self.employer_id,
            'status': self.status,
            'applied_students': self.applied_students,
            'claimed_by': self.claimed_by,
            'created_at': self.created_at.isoformat()
        }

    @staticmethod
    def from_dict(data):
        return Gig(
            title=data.get('title'),
            description=data.get('description'),
            price=data.get('price'),
            required_skill_tag=data.get('required_skill_tag'),
            employer_id=data.get('employer_id'),
            status=data.get('status', "POSTED"),
            applied_students=data.get('applied_students'),
            claimed_by=data.get('claimed_by'),
            _id=data.get('_id')
        )

    def save(self):
        gigs_collection = get_collection(self.collection_name)
        gig_data = self.to_dict()
        if '_id' in gig_data:
            gig_data['_id'] = ObjectId(gig_data['_id'])
        
        if gigs_collection.find_one({'_id': self._id}):
            gigs_collection.update_one({'_id': self._id}, {'$set': gig_data})
        else:
            gigs_collection.insert_one(gig_data)
        return self

    @staticmethod
    def find_by_id(gig_id):
        gigs_collection = get_collection(Gig.collection_name)
        gig_data = gigs_collection.find_one({'_id': ObjectId(gig_id)})
        return Gig.from_dict(gig_data) if gig_data else None

    @staticmethod
    def find_all():
        gigs_collection = get_collection(Gig.collection_name)
        return [Gig.from_dict(gig) for gig in gigs_collection.find()]

    @staticmethod
    def find_by_employer(employer_id):
        gigs_collection = get_collection(Gig.collection_name)
        return [Gig.from_dict(gig) for gig in gigs_collection.find({'employer_id': str(employer_id)})]