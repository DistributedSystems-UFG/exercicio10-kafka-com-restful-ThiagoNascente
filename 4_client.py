import requests
import time

def run():
    print("Iniciando cliente RESTful do Gestor de Frota...")
    
    # IP da Máquina onde o 3_server.py está rodando
    # Lembre-se de ajustar este IP para o IP Público ou Privado correto da sua máquina na AWS
    #server_ip = '13.217.28.164'
    server_ip = 'localhost'
    base_url = f'http://{server_ip}:5000/api/vehicle/'
    
    vehicle_id = "CAMINHAO-001"
    
    # Faz consultas periódicas simulando o painel web
    for _ in range(5):
        print(f"\n[Cliente] Consultando status de {vehicle_id}...")
        try:
            # Faz a requisição GET
            response = requests.get(base_url + vehicle_id)
            
            # Verifica se a requisição foi bem sucedida (HTTP 200 OK)
            if response.status_code == 200:
                data = response.json()
                print(f" > Velocidade Atual: {data['average_speed']} km/h")
                print(f" > Status: {data['status']}")
                print(f" > Última atualização: {data['last_updated']}")
            elif response.status_code == 404:
                print(f" > Aviso: {response.json().get('error')}")
            else:
                print(f"Erro inesperado: Status Code {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão com o servidor: {e}")
        
        time.sleep(3)

if __name__ == '__main__':
    run()