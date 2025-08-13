from flask import request
from flask_restx import Namespace, Resource, fields
from src.models.user import db
from src.models.assessment import AvaliacaoDesastre
import os
from werkzeug.utils import secure_filename

# Criar namespace para avaliações de desastres
api = Namespace('avaliacoes', description='Operações de Avaliação de Desastres')

# Configuração para carregamento de ficheiros
PASTA_UPLOAD = 'uploads/evidence'
EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}

def ficheiro_permitido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS

def garantir_pasta_upload():
    """Garantir que a pasta de upload existe"""
    caminho_upload = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', PASTA_UPLOAD)
    os.makedirs(caminho_upload, exist_ok=True)
    return caminho_upload

# Definir modelos para documentação Swagger com campos em português
assessment_model = api.model('AvaliacaoDesastre', {
    'id': fields.Integer(readonly=True, description='ID da Avaliação'),
    'nome_responsavel': fields.String(required=True, description='Nome do Responsável'),
    'numero_documento': fields.String(required=True, description='Número de Documento (BI ou Passaporte)'),
    'contacto_telefonico': fields.String(required=True, description='Contacto Telefónico'),
    'membros_agregado': fields.Integer(required=True, description='N.º de Pessoas no Agregado Familiar'),
    'grupos_vulneraveis': fields.List(fields.String, description='Grupos Vulneráveis', 
                                   enum=['bebe_crianca', 'idoso', 'pessoa_deficiencia', 'doente_cronico']),
    'endereco_completo': fields.String(required=True, description='Endereço Completo'),
    'ponto_referencia': fields.String(description='Ponto de Referência'),
    'latitude_gps': fields.Float(description='Latitude GPS'),
    'longitude_gps': fields.Float(description='Longitude GPS'),
    'tipo_estrutura': fields.String(required=True, description='Tipo de Estrutura Afetada',
                                  enum=['habitacao', 'comercio', 'agricultura', 'outro']),
    'nivel_danos': fields.String(required=True, description='Nível de Danos',
                                enum=['parcial', 'grave', 'total']),
    'perdas': fields.List(fields.String, description='Perdas',
                         enum=['alimentos', 'roupas_calcado', 'moveis', 'eletrodomesticos', 'documentos_pessoais', 'animais_domesticos', 'outros']),
    'outras_perdas': fields.String(description='Especificação de Outras Perdas'),
    'ficheiros_prova': fields.List(fields.String, description='Ficheiros de prova'),
    'necessidade_urgente': fields.String(required=True, description='Necessidade Urgente',
                               enum=['agua_potavel', 'alimentacao', 'abrigo_temporario', 'roupas_cobertores', 'medicamentos', 'outros']),
    'outra_necessidade': fields.String(description='Especificação de Outra Necessidade Urgente'),
    'data_criacao': fields.DateTime(readonly=True, description='Data de Criação'),
    'data_atualizacao': fields.DateTime(readonly=True, description='Data da Última Atualização')
})

entrada_avaliacao = api.model('EntradaAvaliacao', {
    'nome_responsavel': fields.String(required=True, description='Nome do Responsável'),
    'numero_documento': fields.String(required=True, description='Número de Documento (BI ou Passaporte)'),
    'contacto_telefonico': fields.String(required=True, description='Contacto Telefónico'),
    'membros_agregado': fields.Integer(required=True, description='N.º de Pessoas no Agregado Familiar'),
    'grupos_vulneraveis': fields.List(fields.String, description='Grupos Vulneráveis', 
                                   enum=['bebe_crianca', 'idoso', 'pessoa_deficiencia', 'doente_cronico']),
    'endereco_completo': fields.String(required=True, description='Endereço Completo'),
    'ponto_referencia': fields.String(description='Ponto de Referência'),
    'latitude_gps': fields.Float(description='Latitude GPS'),
    'longitude_gps': fields.Float(description='Longitude GPS'),
    'tipo_estrutura': fields.String(required=True, description='Tipo de Estrutura Afetada',
                                  enum=['habitacao', 'comercio', 'agricultura', 'outro']),
    'nivel_danos': fields.String(required=True, description='Nível de Danos',
                                enum=['parcial', 'grave', 'total']),
    'perdas': fields.List(fields.String, description='Perdas',
                         enum=['alimentos', 'roupas_calcado', 'moveis', 'eletrodomesticos', 'documentos_pessoais', 'animais_domesticos', 'outros']),
    'outras_perdas': fields.String(description='Especificação de Outras Perdas'),
    'necessidade_urgente': fields.String(required=True, description='Necessidade Urgente',
                               enum=['agua_potavel', 'alimentacao', 'abrigo_temporario', 'roupas_cobertores', 'medicamentos', 'outros']),
    'outra_necessidade': fields.String(description='Especificação de Outra Necessidade Urgente')
})

