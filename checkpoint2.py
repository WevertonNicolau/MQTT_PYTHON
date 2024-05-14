# Projeto: Software para analise tecnica do painel.
# Dev: Weverton Nicolau
# Version: 1.0.0.0


import paho.mqtt.client as mqtt
import time
import tkinter as tk
from tkinter import ttk

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

# Callback para quando a conexão com o broker é estabelecida
def on_connect(client, userdata, flags, rc):
    print("Conectado com o código de resultado: " + str(rc))
    # Subscreve ao tópico onde queremos receber o feedback
    client.subscribe(subscribe_topic)

# Função para criar um círculo com a cor padrão
def create_circle(placa, canal):
    if placa not in circle_colors:
        circle_colors[placa] = {}
        
    if canal not in circle_colors[placa]:
        default_color = None
        yellow_circle = tk.Canvas(circle_frames[placa], width=10, height=10, bg=default_color, highlightthickness=0)
        yellow_circle.create_oval(1, 1, 9, 9, fill=None)
        yellow_circle.pack(side=tk.TOP, padx=2, pady=10)
        circle_colors[placa][canal] = yellow_circle

# Função para lidar com mensagens MQTT recebidas
def handle_received_messages(msg):
    global circle_colors
    feedback = msg.payload.decode("utf-8")
    if feedback.strip() != "OK":
        # Limpa o conteúdo do widget de texto antes de adicionar um novo feedback
        received_messages_text.config(state="normal")
        received_messages_text.delete("1.0", tk.END)
        received_messages_text.insert(tk.END, "Feedback: " + feedback + "\n")
        received_messages_text.delete(f"1.{len(feedback)+10}", tk.END)
        received_messages_text.config(state="disabled")
''' try:
            start_idx = feedback.find("<")
            while start_idx != -1:
                end_idx = feedback.find(">", start_idx)
                if end_idx == -1:
                    break
                feedback_block = feedback[start_idx + 1:end_idx]  # Extrai o bloco de feedback
                placa_str = feedback_block[:2]
                placa = int(placa_str)
                channel_statuses = feedback_block[2:]

                placas = ["Placa 1", "Placa 2", "Placa 3", "Placa 4", "Placa 5", "Placa 6", "Placa 7", "Placa 8", "Placa 9"]

                # Verificando o estado dos canais e atualizando as cores dos círculos
                for idx, status in enumerate(channel_statuses):
                    placa_atual = placas[placa - 1]  # Obtemos a placa atual
                    canal = idx + 1  # Canais começam em 1
                    update_circle_color(placa_atual, canal, status)

                start_idx = feedback.find("<", end_idx)
        except ValueError as e:
            print('FHSBFIF', e)'''

# Callback para quando uma mensagem MQTT é recebida
def on_message(client, userdata, msg):
    handle_received_messages(msg)

def update_circle_color(placa, canal, status):
    #print("Placa:", placa)
    #print("Canal:", canal)
    #print("Status:", status)
    
    if placa in circle_colors:
        #print(circle_colors[placa])
        if canal in circle_colors[placa]:
            circle = circle_colors[placa][canal]  # Obtemos o círculo correspondente
            #print("Círculo:", circle)
            
            if status == "D":
                change_circle_color(circle, "red")  # Se o status for "D" (Desligado), altera a cor para vermelho
            elif status == "L":
                change_circle_color(circle, "green")  # Se o status for "L" (Ligado), altera a cor para verde

# Altera a cor de preenchimento do círculo
def change_circle_color(circle, color):
    circle.config(bg=color)


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

# Define o tópico e reinicia a conexão MQTT
def insert_topic():
    global publish_topic, subscribe_topic, topic_set, client

    topic = topic_entry.get()
    publish_topic = f'/Danf/{topic}/V3/Mqtt/Comando'
    subscribe_topic = f'/Danf/{topic}/V3/Mqtt/Feedback'
    topic_set = True

    # Reinicia a conexão MQTT com o novo tópico
    if client:
        client.disconnect()  # Desconecta do broker MQTT atual
        client.loop_stop()   # Para o loop de comunicação
        client = None        # Libera a referência do cliente

    # Cria um novo cliente MQTT com as configurações atualizadas
    create_and_connect_mqtt_client()

# Envia a porcentagem selecionada
def send_percentage(event=None):
    percentage = int(percentage_slider.get())  # Converte para inteiro
    id_canal = id_canal_entry.get()
    if percentage == '0':
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
    frame_on.grid(row=1, column=idx * 3, padx=(5, 2), pady=5)  # Espaçamento menor na lateral direita e um pouco de espaçamento vertical
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
        initial_status = "D"
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
    time.sleep(0.01)

# Cria um cliente MQTT após o tópico ser definido
create_and_connect_mqtt_client()


# Mantém a interface gráfica rodando
root.mainloop()
