# Projeto: Software para análise técnica do painel.
# Dev: Weverton Nicolau
Version = '1.0.3.2'

import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import ttk
import re
import time
from PIL import Image, ImageTk
import sqlite3
import socket


# Informações do servidor MQTT
server = 'super-author.cloudmqtt.com'
port = 1883
username = 'tdmstjgu'
password = 'mBv2M7HusSx8'
default_topic = 'null'
publish_topic = f'/Danf/{default_topic}/V3/Mqtt/Comando'
subscribe_topic = f'/Danf/{default_topic}/V3/Mqtt/Feedback'

# Dicionário para armazenar as imagens das lâmpadas
lamp_labels = {}

# Variável para verificar se o tópico foi definido
topic_set = False

# Variável para armazenar o cliente MQTT
client = None

def on_connect(client, userdata, flags, rc):
    client.subscribe(subscribe_topic)
    print("Conectado com o código de resultado:", rc)
    if rc == 0:
        received_messages_text.config(state="normal")
        received_messages_text.delete("1.0", tk.END)
        received_messages_text.insert(tk.END, "Conectado ao tópico")
        received_messages_text.config(state="disabled")

# Função para tratar o feedback recebido
def tratar_feedback(feedback):
    resultados = []
    segmentos = feedback.split('>')
    for segmento in segmentos:
        if segmento:
            if segmento.startswith("<DM"):
                # Processar feedback de dimmer
                dimmer_id = segmento[3:5]
                canais_estados = re.findall(r'C(\d+)(\d{2})', segmento[5:])
                resultado = {"dimmer_id": dimmer_id}
                for canal, porcentagem in canais_estados:
                    resultado[f"canal{canal}"] = int(porcentagem)
                resultados.append(resultado)
                #print(f"Dimmer ID: {dimmer_id}")
                for canal in resultado.items():
                    if canal != "dimmer_id":
                        atualizar_porcentagem_texto1(resultado['canal1'])
                        atualizar_porcentagem_texto2(resultado['canal2'])
            else:
                # Processar feedback padrão
                placa = segmento[1:3]
                canais_estados = re.findall(r'(\d)([LD])', segmento[3:])
                resultado = {"placa": placa}
                for i, (canal, estado) in enumerate(canais_estados, start=1):
                    resultado[f"canal{i}"] = {"numero": canal, "estado": estado}
                resultados.append(resultado)
                #print(resultado)
    return resultados

# Callback para quando uma mensagem MQTT é recebida
def on_message(client, userdata, msg):
    if send_via_ip.get():
        feedback = msg.decode("utf-8")
    else:
        feedback = msg.payload.decode("utf-8")
    
    received_messages_text.config(state="normal")
    received_messages_text.delete("1.0", tk.END)
    received_messages_text.insert(tk.END, "Feedback: " + feedback + "\n")
    received_messages_text.delete(f"1.{len(feedback)+10}", tk.END)
    received_messages_text.config(state="disabled")

    resultados = tratar_feedback(feedback)
    
    for resultado in resultados:
        if "placa" in resultado:
            placa = resultado["placa"]
            for i in range(1, 9):
                canal = f"canal{i}"
                if canal in resultado:
                    estado = resultado[canal]["estado"]
                    update_lamp_image(placa, i, estado)
            update_placa_feedback(placa)

def create_lamp_label(placa, canal):
    placa_str = str(placa)
    if placa_str not in lamp_labels:
        lamp_labels[placa_str] = {}
        # Cria a lâmpada de feedback da placa
        feedback_label = tk.Label(lamp_frames[placa_str], image=imageNone, bg=color_p)
        feedback_label.pack(side=tk.TOP, padx=2, pady=5)
        lamp_labels[placa_str]["feedback"] = feedback_label
    if canal not in lamp_labels[placa_str]:
        default_image = imageNone
        try:
            lamp_label = tk.Label(lamp_frames[placa_str], image=default_image, bg=color_p)
            lamp_label.pack(side=tk.TOP, padx=2, pady=5)
            lamp_labels[placa_str][canal] = lamp_label
        except Exception as e:
            print("Erro ao criar lâmpada:", e)
    else:
        update_lamp_image(placa, canal, "D")

