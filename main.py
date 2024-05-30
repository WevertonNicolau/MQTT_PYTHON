# Projeto: Software para análise técnica do painel.
# Dev: Weverton Nicolau
# Version: 1.0.1.2

import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import ttk
import re
import time
from PIL import Image, ImageTk

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
    feedback = msg.payload.decode("utf-8")
    #print("Feedback recebido:", feedback)  # Mensagem de depuração
    
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
        feedback_label = tk.Label(lamp_frames[placa_str], image=imageNone, bg="white")
        feedback_label.pack(side=tk.TOP, padx=2, pady=5)
        lamp_labels[placa_str]["feedback"] = feedback_label
    if canal not in lamp_labels[placa_str]:
        default_image = imageNone
        try:
            lamp_label = tk.Label(lamp_frames[placa_str], image=default_image, bg="white")
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
    client.connect(server, port)
    client.loop_start()

# Envia uma mensagem MQTT
def send_message(message):
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
        else:
            if message[0] == 'D':
                try:
                    if message[4]:
                        client.publish(publish_topic, message)
                        print('Mensagem enviada:', message) 
                except:
                    received_messages_text.config(state="normal")
                    received_messages_text.delete("1.0", tk.END)
                    received_messages_text.insert(tk.END, "Insira o Canal e o ID")
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
    send_message(message)

# Envia uma mensagem para ligar um canal específico em uma placa
def send_ON_command(channel, placa):
    placa_str = f"0{placa}" if placa < 10 else str(placa)  # Adiciona um zero à esquerda se a placa for menor que 10
    send_message(f"OFONC{channel}{placa_str}")

# Envia uma mensagem para desligar um canal específico em uma placa
def send_OFF_command(channel, placa):
    placa_str = f"0{placa}" if placa < 10 else str(placa)  # Adiciona um zero à esquerda se a placa for menor que 10
    send_message(f"OFFFC{channel}{placa_str}")

# Envia uma mensagem para ligar todos os canais de todas as placas
def send_ON_geral():
    send_message("OFAN")

# Envia uma mensagem para desligar todos os canais de todas as placas
def send_OFF_geral():
    send_message("OFAO")


def destroy_lamp_frames():
    global lamp_frames, lamp_labels
    for placa, frame in lamp_frames.items():
        frame.destroy()
    lamp_frames = {}
    lamp_labels = {}
    for idx, placa in enumerate(placas):
        lamp_frame = tk.Frame(frame_principal, bg="white")
        lamp_frame.grid(row=1, column=idx * 3 + 2, padx=(1, 15), pady=5)
        lamp_frames[placa] = lamp_frame
        for canal in range(1, 9):
            create_lamp_label(placa, canal)
            
    lamp_label_dimmer1 = tk.Label(frame_principal, image=imageNone, bg="white")
    lamp_label_dimmer1.grid(row=1, column=len(placas)*3 + 2, padx=(1, 15), pady=5)
    lamp_label_dimmer2 = tk.Label(frame_principal, image=imageNone, bg="white")
    lamp_label_dimmer2.grid(row=1, column=len(placas)*3 + 4, padx=(1, 15), pady=5)

# Define o tópico e reinicia a conexão MQTT
def insert_topic():
    global publish_topic, subscribe_topic, topic_set, client
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
        send_message(f"DM0{percentage}{id_canal}")
    else:
        send_message(f"DM{percentage}{id_canal}")

def off_Dimmer(canal_id):
    send_message(F'DM00{canal_id}')

# Atualiza o texto da porcentagem do canal
def atualizar_porcentagem_texto1(porcentagem):
    porcentagem_texto1.config(text=f'C1: {porcentagem}%')

def atualizar_porcentagem_texto2(porcentagem):
    porcentagem_texto2.config(text=f'C2: {porcentagem}%')

def send_ON_placa(placa):
    for channel in range(1, 9):
        time.sleep(0.02)
        if placa < 10:
            send_message(f"OFONC{channel}0{placa}")
        else:
            send_message(f"OFONC{channel}{placa}")
# Função para desligar todos os canais de uma placa específica
def send_OFF_placa(placa):
    for channel in range(1, 9):
        time.sleep(0.02)
        if placa < 10:
            send_message(f"OFFFC{channel}0{placa}")
        else:
            send_message(f"OFFFC{channel}{placa}")

# Inicialização da interface gráfica
root = tk.Tk()
root.title("DANF MQTT - Beta")
root.geometry("1370x730")  # Ajusta o tamanho da janela

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
frame_principal = tk.Frame(canvas, bg="white")
canvas.create_window((0, 0), window=frame_principal, anchor='nw')

# Lista de placas
placas = [f"Placa {i}" for i in range(1, 17)]
# Dicionário para armazenar os frames de círculos das bolinhas
lamp_frames = {}

# Criar grupos de botões para cada placa
for idx, placa in enumerate(placas):
    lamp_frame = tk.Frame(frame_principal, bg="white")
    lamp_frame.grid(row=1, column=idx * 3 + 2, padx=(1, 15), pady=5)  # Espaçamento menor na lateral esquerda e um pouco de espaçamento vertical
    lamp_frame.grid_propagate(False)  # Desativa a propagação automática de tamanho

    lamp_labels[placa] = {}
    # Texto da placa
    label_placa = tk.Label(frame_principal, text=placa, padx=10, bg="white", fg="black", font=("Arial", 12, "bold"))
    label_placa.grid(row=0, column=idx * 3, columnspan=3)

    # Frame para os botões ON
    frame_on = tk.Frame(frame_principal, bg="white")
    frame_on.grid(row=1, column=idx * 3, padx=(2, 2), pady=5)  # Espaçamento menor na lateral direita e um pouco de espaçamento vertical
    frame_on.grid_propagate(False)  # Desativa a propagação automática de tamanho

    # Frame para os botões OFF
    frame_off = tk.Frame(frame_principal, bg="white")
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
frame_feedback = tk.Frame(root, bg="white")
frame_feedback.pack(side=tk.BOTTOM, pady=10)  # Adiciona espaçamento vertical de 10 pixels

