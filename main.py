"""
╔══════════════════════════════════════════════════════════════════════╗
║         AquaAlert IoT — Sistema de Monitoreo Automatizado            ║
║    Agente IA Autónomo Multi-Sector | Build with AI Hackaton 2026     ║
║                  Santa Cruz de la Sierra, Bolivia                    ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os
import time
import json
import random
from datetime import datetime
from google import genai
from google.genai import types
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv

# ══════════════════════════════════════════════════════════════════════
# 1. ENTORNO Y CONFIGURACIÓN (PROTEGIDA CON VARIABLES DE ENTORNO)
# ══════════════════════════════════════════════════════════════════════
load_dotenv()

# Lectura segura desde el archivo .env para evitar bloqueos de seguridad en GitHub
api_key          = os.getenv("GEMINI_API_KEY")
TWILIO_SID       = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN     = os.getenv("TWILIO_AUTH_TOKEN")
TELEFONO_DESTINO = os.getenv("TELEFONO_DESTINO", "whatsapp:+59176091732") 
TWILIO_FROM      = os.getenv("TWILIO_FROM", "whatsapp:+14155238886") 

if not api_key:
    print("❌ Error: No se ha detectado la variable GEMINI_API_KEY en el archivo .env.")
    exit(1)

if not TWILIO_SID or not TWILIO_TOKEN:
    print("⚠️ Advertencia: Credenciales de Twilio no detectadas en el archivo .env. Las alertas de WhatsApp estarán desactivadas.")

# Inicialización de clientes de API
client = genai.Client(api_key=api_key)
twilio_client = Client(TWILIO_SID, TWILIO_TOKEN) if TWILIO_SID and TWILIO_TOKEN else None

INTERVALO_CICLO_SEGUNDOS = 30 

# ══════════════════════════════════════════════════════════════════════
# 2. BASE DE SENSORES POR SECTOR
# ══════════════════════════════════════════════════════════════════════
CONFIG_SECTORES = {
    "SEN-001": {"zona": "Zona Norte - Residencial", "p_nominal": (40, 50), "f_nominal": (10.0, 15.0)},
    "SEN-002": {"zona": "Zona Centro - Comercial", "p_nominal": (35, 45), "f_nominal": (30.0, 40.0)},
    "SEN-003": {"zona": "Zona Sur - Industrial", "p_nominal": (70, 85), "f_nominal": (4.0, 8.0)},
    "SEN-004": {"zona": "Distrito Este - Tanque Principal", "p_nominal": (55, 65), "f_nominal": (80.0, 120.0)}
}

# ══════════════════════════════════════════════════════════════════════
# 3. GENERADOR AUTOMÁTICO DE DATOS
# ══════════════════════════════════════════════════════════════════════
def simular_lecturas_sensores() -> list:
    lecturas_actuales = []
    for sensor_id, config in CONFIG_SECTORES.items():
        suerte = random.random()
        p_min, p_max = config["p_nominal"]
        f_min, f_max = config["f_nominal"]
        
        if suerte < 0.60: 
            presion = round(random.uniform(p_min, p_max), 1)
            flujo = round(random.uniform(f_min, f_max), 1)
            estado = "Normal"
        elif suerte < 0.85:
            presion = round(random.uniform(p_min * 0.3, p_min * 0.6), 1)
            flujo = round(random.uniform(f_max * 1.2, f_max * 1.4), 1) 
            estado = "Anomalía (Baja Presión)"
        else:
            presion = 5.0
            flujo = 0.0 
            estado = "Crítico (Sin Flujo)"
            
        lecturas_actuales.append({
            "id": sensor_id, "zona": config["zona"], "presion": presion, "flujo": flujo, "estado": estado
        })
    return lecturas_actuales

# ══════════════════════════════════════════════════════════════════════
# 4. ENVÍO DE WHATSAPP DIRECTO (Texto enriquecido de la IA)
# ══════════════════════════════════════════════════════════════════════
def enviar_whatsapp_predictivo(notificacion_texto: str):
    """ Envía a WhatsApp el reporte detallado que redactó la IA """
    if not twilio_client:
        print("ℹ️ [Twilio] Envío omitido de WhatsApp: Faltan credenciales en el archivo .env")
        return

    try:
        twilio_client.messages.create(
            from_=TWILIO_FROM,
            body=notificacion_texto, 
            to=TELEFONO_DESTINO
        )
        print(f"   📱 [Twilio WhatsApp] ¡Reporte predictivo enviado con éxito!")
    except TwilioRestException as e:
        print(f"   ❌ Error de Twilio en WhatsApp: {e.msg}")
        print("   💡 TIP: Si te da error de plantilla, recuerda mandarle cualquier mensaje (ej: 'hola') al número del bot desde tu celular para activar la ventana de 24 horas.")

# ══════════════════════════════════════════════════════════════════════
# 5. MOTOR DE IA CON REDACCIÓN DE REPORTES
# ══════════════════════════════════════════════════════════════════════
def analizar_red_con_ia(datos_sensores: list):
    print(f"\n📡 [Telemetría Recibida] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("----------------------------------------------------------------")
    
    datos_sensores_str = json.dumps(datos_sensores, indent=2, ensure_ascii=False)
    
    prompt = f"""
    Actúa como un Ingeniero Hidráulico Experto de AquaAlert en Santa Cruz, Bolivia.
    Analiza la siguiente telemetría en tiempo real:
    {datos_sensores_str}
    
    Si encuentras algún sensor en estado 'Anomalía' o 'Crítico', debes redactar una alerta técnica predictiva e impactante para WhatsApp.
    
    ESTRUCTURA OBLIGATORIA DEL MENSAJE DE ALERTA:
    "¡AquaAlert 🚨 PREVENCIÓN DE FUGA en [ID_SENSOR]! Detectada [breve descripción del problema físico basado en los datos]. Se ha sugerido la acción inmediata de [ACCIÓN RECOMENDADA] para evitar una ruptura inminente. Flujo actual: [X] L/s, Presión: [Y] PSI. Estimamos una falla en ~[Z] horas si no se interviene. Costo estimado de pérdida evitada para el turno restante: Bs. [Cálculo realista en Bolivianos]. Equipo de mantenimiento alertado para revisión. 🛠️"
    
    - Si hay más de un sensor con problemas, pon cada reporte separado por una línea divisoria.
    - Si TODO el sistema está normal, responde estrictamente: "SISTEMA OPERANDO CON TOTAL NORMALIDAD".
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        reporte_ia = response.text.strip()
        
        print("\n🤖 === REPORTE AGENTE IA [AQUAALERT] ===")
        print(reporte_ia)
        print("=========================================\n")
        
        if "SISTEMA OPERANDO CON TOTAL NORMALIDAD" not in reporte_ia:
            print("🚀 Despachando reporte predictivo completo a WhatsApp...")
            enviar_whatsapp_predictivo(reporte_ia)
            
    except Exception as e:
        print(f"❌ Error en la llamada a Gemini: {e}")

# ══════════════════════════════════════════════════════════════════════
# 6. BUCLE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════
def main():
    print("\n" + "═"*65)
    print("   💧 AquaAlert IoT — MONITOREO CONTINUO EN WHATSAPP")
    print("═"*65)
    
    ciclo = 0
    while True:
        ciclo += 1
        print(f"\n🔄 INICIANDO CICLO DE ANÁLISIS #{ciclo}")
        
        datos_actuales = simular_lecturas_sensores()
        
        # Imprimir telemetría en consola
        for s in datos_actuales:
            print(f"   [{s['id']}] {s['zona']:-<35} P: {s['presion']} PSI | F: {s['flujo']} L/s | Estado: {s['estado']}")
        
        # Procesar datos y gatillar WhatsApp si corresponde
        analizar_red_con_ia(datos_actuales)
        
        print(f"⏱️ Ciclo #{ciclo} completado. Próximo escaneo en {INTERVALO_CICLO_SEGUNDOS}s...\n")
        time.sleep(INTERVALO_CICLO_SEGUNDOS)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Sistema detenido por el operador.")
