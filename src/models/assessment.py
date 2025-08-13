from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# Import db from user module
from .user import db

class AvaliacaoDesastre(db.Model):
    __tablename__ = 'avaliacoes_desastre'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Identificação da Família
    nome_responsavel = db.Column(db.String(200), nullable=False)  # Nome do Responsável
    numero_documento = db.Column(db.String(50), nullable=False)    # Número de Documento (BI ou Passaporte)
    contacto_telefonico = db.Column(db.String(20), nullable=False)      # Contacto Telefónico
    membros_agregado = db.Column(db.Integer, nullable=False)     # N.º de Pessoas no Agregado Familiar
    grupos_vulneraveis = db.Column(db.Text)  # JSON string: ['bebe_crianca', 'idoso', 'pessoa_deficiencia', 'doente_cronico']
    
    # Localização
    endereco_completo = db.Column(db.Text, nullable=False)            # Endereço Completo
    ponto_referencia = db.Column(db.String(500))                 # Ponto de Referência (opcional)
    latitude_gps = db.Column(db.Float)                           # Latitude GPS
    longitude_gps = db.Column(db.Float)                          # Longitude GPS
    
    # Tipo e Nível de Danos
    tipo_estrutura = db.Column(db.String(50), nullable=False)    # ['habitacao', 'comercio', 'agricultura', 'outro']
    nivel_danos = db.Column(db.String(20), nullable=False)      # ['parcial', 'grave', 'total']
    
    # Perdas
    perdas = db.Column(db.Text)                                  # JSON string: tipos de perdas
    outras_perdas = db.Column(db.Text)                            # Especificação de outras perdas
    
    # Provas
    ficheiros_prova = db.Column(db.Text)                          # JSON string: caminhos dos ficheiros (até 3)
    
    # Necessidade Urgente
    necessidade_urgente = db.Column(db.String(50), nullable=False)       # ['agua_potavel', 'alimentacao', 'abrigo_temporario', 'roupas_cobertores', 'medicamentos', 'outros']
    outra_necessidade = db.Column(db.Text)                       # Especificação de outra necessidade
    
    # Timestamps
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AvaliacaoDesastre {self.id} - {self.nome_responsavel}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome_responsavel': self.nome_responsavel,
            'numero_documento': self.numero_documento,
            'contacto_telefonico': self.contacto_telefonico,
            'membros_agregado': self.membros_agregado,
            'grupos_vulneraveis': json.loads(self.grupos_vulneraveis) if self.grupos_vulneraveis else [],
            'endereco_completo': self.endereco_completo,
            'ponto_referencia': self.ponto_referencia,
            'latitude_gps': self.latitude_gps,
            'longitude_gps': self.longitude_gps,
            'tipo_estrutura': self.tipo_estrutura,
            'nivel_danos': self.nivel_danos,
            'perdas': json.loads(self.perdas) if self.perdas else [],
            'outras_perdas': self.outras_perdas,
            'ficheiros_prova': json.loads(self.ficheiros_prova) if self.ficheiros_prova else [],
            'necessidade_urgente': self.necessidade_urgente,
            'outra_necessidade': self.outra_necessidade,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None
        }

    @classmethod
    def from_dict(cls, data):
        """Criar uma instância de AvaliacaoDesastre a partir de um dicionário"""
        assessment = cls()
        assessment.nome_responsavel = data.get('nome_responsavel')
        assessment.numero_documento = data.get('numero_documento')
        assessment.contacto_telefonico = data.get('contacto_telefonico')
        assessment.membros_agregado = data.get('membros_agregado')
        assessment.grupos_vulneraveis = json.dumps(data.get('grupos_vulneraveis', []))
        assessment.endereco_completo = data.get('endereco_completo')
        assessment.ponto_referencia = data.get('ponto_referencia')
        assessment.latitude_gps = data.get('latitude_gps')
        assessment.longitude_gps = data.get('longitude_gps')
        assessment.tipo_estrutura = data.get('tipo_estrutura')
        assessment.nivel_danos = data.get('nivel_danos')
        assessment.perdas = json.dumps(data.get('perdas', []))
        assessment.outras_perdas = data.get('outras_perdas')
        assessment.ficheiros_prova = json.dumps(data.get('ficheiros_prova', []))
        assessment.necessidade_urgente = data.get('necessidade_urgente')
        assessment.outra_necessidade = data.get('outra_necessidade')
        return assessment
