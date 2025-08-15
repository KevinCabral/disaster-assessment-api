#!/usr/bin/env python3
"""
Script to create/migrate the database with Portuguese field names
"""
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))

from src.models.user import db, Usuario, TipoUtilizador
from src.models.assessment import AvaliacaoDesastre
from flask import Flask

def create_app():
    """Create Flask app for database operations"""
    app = Flask(__name__)
    
    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_folder = os.path.join(basedir, 'database')
    
    # Create database folder if it doesn't exist
    os.makedirs(db_folder, exist_ok=True)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(db_folder, "disaster_assessment.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-key-for-migration'
    
    # Initialize database with app
    db.init_app(app)
    
    return app

def migrate_database():
    """Create all tables and add sample data"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        
        # Drop all tables first (clean slate)
        db.drop_all()
        print("Dropped existing tables")
        
        # Create all tables
        db.create_all()
        print("Created new tables with Portuguese field names")
        
        # Add a sample admin user
        admin_user = Usuario()
        admin_user.nome = "Administrador Sistema"
        admin_user.email = "admin@sistema.pt"
        admin_user.definir_senha("admin123")
        admin_user.papel = TipoUtilizador.ADMIN
        
        db.session.add(admin_user)
        
        # Add a sample coordinator
        coordinator = Usuario()
        coordinator.nome = "João Coordenador"
        coordinator.email = "coordenador@sistema.pt"
        coordinator.definir_senha("coord123")
        coordinator.papel = TipoUtilizador.COORDENADOR
        
        db.session.add(coordinator)
        
        # Add a sample field worker
        field_worker = Usuario()
        field_worker.nome = "Maria Terreno"
        field_worker.email = "terreno@sistema.pt"
        field_worker.definir_senha("campo123")
        field_worker.papel = TipoUtilizador.TRABALHADOR_TERRENO
        
        db.session.add(field_worker)
        
        # Add a sample assessment for testing
        sample_assessment = AvaliacaoDesastre()
        sample_assessment.nome_responsavel = "João Silva"
        sample_assessment.numero_documento = "12345678"
        sample_assessment.contacto_telefonico = "+351 912 345 678"
        sample_assessment.membros_agregado = 4
        sample_assessment.grupos_vulneraveis = '["idoso", "bebe_crianca"]'
        sample_assessment.endereco_completo = "Rua das Flores, 123, Lisboa"
        sample_assessment.ponto_referencia = "Próximo ao mercado central"
        sample_assessment.latitude_gps = 38.7223
        sample_assessment.longitude_gps = -9.1393
        sample_assessment.tipo_estrutura = "habitacao"
        sample_assessment.nivel_danos = "parcial"
        sample_assessment.perdas = '["moveis", "eletrodomesticos"]'
        sample_assessment.outras_perdas = "Televisão e micro-ondas"
        sample_assessment.ficheiros_prova = '["foto1.jpg", "foto2.jpg"]'
        sample_assessment.necessidade_urgente = "abrigo_temporario"
        sample_assessment.outra_necessidade = "Necessidade de reparação do telhado"
        
        db.session.add(sample_assessment)
        db.session.commit()
        
        print("Added sample assessment data")
        print("Added sample users:")
        print("- Admin: admin@sistema.pt / admin123")
        print("- Coordenador: coordenador@sistema.pt / coord123") 
        print("- Trabalhador Terreno: terreno@sistema.pt / campo123")
        print("Database migration completed successfully!")
        
        # Verify the data
        assessments = AvaliacaoDesastre.query.all()
        users = Usuario.query.all()
        print(f"Total assessments in database: {len(assessments)}")
        print(f"Total users in database: {len(users)}")
        
        if assessments:
            sample = assessments[0]
            print(f"Sample assessment: {sample.nome_responsavel} - {sample.tipo_estrutura}")

if __name__ == "__main__":
    migrate_database()
