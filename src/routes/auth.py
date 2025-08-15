from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from src.models.user import db, Usuario, TipoUtilizador
import jwt
from datetime import datetime, timedelta
import os

# Criar namespace para autenticação
api = Namespace('autenticacao', description='Operações de Autenticação e Gestão de Utilizadores')

# Chave secreta para JWT (em produção, usar variável de ambiente)
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'chave-secreta-jwt-desenvolvimento')
JWT_EXPIRATION_HOURS = 24

# Modelos Swagger para autenticação
modelo_login = api.model('Login', {
    'email': fields.String(required=True, description='Email do utilizador'),
    'senha': fields.String(required=True, description='Senha do utilizador')
})

modelo_registo = api.model('Registo', {
    'nome': fields.String(required=True, description='Nome completo do utilizador'),
    'email': fields.String(required=True, description='Email do utilizador'),
    'senha': fields.String(required=True, description='Senha do utilizador'),
    'papel': fields.String(required=True, description='Papel do utilizador', 
                          enum=['ADMIN', 'COORDENADOR', 'TRABALHADOR_TERRENO'])
})

modelo_utilizador = api.model('Utilizador', {
    'id': fields.String(readonly=True, description='ID único do utilizador'),
    'nome': fields.String(description='Nome completo do utilizador'),
    'email': fields.String(description='Email do utilizador'),
    'papel': fields.String(description='Papel do utilizador'),
    'data_criacao': fields.DateTime(readonly=True, description='Data de criação'),
    'data_atualizacao': fields.DateTime(readonly=True, description='Data da última atualização')
})

modelo_token = api.model('Token', {
    'token': fields.String(description='Token JWT de acesso'),
    'tipo': fields.String(description='Tipo do token (Bearer)'),
    'expira_em': fields.DateTime(description='Data de expiração do token'),
    'utilizador': fields.Nested(modelo_utilizador, description='Dados do utilizador')
})

modelo_verificar_token = api.model('VerificarToken', {
    'token': fields.String(required=True, description='Token JWT para verificar')
})

modelo_resposta_verificacao = api.model('RespostaVerificacao', {
    'valido': fields.Boolean(description='Se o token é válido'),
    'utilizador': fields.Nested(modelo_utilizador),
    'expira_em': fields.DateTime(description='Data de expiração do token')
})

modelo_alterar_senha = api.model('AlterarSenha', {
    'senha_atual': fields.String(required=True, description='Senha atual'),
    'senha_nova': fields.String(required=True, description='Nova senha'),
    'confirmar_senha': fields.String(required=True, description='Confirmação da nova senha')
})

modelo_solicitar_reset = api.model('SolicitarReset', {
    'email': fields.String(required=True, description='Email do utilizador')
})

modelo_reset_senha = api.model('ResetSenha', {
    'token': fields.String(required=True, description='Token de reset'),
    'senha_nova': fields.String(required=True, description='Nova senha'),
    'confirmar_senha': fields.String(required=True, description='Confirmação da nova senha')
})

modelo_resposta_reset = api.model('RespostaReset', {
    'mensagem': fields.String(description='Mensagem de sucesso'),
    'email_enviado': fields.Boolean(description='Se o email foi enviado')
})

