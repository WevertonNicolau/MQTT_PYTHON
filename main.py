# Projeto: Software para analise tecnica do painel.
# Dev: Weverton Nicolau
# Version: 1.0.0.3

import paho.mqtt.client as mqtt
import tkinter as tk
from tkinter import ttk
import re
import time

# Informações do servidor MQTT
server = 'super-author.cloudmqtt.com'
port = 1883
username = 'tdmstjgu'
password = 'mBv2M7HusSx8'
default_topic = 'null'
publish_topic = f'/Danf/{default_topic}/V3/Mqtt/Comando'
subscribe_topic = f'/Danf/{default_topic}/V3/Mqtt/Feedback'

# Dicionário para armazenar os círculos das bolinhas e suas cores
circle_colors = {}

# Variável para verificar se o tópico foi definido
topic_set = False

# Variável para armazenar o cliente MQTT
client = None

def on_connect(client, userdata, flags, rc):
    print("Conectado com o código de resultado:", rc)
    # Subscreve ao tópico onde queremos receber o feedback
    client.subscribe(subscribe_topic)

# Função para tratar o feedback recebido
def tratar_feedback(feedback):
    resultados = []
    segmentos = feedback.split('>')
    for segmento in segmentos:
        if segmento:
            placa = segmento[1:3]
            canais_estados = re.findall(r'(\d)([LD])', segmento[3:])
            resultado = {"placa": placa}
            for i, (canal, estado) in enumerate(canais_estados, start=1):
                resultado[f"canal{i}"] = {"numero": canal, "estado": estado}
            resultados.append(resultado)
            print(resultado)
    return resultados

# Callback para quando uma mensagem MQTT é recebida
def on_message(client, userdata, msg):
    feedback = msg.payload.decode("utf-8")
    print("Feedback recebido:", feedback)  # Mensagem de depuração
    
    if feedback.strip() != "OK":
        received_messages_text.config(state="normal")
        received_messages_text.delete("1.0", tk.END)
        received_messages_text.insert(tk.END, "Feedback: " + feedback + "\n")
        received_messages_text.delete(f"1.{len(feedback)+10}", tk.END)
        received_messages_text.config(state="disabled")

    resultados = tratar_feedback(feedback)
    #print("Resultados:", resultados)  # Mensagem de depuração
    
    for resultado in resultados:
        placa = resultado["placa"]
        
        for i in range(1, 9):
            canal = f"canal{i}"
            if canal in resultado:
                estado = resultado[canal]["estado"]
                update_circle_color(placa, i, estado)

def create_circle(placa, canal):
    placa_str = str(placa)  # Convertendo para string
    if placa_str not in circle_colors:
        circle_colors[placa_str] = {}
    if canal not in circle_colors[placa_str]:
        default_color = "yellow"  # Definindo a cor padrão como amarelo
        try:
            circle = tk.Canvas(circle_frames[placa_str], width=12, height=12, highlightthickness=0)
            circle.create_oval(2, 2, 10, 10, fill=default_color)  # Cria uma oval preenchida com a cor padrão

            circle.pack(side=tk.TOP, padx=2, pady=9)
            circle_colors[placa_str][canal] = circle
        except Exception as e:
            print("Erro ao criar círculo:", e)
    else:
        # Se o círculo já existe, apenas atualiza sua cor
        update_circle_color(placa, canal, "D")

def update_circle_color(placa, canal, status):
    placa_str = 'Placa ' + str(placa[1])
    if placa_str in circle_colors:
        if canal in circle_colors[placa_str]:
            circle = circle_colors[placa_str][canal]  # Obtemos o círculo correspondente
                
            if status == "D":
                change_circle_color(circle, "red")  # Se o status for "D" (Desligado), altera a cor para vermelho
            elif status == "L":
                change_circle_color(circle, "green")  # Se o status for "L" (Ligado), altera a cor para verde
            else:
                change_circle_color(circle, "yellow")
                print("Status desconhecido:", status)  # Mensagem de depuração
        else:
            print("Canal não encontrado para placa", placa_str)  # Mensagem de depuração
    else:
        print("Placa não encontrada:", placa_str)  # Mensagem de depuração

def change_circle_color(circle, color):
    circle.itemconfig(1, fill=color)

