#!/usr/bin/env python3
"""
Test script for the Disaster Assessment API - Debug Version
"""
import requests
import json

# API configuration
BASE_URL = "http://localhost:5000"
API_URL = f"{BASE_URL}/api/avaliacoes"

def test_post_avaliacao():
    """Test creating a new assessment"""
    print("Testing POST /api/avaliacoes")
    print("=" * 50)
    
    # Test data - exactly like your curl request
    test_data = {
        "nome_responsavel": "kc",
        "numero_documento": "1234567",
        "contacto_telefonico": "1234567",
        "membros_agregado": 0,
        "grupos_vulneraveis": ["idoso"],
        "endereco_completo": "Rua de Teste, 123",
        "ponto_referencia": "Próximo ao mercado",
        "latitude_gps": 38.7223,
        "longitude_gps": -9.1393,
        "tipo_estrutura": "habitacao",
        "nivel_danos": "parcial",
        "perdas": ["moveis"],
        "outras_perdas": "Mesa de jantar",
        "necessidade_urgente": "agua_potavel",
        "outra_necessidade": "Reparação do telhado"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        print(f"Sending POST request to: {API_URL}")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        print()
        
        response = requests.post(API_URL, json=test_data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        if response.headers.get('content-type', '').startswith('application/json'):
            response_data = response.json()
            print("Response JSON:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        else:
            print("Response Text:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API. Is the server running?")
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in response: {e}")
        print(f"Raw response: {response.text}")

def test_get_avaliacoes():
    """Test getting all assessments"""
    print("\nTesting GET /api/avaliacoes")
    print("=" * 50)
    
    try:
        response = requests.get(API_URL)
        print(f"Status Code: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            response_data = response.json()
            print("Response JSON:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        else:
            print("Response Text:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API. Is the server running?")
    except Exception as e:
        print(f"ERROR: {e}")

def test_api_root():
    """Test the API root endpoint"""
    print("\nTesting API Root")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"ERROR: {e}")

def test_docs():
    """Test the documentation endpoint"""
    print("\nTesting Documentation")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/docs/")
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.text)}")
        if response.status_code == 200:
            print("Documentation is accessible!")
        
    except Exception as e:
        print(f"ERROR: {e}")

def test_minimal_post():
    """Test with minimal required data only"""
    print("\nTesting POST with minimal data")
    print("=" * 50)
    
    # Minimal required fields only
    minimal_data = {
        "nome_responsavel": "Test User",
        "numero_documento": "123456",
        "contacto_telefonico": "123456789",
        "membros_agregado": 1,
        "endereco_completo": "Test Address",
        "tipo_estrutura": "habitacao",
        "nivel_danos": "parcial",
        "necessidade_urgente": "agua_potavel"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        print(f"Sending minimal POST request to: {API_URL}")
        print(f"Data: {json.dumps(minimal_data, indent=2)}")
        print()
        
        response = requests.post(API_URL, json=minimal_data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            response_data = response.json()
            print("Response JSON:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        else:
            print("Response Text:")
            print(response.text)
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    print("Disaster Assessment API Test - Debug Version")
    print("=" * 60)
    
    # Test basic connectivity
    test_api_root()
    test_docs()
    
    # Test GET endpoint first
    test_get_avaliacoes()
    
    # Test POST endpoint with minimal data
    test_minimal_post()
    
    # Test POST endpoint with full data
    test_post_avaliacao()
