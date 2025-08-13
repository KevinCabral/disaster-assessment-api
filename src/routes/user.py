from flask import Blueprint, request, jsonify
from models.user import db, Usuario

# Create blueprint for user routes (template)
usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route('/usuarios', methods=['GET'])
def obter_usuarios():
    """Obter todos os utilizadores (rota modelo)"""
    try:
        usuarios = Usuario.query.all()
        return jsonify([usuario.to_dict() for usuario in usuarios])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@usuario_bp.route('/usuarios', methods=['POST'])
def criar_usuario():
    """Criar um novo utilizador (rota modelo)"""
    try:
        data = request.get_json()
        usuario = Usuario(
            nome_usuario=data.get('nome_usuario'),
            email=data.get('email')
        )
        db.session.add(usuario)
        db.session.commit()
        return jsonify(usuario.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@usuario_bp.route('/usuarios/<int:id>', methods=['GET'])
def obter_usuario(id):
    """Obter um utilizador específico (rota modelo)"""
    try:
        usuario = Usuario.query.get_or_404(id)
        return jsonify(usuario.to_dict())
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