def update_lamp_image(placa, canal, status):
    placa_str = 'Placa ' + str(placa).lstrip('0')
    if placa_str in lamp_labels:
        if canal in lamp_labels[placa_str]:
            lamp_label = lamp_labels[placa_str][canal]
            update_placa_feedback(placa_str)
            if status == "D":
                change_lamp_image(lamp_label, imageOff)
            elif status == "L":
                change_lamp_image(lamp_label, imageOn)
            else:
                change_lamp_image(lamp_label, imageNone)
                print("Status desconhecido:", status)
        else:
            print("Canal não encontrado para placa", placa_str)
    else:
        print("Placa não encontrada:", placa_str)

def update_placa_feedback(placa):
    placa_str = 'Placa ' + str(placa).lstrip('0')
    if placa_str in lamp_labels:
        feedback_label = lamp_labels[placa_str].get("feedback")
        if feedback_label:
            any_on = any(
                lamp_label.cget("image") == str(imageOn)
                for lamp_label in lamp_labels[placa_str].values()
                if lamp_label != feedback_label
            )
            change_lamp_image(feedback_label, imageOn if any_on else imageOff)

def change_lamp_image(lamp_label, image):
    lamp_label.config(image=image)
    lamp_label.image = image

# Cria e conecta o cliente MQTT
def create_and_connect_mqtt_client():
    global client
    try:
        client = mqtt.Client()
    except:
        received_messages_text.config(state="normal")
        received_messages_text.delete("1.0", tk.END)
        received_messages_text.insert(tk.END, "Erro na API :(")
        received_messages_text.config(state="disabled")
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username, password)
    try:
        client.connect(server, port)
    except:
        received_messages_text.config(state="normal")
        received_messages_text.delete("1.0", tk.END)
        received_messages_text.insert(tk.END, "Sem conexão com a internet")
        received_messages_text.config(state="disabled")
    client.loop_start()

def send_message(message, via_ip=False):
    message = message.upper()

    if message == 'SA' or message == 'SI':
        received_messages_text.config(state="normal")
        received_messages_text.delete("1.0", tk.END)
        received_messages_text.insert(tk.END, "Central não responde :(")
        received_messages_text.config(state="disabled")

    try:
        if message == '':
            received_messages_text.config(state="normal")
            received_messages_text.delete("1.0", tk.END)
            received_messages_text.insert(tk.END, "Insira uma mensagem")
            received_messages_text.config(state="disabled")

        elif message.startswith('DM'):
            if id_canal_entry.get() == '':
                received_messages_text.config(state="normal")
                received_messages_text.delete("1.0", tk.END)
                received_messages_text.insert(tk.END, "Insira o Canal e o ID")
                received_messages_text.config(state="disabled")
            else:
                if via_ip:
                    on_checkbutton_toggled(message,False)
                    print(message)
                else:
                    client.publish(publish_topic, message)
                    print(message)
        else:
            if via_ip:
                received_messages_text.config(state="normal")
                received_messages_text.delete("1.0", tk.END)
                received_messages_text.insert(tk.END, on_checkbutton_toggled(message,False))
                received_messages_text.config(state="disabled")
                        
            else:
                client.publish(publish_topic, message)
                print('Mensagem enviada:', message)

    except AttributeError:
        received_messages_text.config(state="normal")
        received_messages_text.delete("1.0", tk.END)
        received_messages_text.insert(tk.END, "Insira um tópico, por favor :)")
        received_messages_text.config(state="disabled")
        
# Envia uma mensagem personalizada
def send_custom_message():
    message = entry.get()
    send_message(message, via_ip=send_via_ip.get())

# Envia uma mensagem para ligar um canal específico em uma placa
def send_ON_command(channel, placa):
    placa_str = f"0{placa}" if placa < 10 else str(placa)  # Adiciona um zero à esquerda se a placa for menor que 10
    send_message(f"OFONC{channel}{placa_str}",via_ip=send_via_ip.get())

# Envia uma mensagem para desligar um canal específico em uma placa
def send_OFF_command(channel, placa):
    placa_str = f"0{placa}" if placa < 10 else str(placa)  # Adiciona um zero à esquerda se a placa for menor que 10
    send_message(f"OFFFC{channel}{placa_str}",via_ip=send_via_ip.get())

# Envia uma mensagem para ligar todos os canais de todas as placas
def send_ON_geral():
    send_message("OFAN",via_ip=send_via_ip.get())

# Envia uma mensagem para desligar todos os canais de todas as placas
def send_OFF_geral():
    send_message("OFAO",via_ip=send_via_ip.get())

