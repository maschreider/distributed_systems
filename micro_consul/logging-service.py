from flask import Flask, request, jsonify
import hazelcast, argparse, os
import my_consul

app = Flask(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, required=True)
args = parser.parse_args()

service_id = my_consul.service_register('logging-service', args.port)
consul_settings = my_consul.get_settings("my_settings")

containers_settings = consul_settings['cluster_nodes']
containers = list(containers_settings.keys())

for c in containers[:-1]:
    if containers_settings[c] == 0:
        os.system(f'docker start {c}')
        containers_settings[c] = 1
        container = c
        break

if containers_settings[containers[-1]] == 0:
    containers_settings[containers[-1]] = 1
    os.system(f'docker start {containers[-1]}')

my_consul.put_setting('my_settings', consul_settings)

hz = hazelcast.HazelcastClient(cluster_name=consul_settings['cluster_name'])
msg = hz.get_map(consul_settings['map_name']).blocking() 

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

    my_consul.service_deregister(service_id)
    consul_settings = my_consul.get_settings("my_settings")
    consul_settings['cluster_nodes'][c] = 0
    my_consul.put_setting('my_settings', consul_settings)


    
