import tkinter as tk
from PIL import Image, ImageTk
from mensages.mensages_functions import send_OFF_command, send_ON_command

lamp_labels = {}
lamp_frames = {}
color_p = 'lightgray'

# Inicialização da interface gráfica
root = tk.Tk()

imageOff = 'main/img/lampadaapagada.png'
imageOn = 'main/img/lampadaacesa.png'
imageNone = 'main/img/lampadavermelha.png'
imageOff = Image.open(imageOff).resize((16, 16), Image.LANCZOS)
imageOn = Image.open(imageOn).resize((16, 16), Image.LANCZOS)
imageNone = Image.open(imageNone).resize((16, 16), Image.LANCZOS)

# Convertendo imagens para PhotoImage após a criação da janela principal
imageOff = ImageTk.PhotoImage(imageOff)
imageOn = ImageTk.PhotoImage(imageOn)
imageNone = ImageTk.PhotoImage(imageNone)

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

def change_lamp_image(lamp_label, image):
    lamp_label.config(image=image)
    lamp_label.image = image

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


def inicia_interface():
    root.title("DANF - MQTT")
    root.title("DANF - MQTT")
    root.geometry("1370x700")  # Ajusta o tamanho da janela
    root.configure(bg=color_p)

    imageOff = 'main/img/lampadaapagada.png'
    imageOn = 'main/img/lampadaacesa.png'
    imageNone = 'main/img/lampadavermelha.png'
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
        
        root.mainloop()