def destroy_lamp_frames():
    global lamp_frames, lamp_labels
    for placa, frame in lamp_frames.items():
        frame.destroy()
    lamp_frames = {}
    lamp_labels = {}
    for idx, placa in enumerate(placas):
        lamp_frame = tk.Frame(frame_principal, bg=color_p)
        lamp_frame.grid(row=1, column=idx * 3 + 2, padx=(1, 15), pady=5)
        lamp_frames[placa] = lamp_frame
        for canal in range(1, 9):
            create_lamp_label(placa, canal)

# Define o tópico e reinicia a conexão MQTT
def insert_topic():
    global publish_topic, subscribe_topic, topic_set, client
    if send_via_ip.get():
        try:
            client.disconnect()
            client.loop_stop()
        except:
            pass
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        # Define o endereço e porta de destino
        sock.settimeout(0.5)
        resposta = udp_scan()
        ip = extract_info(resposta)

        topic_entry.delete("0", tk.END)
        topic_entry.insert(0, ip)

    else:
        topic = topic_entry.get()
        publish_topic = f'/Danf/{topic}/V3/Mqtt/Comando'
        subscribe_topic = f'/Danf/{topic}/V3/Mqtt/Feedback'
        topic_set = True
        create_and_connect_mqtt_client()
        
    destroy_lamp_frames()

# Envia a porcentagem selecionada
def send_percentage(event=None):
    percentage = int(percentage_slider.get())  # Converte para inteiro
    id_canal = id_canal_entry.get()
    if percentage < 10:
        send_message(f"DM0{percentage}{id_canal}",via_ip=send_via_ip.get())
    else:
        send_message(f"DM{percentage}{id_canal}",via_ip=send_via_ip.get())

def off_Dimmer(canal_id):
    send_message(F'DM00{canal_id}',via_ip=send_via_ip.get())

# Atualiza o texto da porcentagem do canal
def atualizar_porcentagem_texto1(porcentagem):
    porcentagem_texto1.config(text=f'C1: {porcentagem}%')

def atualizar_porcentagem_texto2(porcentagem):
    porcentagem_texto2.config(text=f'C2: {porcentagem}%')

def send_ON_placa(placa):
    for channel in range(1, 9):
        time.sleep(0.1)
        if placa < 10:
            send_message(f"OFONC{channel}0{placa}",via_ip=send_via_ip.get())
        else:
            send_message(f"OFONC{channel}{placa}",via_ip=send_via_ip.get())
# Função para desligar todos os canais de uma placa específica
def send_OFF_placa(placa):
    for channel in range(1, 9):
        time.sleep(0.1)
        if placa < 10:
            send_message(f"OFFFC{channel}0{placa}",via_ip=send_via_ip.get())
        else:
            send_message(f"OFFFC{channel}{placa}",via_ip=send_via_ip.get())

def filter_combobox_suggestions(event):
    root.after(100, update_combobox_values) 
    
def update_combobox_values():
    value = combobox.get().upper()
    if value == '':
        combobox['values'] = list(original_values.keys())  # Mostra todos os valores quando o texto é apagado
    else:
        data = [item for item in original_values.keys() if value in item.upper()]
        combobox['values'] = data

    combobox.event_generate('<Down>')
    topic_entry.delete("0", tk.END)
    topic_entry.insert(0, original_values[combobox.get()])

def get_client_data():
    conn = sqlite3.connect('base_de_dados/Clientes.db')
    cursor = conn.cursor()
    
    cursor.execute('CREATE TABLE IF NOT EXISTS Clientes ('  # Executa uma instrução SQL para criar uma tabela chamada 'clientes'
            'Nome TEXT,'  # Define a coluna 'nome' como do tipo texto
            'Topico TEXT'  # Define a coluna 'peso' como do tipo real (número decimal)
            ')')

    cursor.execute('SELECT Nome, Topico FROM Clientes')
    rows = cursor.fetchall()
    
    conn.close()
    
    # Cria um dicionário onde a chave é o nome e o valor é o tópico
    return {row[0]: row[1] for row in rows}

