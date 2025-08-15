from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import enum

db = SQLAlchemy()

class TipoUtilizador(enum.Enum):
    ADMIN = "ADMIN"
    COORDENADOR = "COORDENADOR" 
    TRABALHADOR_TERRENO = "TRABALHADOR_TERRENO"

class Usuario(db.Model):
    __tablename__ = 'utilizadores'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(200), nullable=False)  # Nome completo do utilizador
    email = db.Column(db.String(120), unique=True, nullable=False)  # Email para login
    hash_senha = db.Column(db.String(255), nullable=False)  # Hash da senha
    papel = db.Column(db.Enum(TipoUtilizador), nullable=False)  # Papel do utilizador
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Usuario {self.id} - {self.nome} ({self.papel.value})>'
    
    def definir_senha(self, senha):
        """Definir senha com hash seguro"""
        self.hash_senha = generate_password_hash(senha)
    
    def verificar_senha(self, senha):
        """Verificar se a senha fornecida está correta"""
        return check_password_hash(self.hash_senha, senha)
    
    def to_dict(self):
        """Converter utilizador para dicionário (sem informações sensíveis)"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'papel': self.papel.value,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Criar utilizador a partir de dicionário"""
        usuario = cls()
        usuario.nome = data.get('nome')
        usuario.email = data.get('email')
        if data.get('senha'):
            usuario.definir_senha(data.get('senha'))
        papel_str = data.get('papel', 'TRABALHADOR_TERRENO')
        usuario.papel = TipoUtilizador(papel_str)
        return usuario
