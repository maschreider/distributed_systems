import consul
from os import getenv
from uuid import uuid4
from random import randint
from json import loads

consul_service = consul.Consul(host='127.0.0.1', port=8500)

def service_register(service_name, service_port):
    id = str(uuid4())
    consul_service.agent.service.register(service_name, 
                                          service_id=id, 
                                          address=getenv('SERVICE_IP', 'localhost'), 
                                          port=service_port)
    return id

def service_deregister(id):
    return consul_service.agent.service.deregister(id)

def get_address(service_name):
    _, services = consul_service.catalog.service(service_name)
    n = randint(0, len(services) - 1)
    if services:
        address = services[n]['ServiceAddress']
        port = services[n]['ServicePort']
        print(service_name, port)
        return f'http://{address}:{port}'
    else:
        raise Exception(f'No {service_name} service found in Consul')
    
def get_settings(setting):
    _, settings = consul_service.kv.get(setting)
    if settings:
        return loads(settings['Value'])
    else:
        raise Exception("No settings found in Consul")

def put_setting(setting, value):
    consul_service.kv.put(setting, str(value).replace("'", '"'))
