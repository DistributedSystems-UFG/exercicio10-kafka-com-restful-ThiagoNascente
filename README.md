## Requisitos

- 5 máquinas t3-small (aws)
- Todas compartilhando a pasta /mnt/efs/fs1
- Portas 9092, 50051

### Maquina 1

```bash
cd /mnt/efs/fs1
```

```bash
sudo apt update
```

```bash
sudo apt install default-jdk
```

```bash
wget https://dlcdn.apache.org/kafka/4.2.0/kafka_2.13-4.2.0.tgz
```

```bash
tar -xzf kafka_2.13-4.2.0.tgz
```

```bash
cd kafka_2.13-4.2.0/
```

```bash
nano config/server.properties
```

```bash
advertised.listeners=PLAINTEXT://<IP_PUBLICO_MAQUINA_1>:9092,CONTROLLER://localhost:9093
```

- CTRL + O
- ENTER
- CTRL + X

```bash
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
bin/kafka-storage.sh format --standalone -t $KAFKA_CLUSTER_ID -c config/server.properties
```

```bash
bin/kafka-server-start.sh config/server.properties
```

- Em outro terminal onde ta rodando kafka, rodar esses dois comandos

```bash
bin/kafka-topics.sh --create --topic telemetria-bruta --bootstrap-server localhost:9092
bin/kafka-topics.sh --create --topic eventos-frota --bootstrap-server localhost:9092
```

### Maquina 2

- Cria e ativa o ambiente virtual

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

- Instala as dependências

```bash
pip install flask requests confluent-kafka
```

```bash
python 3_server.py
```

### Maquina 3

```bash
python 2_processor.py
```

### Maquina 4

```bash
python 1_sensor.py
```

### Maquina 5

```bash
python 4_client.py
```


