import re

def tratar_feedback(feedback):
    print("Feedback recebido:", feedback)  # Imprimir o feedback recebido
    
    # Remover o '<' do início e dividir o feedback em segmentos com base no caractere '>'
    segmentos = feedback.split('>')
    
    # Inicializar lista para armazenar os resultados
    resultados = []

    # Iterar sobre cada segmento
    for segmento in segmentos:
        if segmento:
            # Encontrar a placa
            indice_placa = segmento.find('C')
            placa = segmento[:indice_placa]
            placa = placa[1:]  # Remover o '<'
            
            # Encontrar todos os canais e seus estados na placa
            canais_estados = re.findall(r'(\d)([LD])', segmento[indice_placa:])

            # Construir o resultado
            resultado = {"placa": placa}
            for i, (canal, estado) in enumerate(canais_estados, start=1):
                resultado[f"canal{i}"] = {"numero": canal, "estado": estado}

            resultados.append(resultado)

    return resultados

feedback = '<02C1DC2LC3DC4DC5DC6DC7DC8D><04C1DC2DC3DC4LC5DC6DC7DC8D><12C1LC2DC3LC4LC5DC6DC7DC8D><09C1DC2DC3DC4LC5DC6DC7DC8L>'
leitura = tratar_feedback(feedback)
for leitura_individual in leitura:
    print(leitura_individual)
