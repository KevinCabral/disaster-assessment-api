import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_restx import Api
from src.models.user import db
from src.models.assessment import AvaliacaoDesastre
from src.routes.assessment_swagger import api as api_avaliacoes
from src.routes.auth import api as api_autenticacao

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Activar CORS para todas as rotas
CORS(app)

# Inicializar API Flask-RESTX com documentação Swagger
api = Api(
    app,
    version='1.0',
    title='API de Avaliação de Desastres',
    description='API para gestão de avaliações de desastres naturais',
    doc='/docs/',  # Swagger UI estará disponível em /docs/
    prefix='/api'
)

# Adicionar namespaces
api.add_namespace(api_avaliacoes, path='/avaliacoes')
api.add_namespace(api_autenticacao, path='/autenticacao')

# Configuração da base de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'disaster_assessment.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def servir(path):
    pasta_estatica = app.static_folder
    if pasta_estatica is None:
            return "Pasta estática não configurada", 404

    if path != "" and os.path.exists(os.path.join(pasta_estatica, path)):
        return send_from_directory(pasta_estatica, path)
    else:
        caminho_index = os.path.join(pasta_estatica, 'index.html')
        if os.path.exists(caminho_index):
            return send_from_directory(pasta_estatica, 'index.html')
        else:
            return "index.html não encontrado", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

