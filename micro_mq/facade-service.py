from flask import Flask, request, jsonify
import requests, uuid, random, socket, hazelcast

app = Flask(__name__)

logging_ports = [8881, 8882, 8883]
messages_ports = [8884, 8885]

hz = hazelcast.HazelcastClient(cluster_name='hc')
msg_queue = hz.get_queue("queue").blocking()
from_messages_response = []

def is_open(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    check_port = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return True if check_port == 0 else False

def choose_port(ports):
    open_ports = ports
    while True:
        if len(open_ports) == 0:
            print('all ports are closed')
        port = random.choice(open_ports)
        if not is_open(port):
            print(port, 'is closed')
            open_ports.remove(port)
        else: return port

@app.route('/', methods=['POST', 'GET'])
def home():
    
    logging_port = choose_port(logging_ports)
    print(f'logging port: {logging_port}')
 
    if request.method == 'POST':
        txt = request.form.get('txt')
        if not txt:
            return jsonify('No message'), 400
        id = str(uuid.uuid4())
        msg = {'id': id, 'txt': txt}
        action = requests.post(f'http://localhost:{logging_port}/', data=msg)
        msg_queue.put(txt)
        return jsonify(msg), 200
    
    elif request.method == 'GET':

        messages_port = choose_port(messages_ports)
        print(f'messages port: {messages_port}')
        logging_response, messages_response = requests.get(f'http://localhost:{logging_port}/'), requests.get(f'http://localhost:{messages_port}/')

        for i in messages_response.json():
            if i not in from_messages_response:
                from_messages_response.append(i)

        return [f'logging-service: {logging_response.json()}'[:-1], f'message-service: {from_messages_response}'], 200
    
    else:
        return jsonify('Method not allowed'), 405

if __name__ == '__main__':
    app.run(port=8880)