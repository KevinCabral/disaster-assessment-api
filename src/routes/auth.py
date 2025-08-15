from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from src.models.user import db, Usuario, TipoUtilizador
import jwt
from datetime import datetime, timedelta
import os
import secrets
import string

# Criar namespace para autenticação
api = Namespace('autenticacao', 
                description='Operações de Autenticação e Gestão de Utilizadores',
                authorizations={
                    'Bearer': {
                        'type': 'apiKey',
                        'in': 'header',
                        'name': 'Authorization',
                        'description': 'Digite: Bearer <token>'
                    }
                })

# Chave secreta para JWT (em produção, usar variável de ambiente)
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'chave-secreta-jwt-desenvolvimento')
JWT_EXPIRATION_HOURS = 24

# Simulação de armazenamento temporário para códigos de reset (em produção, usar Redis ou base de dados)
codigos_reset = {}

def gerar_codigo_reset():
    """Gerar código de reset de 6 dígitos"""
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def enviar_email_reset(email, codigo):
    """Simular envio de email com código de reset (em produção, integrar com serviço de email)"""
    print(f"EMAIL SIMULADO para {email}: Seu código de reset é: {codigo}")
    print(f"Este código expira em 30 minutos.")
    return True

def validar_senha(senha):
    """Validar força da senha"""
    if len(senha) < 8:
        return False, "Senha deve ter pelo menos 8 caracteres"
    if not any(c.isupper() for c in senha):
        return False, "Senha deve conter pelo menos uma letra maiúscula"
    if not any(c.islower() for c in senha):
        return False, "Senha deve conter pelo menos uma letra minúscula"
    if not any(c.isdigit() for c in senha):
        return False, "Senha deve conter pelo menos um número"
    return True, "Senha válida"

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
    'utilizador': fields.Nested(modelo_utilizador, description='Dados do utilizador (se válido)'),
    'mensagem': fields.String(description='Mensagem de status')
})

modelo_atualizar_senha = api.model('AtualizarSenha', {
    'senha_atual': fields.String(required=True, description='Senha atual do utilizador (para verificação)'),
    'senha_nova': fields.String(required=True, description='Nova senha do utilizador (min. 8 caracteres)'),
    'confirmar_senha': fields.String(required=True, description='Confirmação da nova senha (deve ser igual à nova senha)')
})

modelo_solicitar_reset = api.model('SolicitarReset', {
    'email': fields.String(required=True, description='Email do utilizador para reset')
})

modelo_reset_senha = api.model('ResetSenha', {
    'email': fields.String(required=True, description='Email do utilizador'),
    'codigo_reset': fields.String(required=True, description='Código de reset recebido por email'),
    'senha_nova': fields.String(required=True, description='Nova senha do utilizador'),
    'confirmar_senha': fields.String(required=True, description='Confirmação da nova senha')
})

