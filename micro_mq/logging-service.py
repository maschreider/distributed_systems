from flask import Flask, request, jsonify
import hazelcast, argparse, os
from isrunning import is_container_running

app = Flask(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, required=True)
args = parser.parse_args()

containers = ['node1', 'node2', 'node3', 'hc-mc']
for c in containers[:-1]:
    if not is_container_running(c):
        os.system(f'docker start {c}')
        container = c
        break
if not is_container_running(containers[-1]):
    os.system(f'docker start {containers[-1]}')

hz = hazelcast.HazelcastClient(cluster_name='hc')
msg = hz.get_map('messages').blocking() 

@app.route('/', methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        id, txt = request.form.get('id'), request.form.get('txt')
        if not (id or txt):
            return jsonify('No id or text'), 400

        msg.put(id, txt)
        print('Message:', txt)
        return jsonify('Message was logged'), 201
    
    elif request.method == 'GET':
        return [msg.get(key) for key in msg.key_set()]
    
    else:
        return jsonify('Method not allowed'), 405

app.run(port=args.port)

try:
    while True: pass
except KeyboardInterrupt:
    hz.shutdown()
    os.system(f'docker stop {container}')
