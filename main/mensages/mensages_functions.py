

def send_ON_command(channel, placa):
    placa_str = f"0{placa}" if placa < 10 else str(placa)  # Adiciona um zero à esquerda se a placa for menor que 10
    send_message(f"OFONC{channel}{placa_str}",via_ip=send_via_ip.get())

# Envia uma mensagem para desligar um canal específico em uma placa
def send_OFF_command(channel, placa):
    placa_str = f"0{placa}" if placa < 10 else str(placa)  # Adiciona um zero à esquerda se a placa for menor que 10
    send_message(f"OFFFC{channel}{placa_str}",via_ip=send_via_ip.get())
