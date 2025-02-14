from flask import Flask, jsonify, request
from flask_cors import CORS
from kafka import KafkaConsumer, KafkaProducer
import json
from datetime import datetime
import threading
import random
from collections import defaultdict

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5000"}})
KAFKA_SERVER = 'kafka:9092'
MESSAGES_TOPIC = 'message'

messages_cache = defaultdict(list)
# contacts_cache = []

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_SERVER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
    
@app.route('/api/messages', methods=['POST'])
def send_message():
    data = request.json
    try:
        message = {
            'id': str(random.randint(0, 100000000000)),
            'user_id': data['user_id'],
            'message': data['message'],
            'type': '',
            'chat_id': '0',
            'Created_At': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        messages_consumer = KafkaConsumer(
            MESSAGES_TOPIC,
            bootstrap_servers=[KAFKA_SERVER],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='earliest'
        )

        # Envoie le message à Kafka
        producer.send(MESSAGES_TOPIC, message)
        try:
            for msg in messages_consumer:
                response = msg.value
                if response["id"] == message["id"]:
                    messages_consumer.close() 
                    return jsonify(response), 200
        finally:
            messages_consumer.close()
            
        # Mise à jour du cache local
        conversation_id = f"{min(message['sender_id'], message['receiver_id'])}_{max(message['sender_id'], message['receiver_id'])}"
        messages_cache[conversation_id].append(message)

        return jsonify({'status': 'success', 'message': message}), 201

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/messages/<int:chat_id>')
def get_messages(chat_id):
    messages = messages_cache[chat_id]
    return jsonify(messages)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)