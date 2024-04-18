from flask import Flask, request, jsonify
import requests, uuid, hazelcast, argparse
import my_consul

app = Flask(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, required=True)
args = parser.parse_args()

service_id = my_consul.service_register('facade-service', args.port)
consul_settings = my_consul.get_settings("my_settings")

hz = hazelcast.HazelcastClient(cluster_name=consul_settings['cluster_name'])
msg_queue = hz.get_queue(consul_settings['queue_name']).blocking()
from_messages_response = []

@app.route('/', methods=['POST', 'GET'])
def home():
    
    logging_service = my_consul.get_address('logging-service')
 
    if request.method == 'POST':
        txt = request.form.get('txt')
        if not txt:
            return jsonify('No message'), 400
        id = str(uuid.uuid4())
        msg = {'id': id, 'txt': txt}
        action = requests.post(logging_service, data=msg)
        msg_queue.put(txt)
        return jsonify(msg), 200
    
    elif request.method == 'GET':

        messages_service = my_consul.get_address('messages-service')
        logging_response, messages_response = requests.get(logging_service), requests.get(messages_service)

        for i in messages_response.json():
            if i not in from_messages_response:
                from_messages_response.append(i)

        return [f'logging-service: {logging_response.json()}', f'message-service: {from_messages_response}'], 200
    
    else:
        return jsonify('Method not allowed'), 405

app.run(port=args.port)

try:
    while True: pass
except KeyboardInterrupt:
    hz.shutdown()
    my_consul.service_deregister(service_id)