from flask import Blueprint, request, jsonify
from models.user import db
from models.assessment import DisasterAssessment

# Create blueprint for basic assessment routes
assessment_bp = Blueprint('assessment', __name__)

@assessment_bp.route('/assessments', methods=['GET'])
def get_assessments():
    """Get all assessments (basic route without Swagger)"""
    try:
        assessments = DisasterAssessment.query.all()
        return jsonify([assessment.to_dict() for assessment in assessments])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assessment_bp.route('/assessments', methods=['POST'])
def create_assessment():
    """Create a new assessment (basic route without Swagger)"""
    try:
        data = request.get_json()
        assessment = DisasterAssessment.from_dict(data)
        db.session.add(assessment)
        db.session.commit()
        return jsonify(assessment.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assessment_bp.route('/assessments/<int:id>', methods=['GET'])
def get_assessment(id):
    """Get a specific assessment (basic route without Swagger)"""
    try:
        assessment = DisasterAssessment.query.get_or_404(id)
        return jsonify(assessment.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assessment_bp.route('/assessments/<int:id>', methods=['PUT'])
def update_assessment(id):
    """Update an assessment (basic route without Swagger)"""
    try:
        assessment = DisasterAssessment.query.get_or_404(id)
        data = request.get_json()
        
        # Update fields
        for key, value in data.items():
            if hasattr(assessment, key):
                setattr(assessment, key, value)
        
        db.session.commit()
        return jsonify(assessment.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assessment_bp.route('/assessments/<int:id>', methods=['DELETE'])
def delete_assessment(id):
    """Delete an assessment (basic route without Swagger)"""
    try:
        assessment = DisasterAssessment.query.get_or_404(id)
        db.session.delete(assessment)
        db.session.commit()
        return jsonify({'message': 'Assessment deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
