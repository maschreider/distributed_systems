from flask import Flask, request, jsonify
import hazelcast, argparse, threading

app = Flask(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, required=True)
args = parser.parse_args()

hz = hazelcast.HazelcastClient(cluster_name='hc')
msg_queue = hz.get_queue("queue").blocking()
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

    