modelo_resposta_reset = api.model('RespostaReset', {
    'mensagem': fields.String(description='Mensagem de confirmação'),
    'codigo_enviado': fields.Boolean(description='Se o código foi enviado com sucesso')
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
                
                # Support both "Bearer token" and just "token" formats
                if auth_header.startswith('Bearer '):
                    try:
                        token = auth_header.split(' ')[1]  # Remove "Bearer "
                    except IndexError:
                        return {'error': 'Formato de token inválido no header. Use: Bearer <token>'}, 400
                else:
                    # If no "Bearer " prefix, assume the entire header is the token
                    token = auth_header
            
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

@api.route('/atualizar-senha')
class AtualizarSenha(Resource):
    @api.doc('atualizar_senha', 
             description='Atualizar senha do utilizador autenticado. Requer token Bearer no header Authorization.',
             security='Bearer')
    @api.expect(modelo_atualizar_senha)
    def put(self):
        """Atualizar senha do utilizador autenticado"""
        try:
            # Verificar token de autorização
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return {'error': 'Token de autorização não fornecido'}, 401
            
            # Support both "Bearer token" and just "token" formats
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                # If no "Bearer " prefix, assume the entire header is the token
                token = auth_header
            payload = verificar_token(token)
            
            if not payload:
                return {'error': 'Token inválido ou expirado'}, 401
            
            # Obter dados da requisição
            data = api.payload
            if not data:
                return {'error': 'Dados não fornecidos'}, 400
            
            # Validar campos obrigatórios
            campos_obrigatorios = ['senha_atual', 'senha_nova', 'confirmar_senha']
            for campo in campos_obrigatorios:
                if not data.get(campo):
                    return {'error': f'Campo obrigatório: {campo}'}, 400
            
            # Verificar se as senhas novas coincidem
            if data['senha_nova'] != data['confirmar_senha']:
                return {'error': 'Confirmação de senha não confere'}, 400
            
            # Validar força da nova senha
            senha_valida, mensagem = validar_senha(data['senha_nova'])
            if not senha_valida:
                return {'error': mensagem}, 400
            
            # Obter utilizador
            utilizador = Usuario.query.get(payload['utilizador_id'])
            if not utilizador:
                return {'error': 'Utilizador não encontrado'}, 404
            
            # Verificar senha atual
            if not utilizador.verificar_senha(data['senha_atual']):
                return {'error': 'Senha atual incorreta'}, 400
            
            # Atualizar senha
            utilizador.definir_senha(data['senha_nova'])
            db.session.commit()
            
            return {'message': 'Senha atualizada com sucesso'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Erro ao atualizar senha: {str(e)}'}, 500

@api.route('/solicitar-reset-senha')
class SolicitarResetSenha(Resource):
    @api.doc('solicitar_reset_senha')
    @api.expect(modelo_solicitar_reset)
    @api.marshal_with(modelo_resposta_reset)
    def post(self):
        """Solicitar reset de senha por email"""
        try:
            data = api.payload
            if not data or not data.get('email'):
                return {'mensagem': 'Email é obrigatório', 'codigo_enviado': False}, 400
            
            email = data['email']
            
            # Verificar se utilizador existe
            utilizador = Usuario.query.filter_by(email=email).first()
            if not utilizador:
                # Por segurança, não revelamos se o email existe ou não
                return {
                    'mensagem': 'Se o email existir no sistema, receberá um código de reset',
                    'codigo_enviado': True
                }, 200
            
            # Gerar código de reset
            codigo = gerar_codigo_reset()
            
            # Armazenar código temporariamente (expires em 30 minutos)
            expiracao = datetime.utcnow() + timedelta(minutes=30)
            codigos_reset[email] = {
                'codigo': codigo,
                'expiracao': expiracao,
                'utilizador_id': utilizador.id
            }
            
            # Enviar email (simulado)
            sucesso_envio = enviar_email_reset(email, codigo)
            
            if sucesso_envio:
                return {
                    'mensagem': 'Código de reset enviado para o email',
                    'codigo_enviado': True
                }, 200
            else:
                return {
                    'mensagem': 'Erro ao enviar email',
                    'codigo_enviado': False
                }, 500
                
        except Exception as e:
            return {
                'mensagem': f'Erro ao processar solicitação: {str(e)}',
                'codigo_enviado': False
            }, 500

@api.route('/reset-senha')
class ResetSenha(Resource):
    @api.doc('reset_senha')
    @api.expect(modelo_reset_senha)
    def post(self):
        """Resetar senha usando código recebido por email"""
        try:
            data = api.payload
            if not data:
                return {'error': 'Dados não fornecidos'}, 400
            
            # Validar campos obrigatórios
            campos_obrigatorios = ['email', 'codigo_reset', 'senha_nova', 'confirmar_senha']
            for campo in campos_obrigatorios:
                if not data.get(campo):
                    return {'error': f'Campo obrigatório: {campo}'}, 400
            
            email = data['email']
            codigo_fornecido = data['codigo_reset']
            senha_nova = data['senha_nova']
            confirmar_senha = data['confirmar_senha']
            
            # Verificar se as senhas coincidem
            if senha_nova != confirmar_senha:
                return {'error': 'Confirmação de senha não confere'}, 400
            
            # Validar força da nova senha
            senha_valida, mensagem = validar_senha(senha_nova)
            if not senha_valida:
                return {'error': mensagem}, 400
            
            # Verificar código de reset
            if email not in codigos_reset:
                return {'error': 'Código de reset inválido ou expirado'}, 400
            
            codigo_data = codigos_reset[email]
            
            # Verificar se código não expirou
            if datetime.utcnow() > codigo_data['expiracao']:
                del codigos_reset[email]
                return {'error': 'Código de reset expirado'}, 400
            
            # Verificar se código está correto
            if codigo_data['codigo'] != codigo_fornecido:
                return {'error': 'Código de reset incorreto'}, 400
            
            # Obter utilizador
            utilizador = Usuario.query.get(codigo_data['utilizador_id'])
            if not utilizador:
                return {'error': 'Utilizador não encontrado'}, 404
            
            # Atualizar senha
            utilizador.definir_senha(senha_nova)
            db.session.commit()
            
            # Remover código usado
            del codigos_reset[email]
            
            return {'message': 'Senha resetada com sucesso'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Erro ao resetar senha: {str(e)}'}, 500
