# 💧 AquaAlert IoT — Sistema Autónomo de Monitoreo Hídrico Predictivo

Sistema inteligente desarrollado en el marco de la hackatón **Build with AI 2026 (GDG Santa Cruz)** para la detección, predicción y mitigación autónoma de fugas de agua en redes industriales y comerciales de Santa Cruz de la Sierra, Bolivia.

---

## 👥 Equipo de Desarrollo (Syntax Labs)
* **Kevin Brayton Zapata Rojas** — Desarrollo e Integración IoT
* **Alan Navarro Limachi** — Negocio, Pitch y Validación
* **Orlando Medina Rodriguez** — Agente IA y Backend

---

## 📂 Recursos y Documentación Oficial
Para facilitar la evaluación del jurado, se han adjuntado las versiones ejecutivas del proyecto directamente en la raíz de este repositorio:

* 📄 **[Descargar Documentación Completa (Word)](./Documental-Hackaton1.docx)**: Manual técnico extendido, arquitectura de capas, matriz FODA, Lean Canvas y proyecciones financieras.
* 📊 **[Descargar Presentación del Pitch (PowerPoint)](./AquaAlert-PitchDeck.pptx)**: Soporte visual y diapositivas comerciales diseñadas para el video de presentación de 2 minutos.

---

## 🛠️ Arquitectura y Componentes del Repositorio
* `main.py`: Código del Agente IA en Python que consume telemetría en tiempo real y ejecuta diagnósticos predictivos mediante **Gemini 2.5 Flash**.
* `index.html`: Dashboard web interactivo con interfaz cyber-industrial para el monitoreo visual del operador de planta.
* `.env`: Archivo de configuración protegido para variables de entorno (Gemini API y Twilio Business API para alertas de WhatsApp).
* `requirements.txt`: Dependencias del entorno de ejecución de Python.

---

## 🎯 Propuesta de Valor Central
> *"Predecimos la fuga antes de que ocurra. No somos una alarma de incendios... somos el detector de humo."* 
* **Anticipación predictiva:** 4 a 6 horas antes de la ruptura física mediante análisis de microgotas progresivas y flujos anómalos nocturnos.
* **Costo Hardware:** Prototipo altamente accesible (\$17-\$34 USD) basado en sensores YF-S201 y microcontroladores ESP32.
* **Impacto:** Reducción de hasta un 30% en las facturas de agua y energía de bombeo para el sector de las PyMEs industriales cruceñas.
