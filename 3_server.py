import json
import sqlite3
import threading
from flask import Flask, jsonify
from confluent_kafka import Consumer

app = Flask(__name__)

# 1. Configuração do Banco de Dados (SQLite)
def setup_db():
    conn = sqlite3.connect('fleet.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicle_state (
            vehicle_id TEXT PRIMARY KEY,
            average_speed REAL,
            status TEXT,
            last_updated TEXT
        )
    ''')
    conn.commit()
    return conn

db_conn = setup_db()

# 2. Worker do Kafka (Consome eventos e salva no DB)
def kafka_consumer_worker():
    consumer = Consumer({
        #'bootstrap.servers': '54.162.220.194:9092',
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'grupo-webservice',
        'auto.offset.reset': 'latest'
    })
    consumer.subscribe(['eventos-frota'])
    
    print("[Kafka Worker] Escutando eventos processados...")
    while True:
        msg = consumer.poll(1.0)
        if msg is None or msg.error(): continue
        
        data = json.loads(msg.value().decode('utf-8'))
        
        # Upsert no SQLite
        cursor = db_conn.cursor()
        cursor.execute('''
            INSERT INTO vehicle_state (vehicle_id, average_speed, status, last_updated)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(vehicle_id) DO UPDATE SET
                average_speed=excluded.average_speed,
                status=excluded.status,
                last_updated=excluded.last_updated
        ''', (data['vehicle_id'], data['average_speed'], data['status'], data['timestamp']))
        db_conn.commit()
        print(f"[DB Write] Estado atualizado para {data['vehicle_id']}")

# 3. Implementação do Endpoint RESTful
@app.route('/api/vehicle/<vehicle_id>', methods=['GET'])
def get_vehicle_status(vehicle_id):
    cursor = db_conn.cursor()
    cursor.execute('SELECT average_speed, status, last_updated FROM vehicle_state WHERE vehicle_id = ?', (vehicle_id,))
    row = cursor.fetchone()
    
    if row:
        return jsonify({
            'vehicle_id': vehicle_id,
            'average_speed': row[0],
            'status': row[1],
            'last_updated': row[2]
        }), 200
    else:
        return jsonify({'error': 'Veículo não encontrado.'}), 404

# 4. Inicialização
if __name__ == '__main__':
    # Inicia o worker do Kafka em background
    threading.Thread(target=kafka_consumer_worker, daemon=True).start()
    
    # Inicia o servidor Flask na porta 5000, escutando em todas as interfaces
    print("[REST Server] Rodando na porta 5000...")
    app.run(host='0.0.0.0', port=5000)