# Widget de texto para exibir mensagens recebidas
received_messages_text = tk.Text(frame_feedback, height=10, width=50, bg="lightgrey", font=("Arial", 10), state="disabled")
received_messages_text.pack(side=tk.BOTTOM, padx=10, pady=5)

# Botões para ligar/desligar geral
frame_geral = tk.Frame(root, bg="white")
frame_geral.pack(side=tk.BOTTOM, pady=10)

btn_on_geral = tk.Button(frame_geral, text="ON Geral", command=send_ON_geral, bg="lightgreen", fg="white", font=("Arial", 10, "bold"))
btn_on_geral.pack(side=tk.LEFT, padx=5, pady=1)

btn_off_geral = tk.Button(frame_geral, text="OFF Geral", command=send_OFF_geral, bg="indianred", fg="white", font=("Arial", 10, "bold"))
btn_off_geral.pack(side=tk.LEFT, padx=5, pady=1)

# Frame para a barra de porcentagem
frame_percentage = tk.Frame(root, bg="white")
frame_percentage.pack(side=tk.BOTTOM, pady=3)  # Adiciona espaçamento vertical de 10 pixels

# Label para a barra de porcentagem
percentage_label = tk.Label(frame_percentage, text="DIMMER:", bg="white", font=("Arial", 10))
percentage_label.pack(side=tk.LEFT, padx=10, pady=1)

# Slider para a barra de porcentagem
percentage_slider = ttk.Scale(frame_percentage, from_=00, to=99, orient=tk.HORIZONTAL, command=send_percentage)
percentage_slider.pack(side=tk.LEFT, padx=10, pady=1)

porcentagem_texto1 = tk.Label(frame_percentage, text='C1: 0%', bg="white", font=("Arial", 10))
porcentagem_texto1.pack(side=tk.LEFT, padx=10, pady=1)

porcentagem_texto2 = tk.Label(frame_percentage, text='C2: 0%', bg="white", font=("Arial", 10))
porcentagem_texto2.pack(side=tk.LEFT, padx=10, pady=1)

btn_off_dimmer = tk.Button(frame_percentage, text="OFF", command=lambda: off_Dimmer(id_canal_entry.get()), bg="indianred", fg="white", font=("Arial", 10, "bold"))
btn_off_dimmer.pack(side=tk.LEFT, padx=5, pady=1)
# Frame para os elementos relacionados ao ID e CANAL
frame_id_canal = tk.Frame(root, bg="white")
frame_id_canal.pack(side=tk.BOTTOM, pady=0)  # Adiciona espaçamento vertical de 10 pixels

# Texto 'ID e Canal' atrás da caixa de inserir ID e canal
label_id_canal = tk.Label(frame_id_canal, text="Canal e ID:", bg="white", font=("Arial", 10))
label_id_canal.pack(side=tk.LEFT, padx=10, pady=0)

# Caixa de texto para inserir o ID e o CANAL
id_canal_entry = tk.Entry(frame_id_canal, font=("Arial", 10))
id_canal_entry.pack(side=tk.LEFT, padx=10, pady=0)

# Frame para os elementos relacionados ao envio de mensagem
frame_send = tk.Frame(root, bg="white")
frame_send.pack(side=tk.BOTTOM, pady=10)  # Adiciona espaçamento vertical de 10 pixels

# Texto 'Mensagem' atrás da caixa de inserir mensagem
label_message = tk.Label(frame_send, text="Mensagem:", bg="white", font=("Arial", 10))
label_message.pack(side=tk.LEFT, padx=10, pady=1)

# Caixa de texto para enviar mensagens personalizadas
entry = tk.Entry(frame_send, font=("Arial", 10))
entry.pack(side=tk.LEFT, padx=10, pady=10)

# Botão para enviar mensagem personalizada
btn_send = tk.Button(frame_send, text="Enviar Mensagem", command=send_custom_message, bg="blue", fg="white", font=("Arial", 10, "bold"))
btn_send.pack(side=tk.LEFT, padx=5, pady=1)  # Ajusta o padding do botão

# Botão para os elementos relacionados ao tópico
frame_topic = tk.Frame(root, bg="white")
frame_topic.pack(side=tk.BOTTOM, pady=1)  # Adiciona espaçamento vertical de 10 pixels

# Texto 'Tópico' atrás da caixa de inserir tópico
label_topic = tk.Label(frame_topic, text="Tópico:", bg="white", font=("Arial", 10))
label_topic.pack(side=tk.LEFT, padx=10, pady=1)

# Caixa de texto para inserir o tópico
topic_entry = tk.Entry(frame_topic, font=("Arial", 10))
topic_entry.insert(0, "TESTE_2024")
topic_entry.pack(side=tk.LEFT, padx=10, pady=1)

# Botão para inserir o tópico
btn_insert_topic = tk.Button(frame_topic, text="Inserir Tópico", command=insert_topic, bg="blue", fg="white", font=("Arial", 10, "bold"))
btn_insert_topic.pack(side=tk.LEFT, padx=5, pady=5)  # Ajusta o padding do botão

# Mantém o programa rodando para receber mensagens somente após o tópico ser definido
while not topic_set:
    root.update()
    time.sleep(0.05)

# Cria um cliente MQTT após o tópico ser definido
create_and_connect_mqtt_client()

# Mantém a interface gráfica rodando
root.mainloop()