def udp_scan():
    # Cria um socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Define um timeout para o socket
    sock.settimeout(0.5)
    
    # Endereço de broadcast e porta
    broadcast_address = '255.255.255.255'
    port = 5555
    message = "<SI>"

    try:
        # Configura o socket para permitir envio de broadcast
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        # Envia a mensagem
        sock.sendto(message.encode(), (broadcast_address, port))
        
        # Tenta receber uma resposta
        response, addr = sock.recvfrom(4096)
        #on_message(None,None,response.decode())
        return response.decode()

    except socket.timeout:
        print("Nenhuma resposta recebida dentro do tempo limite.")
        received_messages_text.config(state="normal")
        received_messages_text.delete("1.0", tk.END)
        received_messages_text.insert(tk.END, "Central nao encontrada")
        received_messages_text.config(state="disabled")
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

        received_messages_text.config(state="normal")
        received_messages_text.delete("1.0", tk.END)
        received_messages_text.insert(tk.END, f'Nome: {nome}\nIP: {ip}\nMAC: {mac}\nVersão: {versao}\n')
        received_messages_text.config(state="disabled")
        
        return ip
    else:
        print("A mensagem não está no formato esperado.")
        return None

def on_checkbutton_toggled(message,scan):
    if send_via_ip.get():
        try:
            client.disconnect()
            client.loop_stop()
        except:
            pass
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = 8080
    
        sock.settimeout(0.5)
        try:
            if scan == True:
                # Define o endereço e porta de destino
                resposta = udp_scan()
                ip = extract_info(resposta)

                topic_entry.delete("0", tk.END)
                topic_entry.insert(0, ip)
            else:
                ip = topic_entry.get()
            # Conecta ao servidor
            sock.connect((ip, port))
                    
            # Envia a mensagem
            message = f'<{message}>'
            sock.sendall(message.encode().upper())
            print(message)   
            # Tenta receber uma resposta
            response = sock.recv(4096)
            on_message(None, None, response)
            print(response.decode())
            return response.decode()

        except Exception as e:
            received_messages_text.config(state="normal")
            received_messages_text.delete("1.0", tk.END)
            received_messages_text.insert(tk.END, 'Central não encontrada')
            received_messages_text.config(state="disabled")
            print(f"Ocorreu um erro: {e}")
            return None
        finally:
                    # Fecha o socket
            sock.close()


color_p = 'lightgray'

# Inicialização da interface gráfica
root = tk.Tk()
root.title("DANF - MQTT")
root.geometry("1370x700")  # Ajusta o tamanho da janela
root.configure(bg=color_p)

imageOff = 'img/lampadaapagada.png'
imageOn = 'img/lampadaacesa.png'
imageNone = 'img/lampadavermelha.png'
imageOff = Image.open(imageOff).resize((16, 16), Image.LANCZOS)
imageOn = Image.open(imageOn).resize((16, 16), Image.LANCZOS)
imageNone = Image.open(imageNone).resize((16, 16), Image.LANCZOS)

# Convertendo imagens para PhotoImage
imageOff = ImageTk.PhotoImage(imageOff)
imageOn = ImageTk.PhotoImage(imageOn)
imageNone = ImageTk.PhotoImage(imageNone)

# Canvas principal para permitir rolagem horizontal
canvas = tk.Canvas(root)
canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

# Adiciona uma barra de rolagem horizontal ao canvas
scrollbar = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=canvas.xview)
scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
canvas.configure(xscrollcommand=scrollbar.set)

# Frame para conter as placas
frame_principal = tk.Frame(canvas, bg=color_p)
canvas.create_window((0, 0), window=frame_principal, anchor='nw')

# Lista de placas
placas = [f"Placa {i}" for i in range(1, 17)]
# Dicionário para armazenar os frames de círculos das bolinhas
lamp_frames = {}

