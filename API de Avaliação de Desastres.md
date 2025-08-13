# API de Avaliação de Desastres

Uma API Flask completa para gestão de avaliações de desastres naturais com documentação Swagger integrada.

## Características

- **Base de Dados SQLite**: Armazenamento local de dados de avaliações
- **Documentação Swagger**: Interface interativa para testar endpoints
- **CORS Habilitado**: Suporte para aplicações frontend
- **Upload de Ficheiros**: Carregamento de provas (fotos/vídeos)
- **Filtragem e Estatísticas**: Endpoints para análise de dados
- **Campos em Português**: Toda a interface e dados em português

## Estrutura da API

### Endpoints Principais

#### 1. Gestão de Avaliações
- `GET /api/assessments` - Listar todas as avaliações (com filtragem)
- `POST /api/assessments` - Criar nova avaliação
- `GET /api/assessments/{id}` - Obter avaliação específica
- `PUT /api/assessments/{id}` - Atualizar avaliação
- `DELETE /api/assessments/{id}` - Eliminar avaliação

#### 2. Upload de Provas
- `POST /api/assessments/{id}/evidence` - Carregar ficheiros de prova

#### 3. Dados de Apoio
- `GET /api/assessments/options` - Obter opções para formulários
- `GET /api/assessments/statistics` - Obter estatísticas

### Modelo de Dados

#### Identificação da Família
- `responsible_name`: Nome do Responsável
- `document_number`: Número de Documento (BI ou Passaporte)
- `phone_contact`: Contacto Telefónico
- `household_members`: N.º de Pessoas no Agregado Familiar
- `vulnerable_groups`: Grupos Vulneráveis (array)
  - `bebe_crianca`: Bebé/criança pequena
  - `idoso`: Idoso
  - `pessoa_deficiencia`: Pessoa com deficiência
  - `doente_cronico`: Doente crónico

#### Localização
- `full_address`: Endereço Completo
- `reference_point`: Ponto de Referência (opcional)
- `gps_latitude`: Latitude GPS
- `gps_longitude`: Longitude GPS

#### Tipo e Nível de Danos
- `structure_type`: Tipo de Estrutura Afetada
  - `habitacao`: Habitação
  - `comercio`: Comércio
  - `agricultura`: Agricultura
  - `outro`: Outro
- `damage_level`: Nível de Danos
  - `parcial`: Parcial (danos pequenos, habitação ainda utilizável)
  - `grave`: Grave (grande parte destruída, risco para uso)
  - `total`: Total (casa inabitável ou destruída)

#### Perdas
- `losses`: Tipos de Perdas (array)
  - `alimentos`: Alimentos
  - `roupas_calcado`: Roupas/calçado
  - `moveis`: Móveis
  - `eletrodomesticos`: Eletrodomésticos
  - `documentos_pessoais`: Documentos pessoais
  - `animais_domesticos`: Animais domésticos
  - `outros`: Outros
- `losses_other`: Especificação de outras perdas

#### Provas
- `evidence_files`: Ficheiros de prova (até 3 ficheiros)

#### Necessidade Urgente
- `urgent_need`: Necessidade Urgente
  - `agua_potavel`: Água potável
  - `alimentacao`: Alimentação
  - `abrigo_temporario`: Abrigo temporário
  - `roupas_cobertores`: Roupas/cobertores
  - `medicamentos`: Medicamentos
  - `outros`: Outros
- `urgent_need_other`: Especificação de outra necessidade

## Instalação e Configuração

### Pré-requisitos
- Python 3.11+
- pip

### Passos de Instalação

1. **Clonar/Descarregar o projeto**
```bash
cd disaster-assessment-api
```

2. **Ativar ambiente virtual**
```bash
source venv/bin/activate
```

3. **Instalar dependências**
```bash
pip install -r requirements.txt
```

4. **Executar a aplicação**
```bash
python src/main_swagger.py
```

A aplicação estará disponível em:
- **API**: http://localhost:5000/api/
- **Documentação Swagger**: http://localhost:5000/docs/

## Utilização

