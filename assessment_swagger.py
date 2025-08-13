from flask import request
from flask_restx import Namespace, Resource, fields
from src.models.assessment import db, DisasterAssessment
import os
from werkzeug.utils import secure_filename

# Create namespace for disaster assessments
api = Namespace('assessments', description='Operações de Avaliação de Desastres')

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads/evidence'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_dir():
    """Ensure upload directory exists"""
    upload_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', UPLOAD_FOLDER)
    os.makedirs(upload_path, exist_ok=True)
    return upload_path

# Define models for Swagger documentation
assessment_model = api.model('DisasterAssessment', {
    'id': fields.Integer(readonly=True, description='ID da Avaliação'),
    'responsible_name': fields.String(required=True, description='Nome do Responsável'),
    'document_number': fields.String(required=True, description='Número de Documento (BI ou Passaporte)'),
    'phone_contact': fields.String(required=True, description='Contacto Telefónico'),
    'household_members': fields.Integer(required=True, description='N.º de Pessoas no Agregado Familiar'),
    'vulnerable_groups': fields.List(fields.String, description='Grupos Vulneráveis', 
                                   enum=['bebe_crianca', 'idoso', 'pessoa_deficiencia', 'doente_cronico']),
    'full_address': fields.String(required=True, description='Endereço Completo'),
    'reference_point': fields.String(description='Ponto de Referência'),
    'gps_latitude': fields.Float(description='Latitude GPS'),
    'gps_longitude': fields.Float(description='Longitude GPS'),
    'structure_type': fields.String(required=True, description='Tipo de Estrutura Afetada',
                                  enum=['habitacao', 'comercio', 'agricultura', 'outro']),
    'damage_level': fields.String(required=True, description='Nível de Danos',
                                enum=['parcial', 'grave', 'total']),
    'losses': fields.List(fields.String, description='Perdas',
                         enum=['alimentos', 'roupas_calcado', 'moveis', 'eletrodomesticos', 'documentos_pessoais', 'animais_domesticos', 'outros']),
    'losses_other': fields.String(description='Especificação de Outras Perdas'),
    'evidence_files': fields.List(fields.String, description='Caminhos dos Ficheiros de Prova'),
    'urgent_need': fields.String(required=True, description='Necessidade Urgente',
                               enum=['agua_potavel', 'alimentacao', 'abrigo_temporario', 'roupas_cobertores', 'medicamentos', 'outros']),
    'urgent_need_other': fields.String(description='Especificação de Outra Necessidade Urgente'),
    'created_at': fields.DateTime(readonly=True, description='Data de Criação'),
    'updated_at': fields.DateTime(readonly=True, description='Data da Última Atualização')
})

assessment_input = api.model('AssessmentInput', {
    'responsible_name': fields.String(required=True, description='Nome do Responsável'),
    'document_number': fields.String(required=True, description='Número de Documento (BI ou Passaporte)'),
    'phone_contact': fields.String(required=True, description='Contacto Telefónico'),
    'household_members': fields.Integer(required=True, description='N.º de Pessoas no Agregado Familiar'),
    'vulnerable_groups': fields.List(fields.String, description='Grupos Vulneráveis', 
                                   enum=['bebe_crianca', 'idoso', 'pessoa_deficiencia', 'doente_cronico']),
    'full_address': fields.String(required=True, description='Endereço Completo'),
    'reference_point': fields.String(description='Ponto de Referência'),
    'gps_latitude': fields.Float(description='Latitude GPS'),
    'gps_longitude': fields.Float(description='Longitude GPS'),
    'structure_type': fields.String(required=True, description='Tipo de Estrutura Afetada',
                                  enum=['habitacao', 'comercio', 'agricultura', 'outro']),
    'damage_level': fields.String(required=True, description='Nível de Danos',
                                enum=['parcial', 'grave', 'total']),
    'losses': fields.List(fields.String, description='Perdas',
                         enum=['alimentos', 'roupas_calcado', 'moveis', 'eletrodomesticos', 'documentos_pessoais', 'animais_domesticos', 'outros']),
    'losses_other': fields.String(description='Especificação de Outras Perdas'),
    'urgent_need': fields.String(required=True, description='Necessidade Urgente',
                               enum=['agua_potavel', 'alimentacao', 'abrigo_temporario', 'roupas_cobertores', 'medicamentos', 'outros']),
    'urgent_need_other': fields.String(description='Especificação de Outra Necessidade Urgente')
})

