import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from flask_cors import CORS
from models.user import db
from routes.assessment import assessment_bp
from routes.user import usuario_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Register blueprints
app.register_blueprint(assessment_bp, url_prefix='/api')
app.register_blueprint(usuario_bp, url_prefix='/api')

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return {'mensagem': 'API de Avaliação de Desastres', 'versao': '1.0'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
