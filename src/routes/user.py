from flask import Blueprint, request, jsonify
from models.user import db, User

# Create blueprint for user routes (template)
user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users (template route)"""
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user (template route)"""
    try:
        data = request.get_json()
        user = User(
            username=data.get('username'),
            email=data.get('email')
        )
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    """Get a specific user (template route)"""
    try:
        user = User.query.get_or_404(id)
        return jsonify(user.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
