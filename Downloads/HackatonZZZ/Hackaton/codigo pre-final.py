"""
╔══════════════════════════════════════════════════════════════════════╗
║           AquaAlert IoT — Agente IA de Monitoreo Hídrico            ║
║  Estrategia de Refinamiento Piloto B2B | Build with AI Hackaton 2026 ║
║                   Santa Cruz de la Sierra, Bolivia                   ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import time
import json
import os
import csv
import google.generativeai as genai
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import pydantic
from dotenv import load_dotenv

# ══════════════════════════════════════════════════════════════════════
# 1. ENTORNO Y CREDENCIALES
# ══════════════════════════════════════════════════════════════════════
load_dotenv()

# Variables de entorno (Usa tokens quemados si no manejas archivo .env aún)
GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6KiwWuQ3vph8uc2SgCoWkPTRBW6-56irq7pN2M-1aEXXA")
TWILIO_SID        = os.getenv("TWILIO_ACCOUNT_SID", "ACf208ac5f9717cb71160ea16976ae7864")
TWILIO_TOKEN      = os.getenv("TWILIO_AUTH_TOKEN", "7003cfd39c878ea13e2a3ddfb04ca332")
TELEFONO_DESTINO  = os.getenv("TELEFONO_DESTINO", "whatsapp:+59176091732")
TWILIO_FROM       = "whatsapp:+14155238886"

# Inicialización de servicios
genai.configure(api_key=GEMINI_API_KEY)
twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)

# ══════════════════════════════════════════════════════════════════════
# 2. DEFINICIÓN DEL ESQUEMA DE DATOS (CONTRATO DE SALIDA)
# ══════════════════════════════════════════════════════════════════════
class DecisionAgente(pydantic.BaseModel):
    analisis_contexto: str
    probabilidad_fuga_porcentaje: int
    tiempo_estimado_falla_horas: int
    es_una_emergencia: bool
    es_alerta_preventiva: bool
    accion_automatica_iot: str
    costo_estimado_bolivianos: float
    notificacion_generada: str

# Instanciar el modelo de inteligencia artificial
model = genai.GenerativeModel("gemini-2.5-flash")

# ══════════════════════════════════════════════════════════════════════
# 3. MÓDULOS DE INGENIERÍA (LOGS, WHATSAPP Y PROMPT)
# ══════════════════════════════════════════════════════════════════════
def guardar_en_registro_piloto(sensor_id: str, escenario: str, decision: DecisionAgente):
    """
    Registra localmente cada predicción de la IA. Este archivo es el núcleo 
    de la estrategia de refinamiento (Data Moat) durante el año de pruebas.
    """
    archivo = "registro_piloto.csv"
    existe = os.path.exists(archivo)
    
    with open(archivo, mode="a", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        if not existe:
            # Encabezados estructurados para auditoría de planta
            escritor.writerow([
                "Fecha_Hora", "Sensor_ID", "Escenario_Simulado", 
                "Prediccion_Fuga_%", "Tiempo_Falla_Horas", 
                "Accion_IoT_Ejecutada", "Costo_Estimado_Bs", 
                "Validacion_Ingeniero_Planta"
            ])
        
        escritor.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            sensor_id,
            escenario,
            decision.probabilidad_fuga_porcentaje,
            decision.tiempo_estimado_falla_horas,
            decision.accion_automatica_iot,
            decision.costo_estimado_bolivianos,
            "PENDIENTE (Auditoría Mensual)"  # Campo manual para el refinamiento de la IA
        ])
    print(f"  💾 Telemetría archivada en '{archivo}' para calibración algorítmica.")

def enviar_whatsapp(mensaje: str, tipo: str) -> bool:
    """Dispara las alertas críticas hacia los teléfonos del personal de la planta."""
    try:
        twilio_client.messages.create(
            from_=TWILIO_FROM,
            body=mensaje,
            to=TELEFONO_DESTINO,
        )
        print(f"  ✅ Canal de comunicación activo: Mensaje {tipo} enviado por WhatsApp.")
        return True
    except TwilioRestException as e:
        print(f"  ❌ Falla de gateway en mensajería Twilio: {e.msg}")
        return False

def construir_prompt(sensor_id: str, hora: int, litros: int, presion: int, es_laboral: bool, historial: list) -> str:
    """
    Prompt de Contexto Industrial Estricto.
    Elimina alucinaciones (como el error de las 1000 horas) mediante reglas matemáticas directas.
    """
    return f"""
Eres AquaAlert, un Agente de IA Industrial de Mantenimiento Hídrico Predictivo para Santa Cruz, Bolivia.
Tu objetivo es analizar la telemetría actual y llenar el esquema JSON de forma ultra-realista siguiendo estas reglas de ingeniería:

HISTORIAL RECIENTE DE LAS ÚLTIMAS HORAS:
{json.dumps(historial, indent=2)}

LECTURA ACTUAL DEL SENSOR '{sensor_id}':
  • Hora actual: {hora:02d}:00
  • Flujo actual: {litros} L/min
  • Presión actual: {presion} PSI
  • ¿Planta operando/activa?: {es_laboral}

REGLAS ESTRICTAS DE DIAGNÓSTICO PARA EL JSON:

1. SI ELIGEN EL ESCENARIO 1 (Operación Normal: {presion} PSI, planta activa):
   - Todo está perfecto. No hay fallas ni anomalías.
   - probabilidad_fuga_porcentaje = 0
   - tiempo_estimado_falla_horas = 0
   - es_alerta_preventiva = false
   - es_una_emergencia = false
   - accion_automatica_iot = "MANTENER_NORMAL"
   - analisis_contexto = "Presión y flujo estables dentro de los rangos nominales de producción."

