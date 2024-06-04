import ssl
import json
import paho.mqtt.client as mqtt

# Preencha com suas credenciais
AWS_IOT_ENDPOINT = "a27psqlmoxrfep-ats.iot.us-east-1.amazonaws.com"
THINGNAME = "TESTE2"

# Preencha com os caminhos para os arquivos de certificado e chave privada
AWS_CERT_CA = "testes/ca1.pem"
AWS_CERT_CRT = "testes/certificado.pem"
AWS_CERT_PRIVATE = "testes/private.key"

# Tópicos MQTT
AWS_IOT_PUBLISH_TOPIC = "esp32/pub"
AWS_IOT_SUBSCRIBE_TOPIC = "esp32/sub"

def on_connect(client, userdata, flags, rc):
    print("Conectado com resultado: "+str(rc))
    client.subscribe(AWS_IOT_SUBSCRIBE_TOPIC)

def on_message(client, userdata, msg):
    print("incoming: ", msg.topic)
    print(msg.payload.decode())

def connect_aws():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.tls_set(ca_certs=AWS_CERT_CA, certfile=AWS_CERT_CRT, keyfile=AWS_CERT_PRIVATE, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
    client.connect(AWS_IOT_ENDPOINT, 8883, keepalive=60)
    return client

def publish_message(client, metrics_value):
    payload = json.dumps({"clientID": THINGNAME, "metrics": metrics_value})
    client.publish(AWS_IOT_PUBLISH_TOPIC, payload)

def main():
    aws_client = connect_aws()
    metrics_value = 'teste wn'  # Aqui você pode colocar a lógica para obter o valor das métricas
    publish_message(aws_client, metrics_value)
    aws_client.loop()
        
if __name__ == "__main__":
    main()
