import time
import random
import json
import google.generativeai as genai
from twilio.rest import Client  # <--- NUEVA LIBRERÍA
# 1. CONFIGURACIÓN DE GEMINI IA
GENAI_API_KEY = "AQ.Ab8RN6Kja745qNbMT07rBM52iwRXidzw1TURLagtzbKMCnE98Q" 
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel(
    'gemini-2.5-flash',
    generation_config={"response_mime_type": "application/json"}
)
COSTO_POR_LITRO = 0.02 
# 2. CONFIGURACIÓN DE TWILIO (WHATSAPP REAL)
# Reemplaza estos datos con los que te dé la página de Twilio (Paso 3)
TWILIO_ACCOUNT_SID = "ACf208ac5f9717cb71160ea16976ae7864"
TWILIO_AUTH_TOKEN = "7003cfd39c878ea13e2a3ddfb04ca332"
MI_CELULAR_REAL = "whatsapp:+59176091732"  # Tu número con el código de Bolivia (+591)
# Este cliente maneja la conexión con los servidores de WhatsApp
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
# 3. SIMULADOR DE MONITOREO
hora = 0
while hora < 24:
    if 8 <= hora <= 18:
        litros_agua = random.randint(50, 100) 
        print(f"⏰ Hora: {hora:02d}:00 - Consumo: {litros_agua} L/min")
    else:
        litros_agua = 15 
        print(f"⏰ Hora: {hora:02d}:00 - Consumo: {litros_agua} L/min [Anomalía]")
        
        prompt = f"""
        Genera un objeto JSON estrictamente con esta estructura:
        {{
            "sensor_id": "SEC-B-04",
            "metrica": "{litros_agua} L/min",
            "estado": "Crítico",
            "timestamp": "2026-05-30T{hora:02d}:15:00Z",
            "notificacion_generada": "Redacta una alerta de WhatsApp para Carlos. Usa emojis. Menciona la pérdida de Bs. {litros_agua * COSTO_POR_LITRO:.2f} por minuto de forma alarmante."
        }}
        """
        try:
            # 1. Gemini genera el JSON
            respuesta = model.generate_content(prompt)
            print("\n🌐 [JSON generado por la IA]:")
            print(respuesta.text)
            
            # 2. Convertimos el texto de Gemini a un objeto Python para leer la alerta
            datos_alerta = json.loads(respuesta.text)
            texto_para_whatsapp = datos_alerta["notificacion_generada"]
            
            # 3. ENVÍO REAL A TU WHATSAPP
            print("🚀 Enviando alerta real por WhatsApp...")
            message = twilio_client.messages.create(
                from_='whatsapp:+14155238886', # Número oficial del Sandbox de Twilio
                body=texto_para_whatsapp,
                to=MI_CELULAR_REAL
            )
            print(f"✅ ¡Mensaje enviado! SID del envío: {message.sid}")
            print("=" * 60 + "\n")
            
            # Pausa de 5 segundos para que no te sature el celular en la simulación
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ Error en el proceso: {e}\n")
            
    hora += 1
    time.sleep(0.4)