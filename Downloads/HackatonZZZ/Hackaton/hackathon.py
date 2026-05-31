import time
import random
# Simula 24h de un día en bucle
hora = 0
while hora < 24:
    #Simulacion del movimiento del agua
    if 7 <= hora <= 22:
        litro_agua = random.randint(50, 100)
    else:
        #En horario no laboral el no deberia haber consumo
        litro_agua = 15
    print(f"Hora: {hora}:00 - Consumo: {litro_agua} L/min")
    # Si estuvieramos fuera de horario laboral y el consumo es mayor a lo establecido... se manda una alerta
    if hora > 18 or hora < 8:
        if litro_agua > 0:
            print("¡Alerta de Fuga! Consumo detectado en horario no laboral.")
            # Aqui se conecta la API que envia el mensaje a mantenimiento
    hora += 1
    time.sleep(0.5)