def gerar_token(utilizador):
    """Gerar token JWT para o utilizador"""
    payload = {
        'utilizador_id': utilizador.id,
        'email': utilizador.email,
        'papel': utilizador.papel.value,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return token

def verificar_token(token):
    """Verificar e decodificar token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def enviar_email_reset_senha(email, token):
    """Enviar email com link de reset de senha"""
    try:
        # Aqui você configuraria o envio real do email
        # Por agora, apenas simularemos
        print(f"EMAIL: Enviando token de reset para {email}: {token}")
        
        # Em produção, você enviaria um email com um link como:
        # https://seudominio.com/reset-password?token={token}
        
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False

from functools import wraps

def token_obrigatorio(f):
    """Decorador para rotas que requerem autenticação"""
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        
        # Verificar header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            
            # Aceitar tanto "Bearer token" quanto apenas "token"
            if auth_header.startswith('Bearer '):
                token = auth_header.split(" ")[1]
            else:
                token = auth_header  # Assumir que é apenas o token
        
        if not token:
            return {'error': 'Token de autorização não fornecido'}, 401
        
        payload = verificar_token(token)
        if not payload:
            return {'error': 'Token inválido ou expirado'}, 401
        
        # Verificar se o utilizador ainda existe
        utilizador = Usuario.query.get(payload['utilizador_id'])  # Corrigido: utilizador_id em vez de user_id
        if not utilizador:
            return {'error': 'Utilizador não encontrado'}, 401
        
        # Adicionar utilizador ao contexto
        request.current_user = utilizador
        return f(*args, **kwargs)
    
    return decorator

@api.route('/login')
class Login(Resource):
    @api.doc('login_utilizador')
    @api.expect(modelo_login)
    @api.marshal_with(modelo_token, code=200)
    def post(self):
        """Autenticar utilizador e obter token de acesso"""
        try:
            data = api.payload
            if not data:
                return {'error': 'Dados não fornecidos'}, 400
            
            email = data.get('email')
            senha = data.get('senha')
            
            if not email or not senha:
                return {'error': 'Email e senha são obrigatórios'}, 400
            
            # Buscar utilizador por email
            utilizador = Usuario.query.filter_by(email=email).first()
            
            if not utilizador or not utilizador.verificar_senha(senha):
                return {'error': 'Credenciais inválidas'}, 401
            
            # Gerar token
            token = gerar_token(utilizador)
            data_expiracao = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
            
            return {
                'token': token,
                'tipo': 'Bearer',
                'expira_em': data_expiracao.isoformat(),
                'utilizador': utilizador.to_dict()
            }, 200
            
        except Exception as e:
            return {'error': f'Erro no login: {str(e)}'}, 500

@api.route('/registo')
class Registo(Resource):
    @api.doc('registar_utilizador')
    @api.expect(modelo_registo)
    @api.marshal_with(modelo_utilizador, code=201)
    def post(self):
        """Registar novo utilizador (apenas para ADMIN)"""
        try:
            data = api.payload
            if not data:
                return {'error': 'Dados não fornecidos'}, 400
            
            # Validar campos obrigatórios
            campos_obrigatorios = ['nome', 'email', 'senha', 'papel']
            campos_em_falta = [campo for campo in campos_obrigatorios if not data.get(campo)]
            
            if campos_em_falta:
                return {
                    'error': 'Campos obrigatórios em falta',
                    'campos_em_falta': campos_em_falta
                }, 400
            
            # Verificar se email já existe
            if Usuario.query.filter_by(email=data['email']).first():
                return {'error': 'Email já está em uso'}, 409
            
            # Validar papel
            try:
                TipoUtilizador(data['papel'])
            except ValueError:
                return {'error': 'Papel inválido'}, 400
            
            # Criar novo utilizador
            novo_utilizador = Usuario.from_dict(data)
            db.session.add(novo_utilizador)
            db.session.commit()
            
            return novo_utilizador.to_dict(), 201
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Erro ao registar utilizador: {str(e)}'}, 500

@api.route('/verificar')
class VerificarToken(Resource):
    @api.doc('verificar_token')
    @api.expect(modelo_verificar_token)
    @api.marshal_with(modelo_resposta_verificacao, code=200)
    def post(self):
        """Verificar validade do token JWT"""
        try:
            # Tentar obter token do body primeiro
            data = api.payload
            token = None
            
            if data and data.get('token'):
                token = data['token']
            else:
                # Se não houver no body, tentar obter do header Authorization
                auth_header = request.headers.get('Authorization')
                
                if not auth_header:
                    return {'error': 'Token deve ser fornecido no campo "token" ou no header Authorization'}, 400
                
                try:
                    token = auth_header.split(' ')[1]  # Remove "Bearer "
                except IndexError:
                    return {'error': 'Formato de token inválido no header. Use: Bearer <token>'}, 400
            
            if not token:
                return {'error': 'Token não fornecido'}, 400
            
            payload = verificar_token(token)
            
            if not payload:
                return {'error': 'Token inválido ou expirado'}, 401
            
            # Buscar utilizador
            utilizador = Usuario.query.get(payload['utilizador_id'])
            
            if not utilizador:
                return {'error': 'Utilizador não encontrado'}, 404
            
            return {
                'valido': True,
                'utilizador': utilizador.to_dict(),
                'expira_em': datetime.fromtimestamp(payload['exp']).isoformat()
            }, 200
            
        except Exception as e:
            return {'error': f'Erro na verificação: {str(e)}'}, 500

@api.route('/utilizadores')
class ListaUtilizadores(Resource):
    @api.doc('listar_utilizadores')
    @api.marshal_with(modelo_utilizador, as_list=True)
    def get(self):
        """Listar todos os utilizadores (apenas para ADMIN)"""
        try:
            # TODO: Adicionar verificação de autorização (apenas ADMIN)
            utilizadores = Usuario.query.all()
            return [utilizador.to_dict() for utilizador in utilizadores], 200
            
        except Exception as e:
            return {'error': f'Erro ao listar utilizadores: {str(e)}'}, 500

@api.route('/utilizadores/<string:utilizador_id>')
class RecursoUtilizador(Resource):
    @api.doc('obter_utilizador')
    @api.marshal_with(modelo_utilizador)
    def get(self, utilizador_id):
        """Obter dados de um utilizador específico"""
        try:
            utilizador = Usuario.query.get(utilizador_id)
            
            if not utilizador:
                return {'error': 'Utilizador não encontrado'}, 404
            
            return utilizador.to_dict(), 200
            
        except Exception as e:
            return {'error': f'Erro ao obter utilizador: {str(e)}'}, 500
    
    @api.doc('atualizar_utilizador')
    @api.expect(modelo_registo)
    @api.marshal_with(modelo_utilizador)
    def put(self, utilizador_id):
        """Atualizar dados de um utilizador"""
        try:
            utilizador = Usuario.query.get(utilizador_id)
            
            if not utilizador:
                return {'error': 'Utilizador não encontrado'}, 404
            
            data = api.payload
            if not data:
                return {'error': 'Dados não fornecidos'}, 400
            
            # Atualizar campos
            if data.get('nome'):
                utilizador.nome = data['nome']
            if data.get('email'):
                # Verificar se novo email já existe
                if Usuario.query.filter(Usuario.email == data['email'], Usuario.id != utilizador_id).first():
                    return {'error': 'Email já está em uso'}, 409
                utilizador.email = data['email']
            if data.get('senha'):
                utilizador.definir_senha(data['senha'])
            if data.get('papel'):
                try:
                    utilizador.papel = TipoUtilizador(data['papel'])
                except ValueError:
                    return {'error': 'Papel inválido'}, 400
            
            db.session.commit()
            return utilizador.to_dict(), 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Erro ao atualizar utilizador: {str(e)}'}, 500
    
    @api.doc('eliminar_utilizador')
    def delete(self, utilizador_id):
        """Eliminar um utilizador"""
        try:
            utilizador = Usuario.query.get(utilizador_id)
            
            if not utilizador:
                return {'error': 'Utilizador não encontrado'}, 404
            
            db.session.delete(utilizador)
            db.session.commit()
            
            return {'message': 'Utilizador eliminado com sucesso'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Erro ao eliminar utilizador: {str(e)}'}, 500

@api.route('/alterar-senha')
class AlterarSenha(Resource):
    @api.doc('alterar_senha')
    @api.expect(modelo_alterar_senha)
    @token_obrigatorio
    def post(self):
        """Alterar senha do utilizador autenticado"""
        try:
            data = api.payload
            if not data:
                return {'error': 'Dados não fornecidos'}, 400
            
            senha_atual = data.get('senha_atual')
            senha_nova = data.get('senha_nova')
            confirmar_senha = data.get('confirmar_senha')
            
            if not all([senha_atual, senha_nova, confirmar_senha]):
                return {'error': 'Todos os campos são obrigatórios'}, 400
            
            # Verificar senha atual
            if not request.current_user.verificar_senha(senha_atual):
                return {'error': 'Senha atual incorreta'}, 401
            
            # Verificar se nova senha e confirmação coincidem
            if senha_nova != confirmar_senha:
                return {'error': 'Nova senha e confirmação não coincidem'}, 400
            
            # Verificar se nova senha é diferente da atual
            if request.current_user.verificar_senha(senha_nova):
                return {'error': 'A nova senha deve ser diferente da atual'}, 400
            
            # Validar força da senha (mínimo 6 caracteres)
            if len(senha_nova) < 6:
                return {'error': 'A senha deve ter pelo menos 6 caracteres'}, 400
            
            # Alterar senha
            request.current_user.definir_senha(senha_nova)
            db.session.commit()
            
            return {'mensagem': 'Senha alterada com sucesso'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Erro ao alterar senha: {str(e)}'}, 500

@api.route('/solicitar-reset-senha')
class SolicitarResetSenha(Resource):
    @api.doc('solicitar_reset_senha')
    @api.expect(modelo_solicitar_reset)
    @api.marshal_with(modelo_resposta_reset, code=200)
    def post(self):
        """Solicitar reset de senha por email"""
        try:
            data = api.payload
            if not data:
                return {'error': 'Dados não fornecidos'}, 400
            
            email = data.get('email')
            if not email:
                return {'error': 'Email é obrigatório'}, 400
            
            # Buscar utilizador por email
            utilizador = Usuario.query.filter_by(email=email).first()
            
            # Por segurança, sempre retornamos sucesso mesmo se o email não existir
            if utilizador:
                # Gerar token de reset
                token = utilizador.gerar_token_reset_senha()
                db.session.commit()
                
                # Enviar email
                email_enviado = enviar_email_reset_senha(email, token)
                
                return {
                    'mensagem': 'Se o email existir, instruções de reset foram enviadas',
                    'email_enviado': email_enviado
                }, 200
            else:
                # Simular delay para não revelar se email existe
                import time
                time.sleep(1)
                
                return {
                    'mensagem': 'Se o email existir, instruções de reset foram enviadas',
                    'email_enviado': False
                }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Erro ao solicitar reset: {str(e)}'}, 500

@api.route('/reset-senha')
class ResetSenha(Resource):
    @api.doc('reset_senha')
    @api.expect(modelo_reset_senha)
    def post(self):
        """Resetar senha usando token"""
        try:
            data = api.payload
            if not data:
                return {'error': 'Dados não fornecidos'}, 400
            
            token = data.get('token')
            senha_nova = data.get('senha_nova')
            confirmar_senha = data.get('confirmar_senha')
            
            if not all([token, senha_nova, confirmar_senha]):
                return {'error': 'Todos os campos são obrigatórios'}, 400
            
            # Verificar se nova senha e confirmação coincidem
            if senha_nova != confirmar_senha:
                return {'error': 'Nova senha e confirmação não coincidem'}, 400
            
            # Validar força da senha
            if len(senha_nova) < 6:
                return {'error': 'A senha deve ter pelo menos 6 caracteres'}, 400
            
            # Buscar utilizador com token válido
            utilizador = Usuario.query.filter_by(token_reset_senha=token).first()
            
            if not utilizador or not utilizador.verificar_token_reset_senha(token):
                return {'error': 'Token inválido ou expirado'}, 400
            
            # Resetar senha
            utilizador.definir_senha(senha_nova)
            utilizador.limpar_token_reset_senha()
            db.session.commit()
            
            return {'mensagem': 'Senha resetada com sucesso'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Erro ao resetar senha: {str(e)}'}, 500
