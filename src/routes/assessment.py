from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.assessment import AvaliacaoDesastre

# Create blueprint for basic assessment routes
assessment_bp = Blueprint('assessment', __name__)

@assessment_bp.route('/assessments', methods=['GET'])
def get_assessments():
    """Obter todas as avaliações (rota básica sem Swagger)"""
    try:
        avaliacoes = AvaliacaoDesastre.query.all()
        return jsonify([avaliacao.to_dict() for avaliacao in avaliacoes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assessment_bp.route('/assessments', methods=['POST'])
def create_assessment():
    """Criar uma nova avaliação (rota básica sem Swagger)"""
    try:
        data = request.get_json()
        avaliacao = AvaliacaoDesastre.from_dict(data)
        db.session.add(avaliacao)
        db.session.commit()
        return jsonify(avaliacao.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assessment_bp.route('/assessments/<int:id>', methods=['GET'])
def get_assessment(id):
    """Obter uma avaliação específica (rota básica sem Swagger)"""
    try:
        avaliacao = AvaliacaoDesastre.query.get_or_404(id)
        return jsonify(avaliacao.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assessment_bp.route('/assessments/<int:id>', methods=['PUT'])
def update_assessment(id):
    """Atualizar uma avaliação (rota básica sem Swagger)"""
    try:
        avaliacao = AvaliacaoDesastre.query.get_or_404(id)
        data = request.get_json()
        
        # Atualizar usando from_dict para mapeamento correto dos campos
        updated_avaliacao = AvaliacaoDesastre.from_dict(data)
        
        # Copiar campos atualizados
        for attr in ['nome_responsavel', 'numero_documento', 'contacto_telefonico', 'membros_agregado',
                     'grupos_vulneraveis', 'endereco_completo', 'ponto_referencia', 'latitude_gps', 
                     'longitude_gps', 'tipo_estrutura', 'nivel_danos', 'perdas', 'outras_perdas',
                     'ficheiros_prova', 'necessidade_urgente', 'outra_necessidade']:
            if hasattr(updated_avaliacao, attr):
                setattr(avaliacao, attr, getattr(updated_avaliacao, attr))
        
        db.session.commit()
        return jsonify(avaliacao.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assessment_bp.route('/assessments/<int:id>', methods=['DELETE'])
def delete_assessment(id):
    """Eliminar uma avaliação (rota básica sem Swagger)"""
    try:
        avaliacao = AvaliacaoDesastre.query.get_or_404(id)
        db.session.delete(avaliacao)
        db.session.commit()
        return jsonify({'message': 'Avaliação eliminada com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