2. SI ELIGEN EL ESCENARIO 2 (Micro-fuga: {presion} PSI, planta cerrada de madrugada):
   - El historial muestra que la presión cae constantemente (45 -> 41 -> 38 -> {presion}). Esto es una micro-fuga activa.
   - Regla matemática: La presión disminuye a un ritmo de 3 PSI por hora. Si la presión actual es {presion} PSI y el colapso crítico ocurre al bajar de 20 PSI, restan exactamente 4 o 5 horas antes del daño total del ducto.
   - tiempo_estimado_falla_horas = Pon obligatoriamente un número entero entre 4 y 5 (¡NUNCA pongas números altos como 1000!).
   - probabilidad_fuga_porcentaje = entre 80 y 90
   - es_alerta_preventiva = true
   - es_una_emergencia = false
   - accion_automatica_iot = "REDUCIR_PRESION"
   - analisis_contexto = "Alerta Predictiva. Desaceleración constante de presión detectada en horario inactivo. Firma matemática compatible con micro-fisura en desarrollo."

3. SI ELIGEN EL ESCENARIO 3 (Ruptura Crítica: {presion} PSI, flujo masivo):
   - El ducto colapsó por completo de manera inmediata.
   - probabilidad_fuga_porcentaje = 100
   - tiempo_estimado_falla_horas = 0 (Ya falló, la acción es inmediata)
   - es_alerta_preventiva = false
   - es_una_emergencia = true
   - accion_automatica_iot = "CERRAR_VALVULA"
   - analisis_contexto = "EMERGENCIA CRÍTICA. Caída drástica de presión por debajo del límite estructural acompañada de un pico de flujo masivo. Se ordena el aislamiento del Sector."
"""

def consultar_agente(prompt: str) -> DecisionAgente | None:
    """Realiza la petición a Gemini exigiendo la estructura JSON estricta."""
    try:
        respuesta = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=DecisionAgente,
            ),
        )
        return DecisionAgente(**json.loads(respuesta.text))
    except Exception as e:
        print(f"  ❌ Error de procesamiento en la API de Google: {e}")
        return None

# ══════════════════════════════════════════════════════════════════════
# 4. ENTORNO INTERACTIVO DE EXPOSICIÓN (MESA JURADO)
# ══════════════════════════════════════════════════════════════════════
def main():
    sensor_actual = "SEC-B-04"
    historial_simulado = [
        {"hora": "01:00", "flujo": 4, "presion": 45},
        {"hora": "02:00", "flujo": 4, "presion": 41},
        {"hora": "03:00", "flujo": 5, "presion": 38}
    ]

    while True:
        print("\n" + "═"*60)
        print("💧 AQUAALERT IoT — PANEL DE CONTROL INTERACTIVO (DEMO)")
        print("═"*60)
        print("1. Inyectar: OPERACIÓN NORMAL (Fábrica Activa)")
        print("2. Inyectar: TENDENCIA ANÓMALA (Modo Predictivo / Micro-fuga)")
        print("3. Inyectar: RUPTURA DE TUBERÍA (Modo Reactivo / Emergencia)")
        print("4. Salir del Sistema")
        print("─"*60)
        
        opcion = input("Selecciona un escenario para enviar al Agente (1-4): ")
        
        if opcion == "4":
            print("Cerrando panel de demostración AquaAlert...")
            break
            
        if opcion == "1":
            nombre_escenario = "Operacion Normal"
            prompt = construir_prompt(sensor_actual, 10, 85, 55, True, [{"hora":"09:00","flujo":82,"presion":54}])
        elif opcion == "2":
            nombre_escenario = "Micro-fuga Predictiva"
            prompt = construir_prompt(sensor_actual, 4, 5, 34, False, historial_simulado)
        elif opcion == "3":
            nombre_escenario = "Ruptura Catastrofica"
            prompt = construir_prompt(sensor_actual, 23, 92, 11, False, historial_simulado)
        else:
            print("⚠️ Entrada no válida. Elige un escenario del 1 al 4.")
            continue

        print("🧠 Consultando al Agente de IA Gemini...")
        decision = consultar_agente(prompt)
        
        if decision:
            print("\n" + "─"*40)
            print(f"📊 ANÁLISIS SENSOR EN TIEMPO REAL: {sensor_actual}")
            print("─"*40)
            print(f"🧠 Contexto    : {decision.analisis_contexto}")
            print(f"🔮 Diagnóstico : {decision.probabilidad_fuga_porcentaje}% riesgo | Fallo estimado en {decision.tiempo_estimado_falla_horas} horas")
            print(f"⚙️  Comando IoT : {decision.accion_automatica_iot}")
            print(f"💸 Pérdida Est.: {decision.costo_estimado_bolivianos:.2f} BOB")
            print("─"*40)
            
            # Guardado automático en el historial de refinamiento
            guardar_en_registro_piloto(sensor_actual, nombre_escenario, decision)
            
            if decision.es_alerta_preventiva or decision.es_una_emergencia:
                tipo = "EMERGENCIA" if decision.es_una_emergencia else "PREVENTIVA"
                print(f"📱 Enviando alerta {tipo} vía canal de mensajería...")
                enviar_whatsapp(decision.notificacion_generada, tipo)
            else:
                print("✅ Estado estable. Las compuertas e integridad del sistema operan con normalidad.")
        
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()