statistics_model = api.model('Statistics', {
    'total_assessments': fields.Integer(description='Total de avaliações'),
    'damage_level_stats': fields.Raw(description='Estatísticas por nível de danos'),
    'structure_type_stats': fields.Raw(description='Estatísticas por tipo de estrutura'),
    'urgent_need_stats': fields.Raw(description='Estatísticas por necessidade urgente')
})

options_model = api.model('Options', {
    'vulnerable_groups': fields.List(fields.String, description='Opções de grupos vulneráveis disponíveis'),
    'structure_types': fields.List(fields.String, description='Opções de tipos de estrutura disponíveis'),
    'damage_levels': fields.List(fields.String, description='Opções de níveis de danos disponíveis'),
    'loss_types': fields.List(fields.String, description='Opções de tipos de perdas disponíveis'),
    'urgent_needs': fields.List(fields.String, description='Opções de necessidades urgentes disponíveis')
})

@api.route('')
class AssessmentList(Resource):
    @api.doc('list_assessments')
    @api.param('page', 'Número da página', type='integer', default=1)
    @api.param('per_page', 'Itens por página', type='integer', default=10)
    @api.param('damage_level', 'Filtrar por nível de danos', enum=['parcial', 'grave', 'total'])
    @api.param('structure_type', 'Filtrar por tipo de estrutura', enum=['habitacao', 'comercio', 'agricultura', 'outro'])
    @api.param('urgent_need', 'Filtrar por necessidade urgente', enum=['agua_potavel', 'alimentacao', 'abrigo_temporario', 'roupas_cobertores', 'medicamentos', 'outros'])
    @api.marshal_with(assessment_model, as_list=True)
    def get(self):
        """Obter todas as avaliações de desastres com filtragem opcional"""
        try:
            # Query parameters for filtering
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            damage_level = request.args.get('damage_level')
            structure_type = request.args.get('structure_type')
            urgent_need = request.args.get('urgent_need')
            
            # Build query
            query = DisasterAssessment.query
            
            if damage_level:
                query = query.filter(DisasterAssessment.damage_level == damage_level)
            if structure_type:
                query = query.filter(DisasterAssessment.structure_type == structure_type)
            if urgent_need:
                query = query.filter(DisasterAssessment.urgent_need == urgent_need)
            
            # Paginate results
            assessments = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            return {
                'assessments': [assessment.to_dict() for assessment in assessments.items],
                'total': assessments.total,
                'pages': assessments.pages,
                'current_page': page,
                'per_page': per_page
            }
        except Exception as e:
            api.abort(500, str(e))

    @api.doc('create_assessment')
    @api.expect(assessment_input)
    @api.marshal_with(assessment_model, code=201)
    def post(self):
        """Criar uma nova avaliação de desastre"""
        try:
            data = api.payload
            
            # Validate required fields
            required_fields = [
                'responsible_name', 'document_number', 'phone_contact', 
                'household_members', 'full_address', 'structure_type', 
                'damage_level', 'urgent_need'
            ]
            
            for field in required_fields:
                if field not in data or not data[field]:
                    api.abort(400, f'Missing required field: {field}')
            
            # Create new assessment
            assessment = DisasterAssessment.from_dict(data)
            
            db.session.add(assessment)
            db.session.commit()
            
            return assessment.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            api.abort(500, str(e))

@api.route('/<int:assessment_id>')
@api.param('assessment_id', 'ID da Avaliação')
class Assessment(Resource):
    @api.doc('get_assessment')
    @api.marshal_with(assessment_model)
    def get(self, assessment_id):
        """Obter uma avaliação de desastre específica por ID"""
        try:
            assessment = DisasterAssessment.query.get_or_404(assessment_id)
            return assessment.to_dict()
        except Exception as e:
            api.abort(500, str(e))

    @api.doc('update_assessment')
    @api.expect(assessment_input)
    @api.marshal_with(assessment_model)
    def put(self, assessment_id):
        """Atualizar uma avaliação de desastre existente"""
        try:
            assessment = DisasterAssessment.query.get_or_404(assessment_id)
            data = api.payload
            
            # Update fields
            if 'responsible_name' in data:
                assessment.responsible_name = data['responsible_name']
            if 'document_number' in data:
                assessment.document_number = data['document_number']
            if 'phone_contact' in data:
                assessment.phone_contact = data['phone_contact']
            if 'household_members' in data:
                assessment.household_members = data['household_members']
            if 'vulnerable_groups' in data:
                assessment.set_vulnerable_groups(data['vulnerable_groups'])
            if 'full_address' in data:
                assessment.full_address = data['full_address']
            if 'reference_point' in data:
                assessment.reference_point = data['reference_point']
            if 'gps_latitude' in data:
                assessment.gps_latitude = data['gps_latitude']
            if 'gps_longitude' in data:
                assessment.gps_longitude = data['gps_longitude']
            if 'structure_type' in data:
                assessment.structure_type = data['structure_type']
            if 'damage_level' in data:
                assessment.damage_level = data['damage_level']
            if 'losses' in data:
                assessment.set_losses(data['losses'])
            if 'losses_other' in data:
                assessment.losses_other = data['losses_other']
            if 'urgent_need' in data:
                assessment.urgent_need = data['urgent_need']
            if 'urgent_need_other' in data:
                assessment.urgent_need_other = data['urgent_need_other']
            
            db.session.commit()
            return assessment.to_dict()
        except Exception as e:
            db.session.rollback()
            api.abort(500, str(e))

    @api.doc('delete_assessment')
    def delete(self, assessment_id):
        """Eliminar uma avaliação de desastre"""
        try:
            assessment = DisasterAssessment.query.get_or_404(assessment_id)
            db.session.delete(assessment)
            db.session.commit()
            return {'message': 'Assessment deleted successfully'}
        except Exception as e:
            db.session.rollback()
            api.abort(500, str(e))

