from flask import Flask, request, jsonify
import requests, uuid, random, socket

app = Flask(__name__)

messages_service = 'http://localhost:8884/'
logging_ports = [8881, 8882, 8883]

def is_open(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    check_port = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return True if check_port == 0 else False

@app.route('/', methods=['POST', 'GET'])
def home():
    open_ports = logging_ports
    while True:
        if len(open_ports) == 0:
            print('all ports are closed')
        port = random.choice(open_ports)
        if not is_open(port):
            print(port, 'is closed')
            open_ports.remove(port)
        else: break

    print(f'logging port: {port}')

    if request.method == 'POST':
        txt = request.form.get('txt')
        if not txt:
            return jsonify('No message'), 400
        id = str(uuid.uuid4())
        msg = {'id': id, 'txt': txt}
        action = requests.post(f'http://localhost:{port}/', data=msg)
        return jsonify(msg), 200
    
    elif request.method == 'GET':
        logging_response, messages_response = requests.get(f'http://localhost:{port}/'), requests.get(messages_service)
        return [f'logging-service: {logging_response.text}'[:-1], f'message-service: {messages_response.text}'], 200
    
    else:
        return jsonify('Method not allowed'), 405

if __name__ == '__main__':
    app.run(port=8880)