import socket
import re

def udp_scan():
    # Cria um socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Define um timeout para o socket
    sock.settimeout(5)
    
    # Endereço de broadcast e porta
    broadcast_address = '255.255.255.255'
    port = 5555
    message = "<SI>"

    try:
        # Configura o socket para permitir envio de broadcast
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Envia a mensagem
        #print(f"Enviando mensagem '{message}' para {broadcast_address}:{port}")
        sock.sendto(message.encode(), (broadcast_address, port))
        
        # Tenta receber uma resposta
        #print("Aguardando resposta...")
        response, addr = sock.recvfrom(4096)
        #print(f"Resposta recebida de {addr}: {response.decode()}")
        return response.decode()

    except socket.timeout:
        print("Nenhuma resposta recebida dentro do tempo limite.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return None
    finally:
        # Fecha o socket
        sock.close()

def extract_info(message):
    # Define o padrão da expressão regular para capturar as informações
    pattern = r"<([^>]+)><([^>]+)><([^>]+)><([^>]+)>"
    match = re.match(pattern, message)
    
    if match:
        # Extrai as informações
        nome = match.group(1)
        ip = match.group(2)
        mac = match.group(3)
        versao = match.group(4)
        
        # Printa as informações
        print(f"Nome: {nome}")
        print(f"IP: {ip}")
        print(f"Endereço MAC: {mac}")
        print(f"Versão: {versao}")
        
        return ip
    else:
        print("A mensagem não está no formato esperado.")
        return None

def send_tcp_message(ip, message):
    # Cria um socket TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Define o endereço e porta de destino
        port = 8080
        
        # Conecta ao servidor
        sock.connect((ip, port))
        
        # Envia a mensagem
        #print(f"Enviando mensagem '{message}' para {ip}:{port}")
        sock.sendall(message.encode())
        
        # Tenta receber uma resposta
        response = sock.recv(4096)
        print(response.decode())
        
        return response.decode()

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return None
    finally:
        # Fecha o socket
        sock.close()

# Executa o scan UDP e salva a resposta em uma variável
resposta = udp_scan()

if resposta:
    #print(f"Resposta salva: {resposta}")
    # Extrai e printa as informações da mensagem recebida
    ip = extract_info(resposta)
    
    if ip:
        # Loop para enviar quantas mensagens desejar
        while True:
            # Solicita a mensagem do usuário
            mensagem = input("Digite a mensagem para enviar (ou 'sair' para terminar): ")
            if mensagem.lower() == 'sair':
                break
            # Envia a mensagem para o IP recebido usando TCP
            mensagem = f'<{mensagem.upper()}>'
            send_tcp_message(ip, mensagem)
else:
    print("Nenhuma resposta para processar.")