@api.route('/<int:assessment_id>/evidence')
@api.param('assessment_id', 'ID da Avaliação')
class AssessmentEvidence(Resource):
    @api.doc('upload_evidence')
    def post(self, assessment_id):
        """Carregar ficheiros de prova para uma avaliação"""
        try:
            assessment = DisasterAssessment.query.get_or_404(assessment_id)
            
            if 'files' not in request.files:
                api.abort(400, 'No files provided')
            
            files = request.files.getlist('files')
            uploaded_files = []
            
            # Ensure upload directory exists
            upload_path = ensure_upload_dir()
            
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Add assessment ID to filename to avoid conflicts
                    filename = f"{assessment_id}_{filename}"
                    file_path = os.path.join(upload_path, filename)
                    file.save(file_path)
                    uploaded_files.append(f"{UPLOAD_FOLDER}/{filename}")
            
            # Update assessment with new evidence files
            current_files = assessment.get_evidence_files()
            current_files.extend(uploaded_files)
            assessment.set_evidence_files(current_files)
            
            db.session.commit()
            
            return {
                'message': f'Uploaded {len(uploaded_files)} files',
                'files': uploaded_files,
                'assessment': assessment.to_dict()
            }
        except Exception as e:
            db.session.rollback()
            api.abort(500, str(e))

@api.route('/statistics')
class AssessmentStatistics(Resource):
    @api.doc('get_statistics')
    @api.marshal_with(statistics_model)
    def get(self):
        """Obter estatísticas sobre avaliações de desastres"""
        try:
            total_assessments = DisasterAssessment.query.count()
            
            # Damage level statistics
            damage_stats = db.session.query(
                DisasterAssessment.damage_level,
                db.func.count(DisasterAssessment.id)
            ).group_by(DisasterAssessment.damage_level).all()
            
            # Structure type statistics
            structure_stats = db.session.query(
                DisasterAssessment.structure_type,
                db.func.count(DisasterAssessment.id)
            ).group_by(DisasterAssessment.structure_type).all()
            
            # Urgent need statistics
            urgent_need_stats = db.session.query(
                DisasterAssessment.urgent_need,
                db.func.count(DisasterAssessment.id)
            ).group_by(DisasterAssessment.urgent_need).all()
            
            return {
                'total_assessments': total_assessments,
                'damage_level_stats': dict(damage_stats),
                'structure_type_stats': dict(structure_stats),
                'urgent_need_stats': dict(urgent_need_stats)
            }
        except Exception as e:
            api.abort(500, str(e))

@api.route('/options')
class AssessmentOptions(Resource):
    @api.doc('get_options')
    @api.marshal_with(options_model)
    def get(self):
        """Obter opções disponíveis para campos do formulário"""
        return {
            'vulnerable_groups': [
                'bebe_crianca',
                'idoso', 
                'pessoa_deficiencia',
                'doente_cronico'
            ],
            'structure_types': [
                'habitacao',
                'comercio',
                'agricultura',
                'outro'
            ],
            'damage_levels': [
                'parcial',
                'grave', 
                'total'
            ],
            'loss_types': [
                'alimentos',
                'roupas_calcado',
                'moveis',
                'eletrodomesticos',
                'documentos_pessoais',
                'animais_domesticos',
                'outros'
            ],
            'urgent_needs': [
                'agua_potavel',
                'alimentacao',
                'abrigo_temporario',
                'roupas_cobertores',
                'medicamentos',
                'outros'
            ]
        }

