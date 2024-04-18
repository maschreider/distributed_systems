from flask import Flask, request, jsonify
import hazelcast, argparse, threading
import my_consul

app = Flask(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, required=True)
args = parser.parse_args()

service_id = my_consul.service_register('messages-service', args.port)
consul_settings = my_consul.get_settings("my_settings")

hz = hazelcast.HazelcastClient(cluster_name=consul_settings['cluster_name'])
msg_queue = hz.get_queue(consul_settings['queue_name']).blocking()
messages = []

def get_messages():
    while True:
        try:
            msg = msg_queue.take()
            messages.append(msg)
            print(f'Message: {msg}')
        except:
            hz.shutdown()
            exit()
            
@app.route('/', methods=['GET'])
def home():
    if request.method == 'GET':
        return messages
    else:
        return jsonify('Method not allowed'), 405
        
if __name__ == '__main__':
    thread_msg = threading.Thread(target=get_messages)
    thread_msg.start()
    app.run(port=args.port)
    my_consul.service_deregister(service_id)

    