modelo_estatisticas = api.model('Estatisticas', {
    'total_avaliacoes': fields.Integer(description='Total de avaliações'),
    'estatisticas_nivel_danos': fields.Raw(description='Estatísticas por nível de danos'),
    'estatisticas_tipo_estrutura': fields.Raw(description='Estatísticas por tipo de estrutura'),
    'estatisticas_necessidade_urgente': fields.Raw(description='Estatísticas por necessidade urgente')
})

modelo_opcoes = api.model('Opcoes', {
    'grupos_vulneraveis': fields.List(fields.String, description='Opções de grupos vulneráveis disponíveis'),
    'tipos_estrutura': fields.List(fields.String, description='Opções de tipos de estrutura disponíveis'),
    'niveis_danos': fields.List(fields.String, description='Opções de níveis de danos disponíveis'),
    'tipos_perdas': fields.List(fields.String, description='Opções de tipos de perdas disponíveis'),
    'necessidades_urgentes': fields.List(fields.String, description='Opções de necessidades urgentes disponíveis')
})

@api.route('')
class ListaAvaliacoes(Resource):
    @api.doc('listar_avaliacoes')
    @api.param('page', 'Número da página', type='integer', default=1)
    @api.param('per_page', 'Itens por página', type='integer', default=10)
    @api.param('damage_level', 'Filtrar por nível de danos', enum=['parcial', 'grave', 'total'])
    @api.param('structure_type', 'Filtrar por tipo de estrutura', enum=['habitacao', 'comercio', 'agricultura', 'outro'])
    @api.param('urgent_need', 'Filtrar por necessidade urgente', enum=['agua_potavel', 'alimentacao', 'abrigo_temporario', 'roupas_cobertores', 'medicamentos', 'outros'])
    @api.marshal_with(assessment_model, as_list=True)
    def get(self):
        """Listar todas as avaliações de desastre"""
        try:
            pagina = request.args.get('page', 1, type=int)
            por_pagina = request.args.get('per_page', 10, type=int)
            nivel_danos = request.args.get('damage_level')
            tipo_estrutura = request.args.get('structure_type')
            necessidade_urgente = request.args.get('urgent_need')

            query = AvaliacaoDesastre.query

            if nivel_danos:
                query = query.filter(AvaliacaoDesastre.damage_level == nivel_danos)
            if tipo_estrutura:
                query = query.filter(AvaliacaoDesastre.structure_type == tipo_estrutura)
            if necessidade_urgente:
                query = query.filter(AvaliacaoDesastre.urgent_need == necessidade_urgente)

            avaliacoes = query.paginate(
                page=pagina, per_page=por_pagina, error_out=False
            )

            return [avaliacao.to_dict() for avaliacao in avaliacoes.items]

        except Exception as e:
            api.abort(500, f'Erro interno do servidor: {str(e)}')

    @api.doc('criar_avaliacao')
    @api.expect(entrada_avaliacao)
    @api.marshal_with(assessment_model, code=201)
    def post(self):
        """Criar uma nova avaliação de desastre"""
        try:
            data = api.payload
            if not data:
                api.abort(400, 'Dados não fornecidos')

            # Validar campos obrigatórios
            campos_obrigatorios = [
                'responsible_name', 'document_number', 'phone_contact',
                'household_members', 'full_address', 'structure_type',
                'damage_level', 'urgent_need'
            ]

            for campo in campos_obrigatorios:
                if not data.get(campo):
                    api.abort(400, f'Campo obrigatório em falta: {campo}')

            avaliacao = AvaliacaoDesastre.from_dict(data)
            db.session.add(avaliacao)
            db.session.commit()

            return avaliacao.to_dict(), 201

        except Exception as e:
            db.session.rollback()
            api.abort(500, f'Erro ao criar avaliação: {str(e)}')

@api.route('/<int:assessment_id>')
class RecursoAvaliacao(Resource):
    @api.doc('obter_avaliacao')
    @api.marshal_with(assessment_model)
    def get(self, assessment_id):
        """Obter uma avaliação específica pelo ID"""
        try:
            avaliacao = AvaliacaoDesastre.query.get_or_404(assessment_id)
            return avaliacao.to_dict()
        except Exception as e:
            api.abort(500, f'Erro ao obter avaliação: {str(e)}')

    @api.doc('atualizar_avaliacao')
    @api.expect(entrada_avaliacao)
    @api.marshal_with(assessment_model)
    def put(self, assessment_id):
        """Atualizar uma avaliação existente"""
        try:
            avaliacao = AvaliacaoDesastre.query.get_or_404(assessment_id)
            data = api.payload

            if not data:
                api.abort(400, 'Dados não fornecidos')

            # Atualizar a avaliação com os novos dados
            avaliacao_atualizada = AvaliacaoDesastre.from_dict(data)
            for campo in data.keys():
                if hasattr(avaliacao, campo):
                    setattr(avaliacao, campo, getattr(avaliacao_atualizada, campo))

            db.session.commit()
            return avaliacao.to_dict()

        except Exception as e:
            db.session.rollback()
            api.abort(500, f'Erro ao atualizar avaliação: {str(e)}')

    @api.doc('eliminar_avaliacao')
    def delete(self, assessment_id):
        """Eliminar uma avaliação"""
        try:
            avaliacao = AvaliacaoDesastre.query.get_or_404(assessment_id)
            db.session.delete(avaliacao)
            db.session.commit()
            return {'message': 'Avaliação eliminada com sucesso'}, 200
        except Exception as e:
            db.session.rollback()
            api.abort(500, f'Erro ao eliminar avaliação: {str(e)}')