# Criar grupos de botões para cada placa
for idx, placa in enumerate(placas):
    lamp_frame = tk.Frame(frame_principal, bg=color_p)
    lamp_frame.grid(row=1, column=idx * 3 + 2, padx=(1, 15), pady=5)  # Espaçamento menor na lateral esquerda e um pouco de espaçamento vertical
    lamp_frame.grid_propagate(False)  # Desativa a propagação automática de tamanho

    lamp_labels[placa] = {}
    # Texto da placa
    label_placa = tk.Label(frame_principal, text=placa, padx=10, bg=color_p, fg="black", font=("Arial", 12, "bold"))
    label_placa.grid(row=0, column=idx * 3, columnspan=3)

    # Frame para os botões ON
    frame_on = tk.Frame(frame_principal, bg=color_p)
    frame_on.grid(row=1, column=idx * 3, padx=(2, 2), pady=5)  # Espaçamento menor na lateral direita e um pouco de espaçamento vertical
    frame_on.grid_propagate(False)  # Desativa a propagação automática de tamanho

    # Frame para os botões OFF
    frame_off = tk.Frame(frame_principal, bg=color_p)
    frame_off.grid(row=1, column=idx * 3 + 1, padx=(2, 1), pady=5)  # Espaçamento menor na lateral esquerda e um pouco de espaçamento vertical
    frame_off.grid_propagate(False)  # Desativa a propagação automática de tamanho

    # Salva a referência ao frame do círculo
    lamp_frames[placa] = lamp_frame

    channel = None

    create_lamp_label(placa, channel)

    btn_ON_placa = tk.Button(frame_on, text=f"On", command=lambda ch=channel, p=idx + 1: send_ON_placa(p), bg="lightgreen", fg="black", width=6, padx=1, pady=1, font=("Arial", 9, "bold"))
    btn_ON_placa.pack(side=tk.TOP, padx=2, pady=2)

    btn_OFF_placa = tk.Button(frame_off, text=f"Off", command=lambda ch=channel, p=idx + 1: send_OFF_placa(p), bg="indianred", fg="black", width=6, padx=1, pady=1, font=("Arial", 9, "bold"))
    btn_OFF_placa.pack(side=tk.TOP, padx=2, pady=2)
    
    # Criando os botões para os canais 1 a 8 da Placa
    for channel in range(1, 9):
        create_lamp_label(placa, channel)

        btn_channel_on = tk.Button(frame_on, text=f"Canal {channel}", command=lambda ch=channel, p=idx + 1: send_ON_command(ch, p), bg="lightgreen", fg="black", width=6, padx=1, pady=1, font=("Arial", 9, "bold"))
        btn_channel_on.pack(side=tk.TOP, padx=2, pady=2)

        btn_channel_off = tk.Button(frame_off, text=f"Canal {channel}", command=lambda ch=channel, p=idx + 1: send_OFF_command(ch, p), bg="indianred", fg="black", width=6, padx=1, pady=1, font=("Arial", 9, "bold"))
        btn_channel_off.pack(side=tk.TOP, padx=2, pady=2)

canvas.update_idletasks()

# Define a região rolável do canvas
canvas.config(scrollregion=canvas.bbox(tk.ALL))

# Frame para os elementos relacionados ao feedback
frame_feedback = tk.Frame(root, bg=color_p)
frame_feedback.pack(side=tk.BOTTOM, pady=2)  # Adiciona espaçamento vertical de 10 pixels

# Widget de texto para exibir mensagens recebidas
received_messages_text = tk.Text(frame_feedback, height=10, width=50, bg="lightgrey", font=("Arial", 10), state="disabled")
received_messages_text.pack(side=tk.BOTTOM, padx=10, pady=5)

# Botões para ligar/desligar geral
frame_geral = tk.Frame(root, bg=color_p)
frame_geral.pack(side=tk.BOTTOM, pady=2)

btn_on_geral = tk.Button(frame_geral, text="ON Geral", command=send_ON_geral, bg="lightgreen", fg='black', font=("Arial", 10, "bold"))
btn_on_geral.pack(side=tk.LEFT, padx=5, pady=1)

btn_off_geral = tk.Button(frame_geral, text="OFF Geral", command=send_OFF_geral, bg="indianred", fg='black', font=("Arial", 10, "bold"))
btn_off_geral.pack(side=tk.LEFT, padx=5, pady=1)

frame_percentage = tk.Frame(root, bg="lightgray")
frame_percentage.pack(side=tk.BOTTOM, pady=3)

percentage_label = tk.Label(frame_percentage, text="Dimmer:", fg="black", bg="lightgray")
percentage_label.pack(side=tk.LEFT, padx=(45,10), pady=1)

style = ttk.Style()
style.configure("Custom.Horizontal.TScale",background="gray") 

# Aplicar o estilo personalizado à escala
percentage_slider = ttk.Scale(frame_percentage, from_=0, to=99, orient=tk.HORIZONTAL, command=send_percentage, style="Custom.Horizontal.TScale")
percentage_slider.pack(side=tk.LEFT)

porcentagem_texto1 = tk.Label(frame_percentage, text='C1: 0%', bg=color_p, font=("Arial", 10))
porcentagem_texto1.pack(side=tk.LEFT, padx=10, pady=1)

