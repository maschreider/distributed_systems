from flask import Flask, request, jsonify
import requests, uuid

app = Flask(__name__)

logging_service = 'http://localhost:8881/logging'
messages_service = 'http://localhost:8882/messages'

@app.route('/', methods=['POST', 'GET'])

def home():
    if request.method == 'POST':
        txt = request.form.get('txt')
        if not txt:
            return jsonify('No message'), 400
        id = str(uuid.uuid4())
        msg = {'id': id, 'txt': txt}
        action = requests.post(logging_service, data=msg)
        return jsonify(msg), 200
    
    elif request.method == 'GET':
        logging_response, messages_response = requests.get(logging_service), requests.get(messages_service)
        return [f'logging-service: {logging_response.text}'[:-1], f'message-service: {messages_response.text}'], 200
    
    else:
        return jsonify('Method not allowed'), 405

if __name__ == '__main__':
    app.run(port=8880)