### Acesso à Documentação Swagger
Visite `http://localhost:5000/docs/` para aceder à interface interativa da API onde pode:
- Ver todos os endpoints disponíveis
- Testar endpoints diretamente no navegador
- Ver exemplos de requests e responses
- Consultar modelos de dados

### Exemplo de Criação de Avaliação

```json
{
  "responsible_name": "João Silva",
  "document_number": "123456789",
  "phone_contact": "+351912345678",
  "household_members": 4,
  "vulnerable_groups": ["idoso", "bebe_crianca"],
  "full_address": "Rua das Flores, 123, Lisboa",
  "reference_point": "Próximo ao mercado municipal",
  "gps_latitude": 38.7223,
  "gps_longitude": -9.1393,
  "structure_type": "habitacao",
  "damage_level": "grave",
  "losses": ["moveis", "eletrodomesticos", "roupas_calcado"],
  "losses_other": "Documentos importantes",
  "urgent_need": "abrigo_temporario",
  "urgent_need_other": ""
}
```

### Filtragem de Avaliações

```bash
# Filtrar por nível de danos
GET /api/assessments?damage_level=grave

# Filtrar por tipo de estrutura
GET /api/assessments?structure_type=habitacao

# Paginação
GET /api/assessments?page=1&per_page=10
```

### Upload de Ficheiros de Prova

```bash
curl -X POST \
  http://localhost:5000/api/assessments/1/evidence \
  -H 'Content-Type: multipart/form-data' \
  -F 'files=@foto1.jpg' \
  -F 'files=@video1.mp4'
```

## Estrutura do Projeto

```
disaster-assessment-api/
├── src/
│   ├── models/
│   │   ├── user.py              # Modelo de utilizador (template)
│   │   └── assessment.py        # Modelo de avaliação de desastre
│   ├── routes/
│   │   ├── user.py              # Rotas de utilizador (template)
│   │   ├── assessment.py        # Rotas básicas de avaliação
│   │   └── assessment_swagger.py # Rotas com documentação Swagger
│   ├── static/
│   │   └── uploads/evidence/    # Ficheiros de prova carregados
│   ├── database/
│   │   └── app.db              # Base de dados SQLite
│   ├── main.py                 # Aplicação Flask básica
│   └── main_swagger.py         # Aplicação Flask com Swagger
├── venv/                       # Ambiente virtual Python
├── requirements.txt            # Dependências Python
└── README.md                   # Esta documentação
```

## Dependências Principais

- **Flask**: Framework web
- **Flask-SQLAlchemy**: ORM para base de dados
- **Flask-RESTX**: Extensão para APIs REST com Swagger
- **Flask-CORS**: Suporte para Cross-Origin Resource Sharing

## Desenvolvimento

### Adicionar Novos Endpoints
1. Editar `src/routes/assessment_swagger.py`
2. Adicionar novos recursos usando decoradores Flask-RESTX
3. Definir modelos de dados para documentação Swagger

### Modificar Base de Dados
1. Editar `src/models/assessment.py`
2. Adicionar/modificar campos do modelo
3. Reiniciar aplicação para aplicar alterações

## Deployment

### Opção 1: Servidor Local
```bash
python src/main_swagger.py
```

### Opção 2: Servidor de Produção
```bash
# Instalar gunicorn
pip install gunicorn

# Executar com gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main_swagger:app
```

### Opção 3: Docker (opcional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "src/main_swagger.py"]
```

## Segurança

- **CORS**: Configurado para aceitar requests de qualquer origem
- **Validação**: Validação básica de campos obrigatórios
- **Upload de Ficheiros**: Restrições de tipo de ficheiro
- **Base de Dados**: SQLite local (adequado para desenvolvimento)

## Limitações Atuais

- Base de dados SQLite (não adequada para produção em larga escala)
- Sem autenticação/autorização
- Upload de ficheiros limitado a tipos específicos
- Sem backup automático de dados

## Suporte

Para questões técnicas ou melhorias, consulte a documentação Swagger em `/docs/` ou revise o código fonte.