# Cria e conecta o cliente MQTT
def create_and_connect_mqtt_client():
    global client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username, password)
    client.connect(server, port)
    client.loop_start()

# Envia a mensagem 'SA' a cada 10 segundos
def send_SA():
    client.publish(publish_topic, "SA")
    #root.after(10000, send_SA)

# Envia uma mensagem MQTT
def send_message(message):
    message = message.upper()
    client.publish(publish_topic, message)
    print('Mensagem enviada:', message)

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

def destroy_circle_frames():
    global circle_frames, circle_colors
    for placa, frame in circle_frames.items():
        frame.destroy()  # Destroi o frame da placa
    circle_frames = {}  # Limpa o dicionário de frames
    circle_colors = {}  # Limpa o dicionário de cores

    # Recria os frames de círculos das bolinhas com a cor amarela para cada placa
    for idx, placa in enumerate(placas):
        circle_frame = tk.Frame(frame_principal, bg="white")
        circle_frame.grid(row=1, column=idx * 3 + 2, padx=(1, 15), pady=5)  # Espaçamento menor na lateral esquerda e um pouco de espaçamento vertical
        circle_frame.grid_propagate(False)  # Desativa a propagação automática de tamanho
        circle_frames[placa] = circle_frame

        circle_colors[placa] = {}  # Inicializa o dicionário para esta placa
        for channel in range(1, 9):
            create_circle(placa, channel)
            update_circle_color(placa, channel, "D")  

# Define o tópico e reinicia a conexão MQTT
def insert_topic():
    global publish_topic, subscribe_topic, topic_set, client
    topic = topic_entry.get()
    publish_topic = f'/Danf/{topic}/V3/Mqtt/Comando'
    subscribe_topic = f'/Danf/{topic}/V3/Mqtt/Feedback'
    topic_set = True

    destroy_circle_frames()

    # Reinicia a conexão MQTT com o novo tópico
    if client:
        client.disconnect()  # Desconecta do broker MQTT atual
        client.loop_stop()   # Para o loop de comunicação
        client = None        # Libera a referência do cliente

    create_and_connect_mqtt_client()

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

# Inicialização da interface gráfica
root = tk.Tk()
root.title("DANF MQTT - Beta")
root.geometry("1370x690")  # Ajusta o tamanho da janela

# Frame principal
frame_principal = tk.Frame(root, bg="white")
frame_principal.pack(side=tk.BOTTOM, pady=10)  # Adiciona espaçamento vertical de 10 pixels

# Lista de placas
placas = ["Placa 1", "Placa 2", "Placa 3", "Placa 4", "Placa 5", "Placa 6", "Placa 7", "Placa 8", "Placa 9"]

# Dicionário para armazenar os frames de círculos das bolinhas
circle_frames = {}

# Criar grupos de botões para cada placa
for idx, placa in enumerate(placas):
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

    # Frame para os círculos das bolinhas
    circle_frame = tk.Frame(frame_principal, bg="white")
    circle_frame.grid(row=1, column=idx * 3 + 2, padx=(1, 15), pady=5)  # Espaçamento menor na lateral esquerda e um pouco de espaçamento vertical
    circle_frame.grid_propagate(False)  # Desativa a propagação automática de tamanho

    # Salva a referência ao frame do círculo
    circle_frames[placa] = circle_frame

    # Criando os botões para os canais 1 a 8 da Placa
    circle_colors[placa] = {}  # Inicializa o dicionário para esta placa
    for channel in range(1, 9):
        initial_status = None
        create_circle(placa, channel)
        update_circle_color(placa, channel, initial_status)

        btn_channel_on = tk.Button(frame_on, text=f"Canal {channel}", command=lambda ch=channel, p=idx + 1: send_ON_command(ch, p), bg="lightgreen", fg="black", width=6, padx=1, pady=1, font=("Arial", 9, "bold"))
        btn_channel_on.pack(side=tk.TOP, padx=2, pady=2)

        btn_channel_off = tk.Button(frame_off, text=f"Canal {channel}", command=lambda ch=channel, p=idx + 1: send_OFF_command(ch, p), bg="indianred", fg="black", width=6, padx=1, pady=1, font=("Arial", 9, "bold"))
        btn_channel_off.pack(side=tk.TOP, padx=2, pady=2)

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
