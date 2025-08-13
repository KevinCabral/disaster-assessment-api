from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# Import db from user module
from .user import db

class DisasterAssessment(db.Model):
    __tablename__ = 'disaster_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    responsible_name = db.Column(db.String(200), nullable=False)
    document_number = db.Column(db.String(50), nullable=False)
    phone_contact = db.Column(db.String(20), nullable=False)
    household_members = db.Column(db.Integer, nullable=False)
    vulnerable_groups = db.Column(db.Text)  # JSON string for list of vulnerable groups
    full_address = db.Column(db.Text, nullable=False)
    reference_point = db.Column(db.String(500))
    gps_latitude = db.Column(db.Float)
    gps_longitude = db.Column(db.Float)
    structure_type = db.Column(db.String(50), nullable=False)
    damage_level = db.Column(db.String(20), nullable=False)
    losses = db.Column(db.Text)  # JSON string for list of losses
    losses_other = db.Column(db.Text)
    evidence_files = db.Column(db.Text)  # JSON string for list of file paths
    urgent_need = db.Column(db.String(50), nullable=False)
    urgent_need_other = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<DisasterAssessment {self.id} - {self.responsible_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'responsible_name': self.responsible_name,
            'document_number': self.document_number,
            'phone_contact': self.phone_contact,
            'household_members': self.household_members,
            'vulnerable_groups': json.loads(self.vulnerable_groups) if self.vulnerable_groups else [],
            'full_address': self.full_address,
            'reference_point': self.reference_point,
            'gps_latitude': self.gps_latitude,
            'gps_longitude': self.gps_longitude,
            'structure_type': self.structure_type,
            'damage_level': self.damage_level,
            'losses': json.loads(self.losses) if self.losses else [],
            'losses_other': self.losses_other,
            'evidence_files': json.loads(self.evidence_files) if self.evidence_files else [],
            'urgent_need': self.urgent_need,
            'urgent_need_other': self.urgent_need_other,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data):
        """Create a DisasterAssessment instance from a dictionary"""
        assessment = cls()
        assessment.responsible_name = data.get('responsible_name')
        assessment.document_number = data.get('document_number')
        assessment.phone_contact = data.get('phone_contact')
        assessment.household_members = data.get('household_members')
        assessment.vulnerable_groups = json.dumps(data.get('vulnerable_groups', []))
        assessment.full_address = data.get('full_address')
        assessment.reference_point = data.get('reference_point')
        assessment.gps_latitude = data.get('gps_latitude')
        assessment.gps_longitude = data.get('gps_longitude')
        assessment.structure_type = data.get('structure_type')
        assessment.damage_level = data.get('damage_level')
        assessment.losses = json.dumps(data.get('losses', []))
        assessment.losses_other = data.get('losses_other')
        assessment.evidence_files = json.dumps(data.get('evidence_files', []))
        assessment.urgent_need = data.get('urgent_need')
        assessment.urgent_need_other = data.get('urgent_need_other')
        return assessment