porcentagem_texto2 = tk.Label(frame_percentage, text='C2: 0%', bg=color_p, font=("Arial", 10))
porcentagem_texto2.pack(side=tk.LEFT, padx=10, pady=1)

btn_off_dimmer = tk.Button(frame_percentage, text="OFF", command=lambda: off_Dimmer(id_canal_entry.get()), bg="indianred", fg='black', font=("Arial", 10, "bold"))
btn_off_dimmer.pack(side=tk.LEFT, padx=5, pady=1)
# Frame para os elementos relacionados ao ID e CANAL
frame_id_canal = tk.Frame(root, bg=color_p)
frame_id_canal.pack(side=tk.BOTTOM, pady=0)  # Adiciona espaçamento vertical de 10 pixels

# Texto 'ID e Canal' atrás da caixa de inserir ID e canal
label_id_canal = tk.Label(frame_id_canal, text="Canal e ID:", bg=color_p, font=("Arial", 10))
label_id_canal.pack(side=tk.LEFT, padx=(0,5), pady=10)

# Caixa de texto para inserir o ID e o CANAL
id_canal_entry = tk.Entry(frame_id_canal, font=("Arial", 10))
id_canal_entry.pack(side=tk.LEFT, padx=(0,115), pady=0)

# Frame para os elementos relacionados ao envio de mensagem
frame_send = tk.Frame(root, bg=color_p)
frame_send.pack(side=tk.BOTTOM, pady=5)  # Adiciona espaçamento vertical de 10 pixels

# Texto 'Mensagem' atrás da caixa de inserir mensagem
label_message = tk.Label(frame_send, text="Mensagem:", bg=color_p, font=("Arial", 10))
label_message.pack(side=tk.LEFT, padx=(0), pady=1)

# Caixa de texto para enviar mensagens personalizadas
entry = tk.Entry(frame_send, font=("Arial", 10))
entry.pack(side=tk.LEFT, padx=(5,10), pady=5)

# Botão para enviar mensagem personalizada
btn_send = tk.Button(frame_send, text="Enviar", command=send_custom_message, bg="gray", fg='white', font=("Arial", 10, "bold"))
btn_send.pack(side=tk.LEFT, padx=(5,50), pady=1)  # Ajusta o padding do botão

# Botão para os elementos relacionados ao tópico
frame_topic = tk.Frame(root, bg=color_p)
frame_topic.pack(side=tk.BOTTOM, pady=1)  # Adiciona espaçamento vertical de 10 pixels

send_via_ip = tk.BooleanVar(value=False)
checkbox = tk.Checkbutton(frame_topic, text="Enviar via IP", variable=send_via_ip,command=on_checkbutton_toggled(None,True), bg=color_p, font=("Arial", 10))
checkbox.pack(side=tk.LEFT, padx=(10,5), pady=1)

# Texto 'Tópico' atrás da caixa de inserir tópico
label_topic = tk.Label(frame_topic, text="Tópico:", bg=color_p, font=("Arial", 10))
label_topic.pack(side=tk.LEFT, padx=(10,5), pady=10)

# Caixa de texto para inserir o tópico
topic_entry = tk.Entry(frame_topic, font=("Arial", 10))
topic_entry.insert(0, "TESTE_2024")
topic_entry.pack(side=tk.LEFT, padx=(0,10), pady=1)

# Botão para inserir o tópico
btn_insert_topic = tk.Button(frame_topic, text="OK", command=insert_topic, bg="gray", fg='white', font=("Arial", 10, "bold"))
btn_insert_topic.pack(side=tk.LEFT, padx=(5,10), pady=5)  # Ajusta o padding do botão

original_values = get_client_data()
combobox = ttk.Combobox(frame_topic, values=list(original_values.keys()))
combobox.pack(side=tk.LEFT, padx=(10,10), pady=1)
combobox.bind('<KeyRelease>', filter_combobox_suggestions)

version_label = tk.Label(root, text=f'Version: {Version}', bg="lightgray", font=("Arial", 8), padx=5, pady=5)
version_label.place(relx=1.0, rely=0.0, anchor='ne')

# Mantém o programa rodando para receber mensagens somente após o tópico ser definido
while not topic_set:
    root.update()
    time.sleep(0.05)

# Cria um cliente MQTT após o tópico ser definido
if not send_via_ip.get():
    create_and_connect_mqtt_client()

# Mantém a interface gráfica rodando
root.mainloop()