@api.route('/<int:assessment_id>/evidence')
class CarregarProvas(Resource):
    @api.doc('carregar_provas')
    def post(self, assessment_id):
        """Carregar ficheiros de prova para uma avaliação"""
        try:
            avaliacao = AvaliacaoDesastre.query.get_or_404(assessment_id)

            if 'files' not in request.files:
                api.abort(400, 'Nenhum ficheiro fornecido')

            ficheiros = request.files.getlist('files')
            if not ficheiros or ficheiros[0].filename == '':
                api.abort(400, 'Nenhum ficheiro selecionado')

            # Limitar a 3 ficheiros
            if len(ficheiros) > 3:
                api.abort(400, 'Máximo de 3 ficheiros permitidos')

            caminhos_salvos = []
            pasta_upload = garantir_pasta_upload()

            for ficheiro in ficheiros:
                if ficheiro and ficheiro_permitido(ficheiro.filename):
                    nome_ficheiro = secure_filename(ficheiro.filename)
                    # Adicionar ID da avaliação ao nome do ficheiro para evitar conflitos
                    nome_unico = f"{assessment_id}_{nome_ficheiro}"
                    caminho_ficheiro = os.path.join(pasta_upload, nome_unico)
                    ficheiro.save(caminho_ficheiro)
                    caminhos_salvos.append(f"{PASTA_UPLOAD}/{nome_unico}")
                else:
                    api.abort(400, f'Tipo de ficheiro não permitido: {ficheiro.filename}')

            # Atualizar a avaliação com os caminhos dos ficheiros
            import json
            ficheiros_existentes = json.loads(avaliacao.evidence_files) if avaliacao.evidence_files else []
            ficheiros_existentes.extend(caminhos_salvos)
            avaliacao.evidence_files = json.dumps(ficheiros_existentes)

            db.session.commit()

            return {
                'message': f'{len(caminhos_salvos)} ficheiro(s) carregado(s) com sucesso',
                'files': caminhos_salvos
            }, 201

        except Exception as e:
            db.session.rollback()
            api.abort(500, f'Erro ao carregar ficheiros: {str(e)}')

@api.route('/statistics')
class RecursoEstatisticas(Resource):
    @api.doc('obter_estatisticas')
    @api.marshal_with(modelo_estatisticas)
    def get(self):
        """Obter estatísticas das avaliações"""
        try:
            total_avaliacoes = AvaliacaoDesastre.query.count()

            # Estatísticas por nível de danos
            stats_nivel_danos = db.session.query(
                AvaliacaoDesastre.damage_level,
                db.func.count(AvaliacaoDesastre.id)
            ).group_by(AvaliacaoDesastre.damage_level).all()

            # Estatísticas por tipo de estrutura
            stats_tipo_estrutura = db.session.query(
                AvaliacaoDesastre.structure_type,
                db.func.count(AvaliacaoDesastre.id)
            ).group_by(AvaliacaoDesastre.structure_type).all()

            # Estatísticas por necessidade urgente
            stats_necessidade_urgente = db.session.query(
                AvaliacaoDesastre.urgent_need,
                db.func.count(AvaliacaoDesastre.id)
            ).group_by(AvaliacaoDesastre.urgent_need).all()

            return {
                'total_assessments': total_avaliacoes,
                'damage_level_stats': {nivel: count for nivel, count in stats_nivel_danos},
                'structure_type_stats': {tipo: count for tipo, count in stats_tipo_estrutura},
                'urgent_need_stats': {necessidade: count for necessidade, count in stats_necessidade_urgente}
            }

        except Exception as e:
            api.abort(500, f'Erro ao obter estatísticas: {str(e)}')

@api.route('/options')
class RecursoOpcoes(Resource):
    @api.doc('obter_opcoes')
    @api.marshal_with(modelo_opcoes)
    def get(self):
        """Obter opções disponíveis para os formulários"""
        return {
            'vulnerable_groups': ['bebe_crianca', 'idoso', 'pessoa_deficiencia', 'doente_cronico'],
            'structure_types': ['habitacao', 'comercio', 'agricultura', 'outro'],
            'damage_levels': ['parcial', 'grave', 'total'],
            'loss_types': ['alimentos', 'roupas_calcado', 'moveis', 'eletrodomesticos', 'documentos_pessoais', 'animais_domesticos', 'outros'],
            'urgent_needs': ['agua_potavel', 'alimentacao', 'abrigo_temporario', 'roupas_cobertores', 'medicamentos', 'outros']
        }
