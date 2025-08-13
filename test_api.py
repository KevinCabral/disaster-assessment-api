#!/usr/bin/env python3
"""
Script de teste para a API de Avaliação de Desastres
Demonstra como usar todos os endpoints da API
"""

import requests
import json

# Configuração da API
BASE_URL = "http://localhost:5000/api"

def test_options():
    """Testar endpoint de opções"""
    print("=== Testando Opções ===")
    response = requests.get(f"{BASE_URL}/assessments/options")
    if response.status_code == 200:
        options = response.json()
        print("✓ Opções obtidas com sucesso:")
        print(f"  - Grupos vulneráveis: {options['vulnerable_groups']}")
        print(f"  - Tipos de estrutura: {options['structure_types']}")
        print(f"  - Níveis de danos: {options['damage_levels']}")
        return True
    else:
        print(f"✗ Erro ao obter opções: {response.status_code}")
        return False

def test_create_assessment():
    """Testar criação de avaliação"""
    print("\n=== Testando Criação de Avaliação ===")
    
    assessment_data = {
        "responsible_name": "Maria Santos",
        "document_number": "987654321",
        "phone_contact": "+351923456789",
        "household_members": 3,
        "vulnerable_groups": ["idoso"],
        "full_address": "Avenida da Liberdade, 456, Porto",
        "reference_point": "Próximo à estação de metro",
        "gps_latitude": 41.1579,
        "gps_longitude": -8.6291,
        "structure_type": "habitacao",
        "damage_level": "parcial",
        "losses": ["moveis", "eletrodomesticos"],
        "losses_other": "Alguns livros",
        "urgent_need": "medicamentos",
        "urgent_need_other": ""
    }
    
    response = requests.post(
        f"{BASE_URL}/assessments",
        json=assessment_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        assessment = response.json()
        print("✓ Avaliação criada com sucesso:")
        print(f"  - ID: {assessment['id']}")
        print(f"  - Responsável: {assessment['responsible_name']}")
        print(f"  - Endereço: {assessment['full_address']}")
        return assessment['id']
    else:
        print(f"✗ Erro ao criar avaliação: {response.status_code}")
        print(f"  Resposta: {response.text}")
        return None

def test_get_assessments():
    """Testar listagem de avaliações"""
    print("\n=== Testando Listagem de Avaliações ===")
    
    response = requests.get(f"{BASE_URL}/assessments")
    if response.status_code == 200:
        data = response.json()
        print("✓ Avaliações obtidas com sucesso:")
        print(f"  - Total: {data['total']}")
        print(f"  - Página atual: {data['current_page']}")
        print(f"  - Avaliações nesta página: {len(data['assessments'])}")
        return True
    else:
        print(f"✗ Erro ao obter avaliações: {response.status_code}")
        return False

def test_get_assessment(assessment_id):
    """Testar obtenção de avaliação específica"""
    print(f"\n=== Testando Obtenção de Avaliação {assessment_id} ===")
    
    response = requests.get(f"{BASE_URL}/assessments/{assessment_id}")
    if response.status_code == 200:
        assessment = response.json()
        print("✓ Avaliação obtida com sucesso:")
        print(f"  - ID: {assessment['id']}")
        print(f"  - Responsável: {assessment['responsible_name']}")
        print(f"  - Nível de danos: {assessment['damage_level']}")
        return True
    else:
        print(f"✗ Erro ao obter avaliação: {response.status_code}")
        return False

def test_update_assessment(assessment_id):
    """Testar atualização de avaliação"""
    print(f"\n=== Testando Atualização de Avaliação {assessment_id} ===")
    
    update_data = {
        "damage_level": "grave",
        "urgent_need": "abrigo_temporario"
    }
    
    response = requests.put(
        f"{BASE_URL}/assessments/{assessment_id}",
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        assessment = response.json()
        print("✓ Avaliação atualizada com sucesso:")
        print(f"  - Novo nível de danos: {assessment['damage_level']}")
        print(f"  - Nova necessidade urgente: {assessment['urgent_need']}")
        return True
    else:
        print(f"✗ Erro ao atualizar avaliação: {response.status_code}")
        return False

def test_statistics():
    """Testar endpoint de estatísticas"""
    print("\n=== Testando Estatísticas ===")
    
    response = requests.get(f"{BASE_URL}/assessments/statistics")
    if response.status_code == 200:
        stats = response.json()
        print("✓ Estatísticas obtidas com sucesso:")
        print(f"  - Total de avaliações: {stats['total_assessments']}")
        print(f"  - Estatísticas por nível de danos: {stats['damage_level_stats']}")
        print(f"  - Estatísticas por tipo de estrutura: {stats['structure_type_stats']}")
        return True
    else:
        print(f"✗ Erro ao obter estatísticas: {response.status_code}")
        return False

def test_filtering():
    """Testar filtragem de avaliações"""
    print("\n=== Testando Filtragem ===")
    
    # Filtrar por nível de danos
    response = requests.get(f"{BASE_URL}/assessments?damage_level=grave")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Filtro por nível 'grave': {len(data['assessments'])} resultados")
    else:
        print(f"✗ Erro no filtro por nível de danos: {response.status_code}")
        return False
    
    # Filtrar por tipo de estrutura
    response = requests.get(f"{BASE_URL}/assessments?structure_type=habitacao")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Filtro por tipo 'habitacao': {len(data['assessments'])} resultados")
        return True
    else:
        print(f"✗ Erro no filtro por tipo de estrutura: {response.status_code}")
        return False

def main():
    """Executar todos os testes"""
    print("🚀 Iniciando testes da API de Avaliação de Desastres")
    print("=" * 50)
    
    try:
        # Testar opções
        if not test_options():
            return
        
        # Criar avaliação
        assessment_id = test_create_assessment()
        if not assessment_id:
            return
        
        # Testar listagem
        if not test_get_assessments():
            return
        
        # Testar obtenção específica
        if not test_get_assessment(assessment_id):
            return
        
        # Testar atualização
        if not test_update_assessment(assessment_id):
            return
        
        # Testar estatísticas
        if not test_statistics():
            return
        
        # Testar filtragem
        if not test_filtering():
            return
        
        print("\n" + "=" * 50)
        print("✅ Todos os testes passaram com sucesso!")
        print("🎉 A API está funcionando corretamente!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Erro de conexão!")
        print("Certifique-se de que a API está em execução em http://localhost:5000")
        print("Execute: python src/main_swagger.py")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()

