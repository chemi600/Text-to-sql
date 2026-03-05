# 🧠 Entrenamiento AI: Text-to-SQL (Fine-Tuning)

Esta carpeta contiene los notebooks intermedios (`.ipynb`) utilizados para entrenar el modelo de Inteligencia Artificial que potencia el backend de nuestra aplicación. 

A diferencia del archivo de código limpio que ejecuta la inferencia real de FastAPI (`backend/app/main.py`), estos notebooks de Google Colab documentan todo el flujo de Ingeniería de Datos (Data Engineering) e Inteligencia Artificial que dio lugar al modelo.

## 📊 1. El Dataset y la Preparación
El modelo necesitaba aprender un nuevo "idioma", es decir, la relación exacta entre instrucciones en Español natural y su correspondiente sintaxis de Bases de Datos relacional, conociendo de antemano el esquema de la tabla de SQL en el contexto.

1. **Recolección de Datos:** Se obtuvieron miles de pares de pares de *Instrucción-Contexto-Salida* basados en bases de datos abiertas (como el corpus de HuggingFace `b-mc2/sql-create-context` traduccido al español, o una curación propia).
2. **Formateo:** La IA no entiende tablas de Excel, por lo que convertimos todos esos miles de pares a un formato de texto único, parecido a un Prompt, por el que pudiera iterar.
   Ejemplo de formateo de datos de entrenamiento:
   ```text
   Pregunta: Dime quién gana más
   Contexto: CREATE TABLE empleados (nombre, salario)
   SQL: SELECT nombre FROM empleados ORDER BY salario DESC LIMIT 1
   ```

## ⚙️ 2. El Proceso de Fine-Tuning (Colab)

Decidimos utilizar como base el modelo **`Qwen/Qwen2.5-Coder-1.5B`**, un prodigio Open Source de 1.5 billones de parámetros que ya es experto general en programación. Sin embargo, no podíamos re-entrenar de cero sus millones de conexiones porque requeriría supercomputadoras.

Implementamos el método **LoRA (Low-Rank Adaptation)** a través de la librería `peft`, lo que nos permitió inyectar el nuevo conocimiento especializado (Nuestra sintaxis Text-to-SQL en español) afectando a menos del 1% del cerebro total del modelo.

**Pasos Destacados en Colab:**
- **Descendiente y Tokenizador:** Descargamos los pesos originales de 3GB.
- **Configuración Cuantizada:** Usamos `bitsandbytes` para bajar la precisión a 4-bits durante el entrenamiento, garantizando que todo cabría en la limitada VRAM (15GB) de la GPU T4 gratuita de Google Colab.
- **Micro-Entrenamiento:** Usamos la librería `TRL` (Supervised Fine-tuning Trainer) sobre cientos de iteraciones para que el modelo aprendiera el patrón perfecto entre Lenguaje -> Contexto -> SQL.

## 💾 3. Guardado Inteligente (Artifacts)
El resultado final del entrenamiento (Notebook: `natural_language_to_sql.ipynb`) no produjo un nuevo modelo pesado de 3GB. Gracias al paradigma LoRA, el output (`modelo_qwen_sql_final`) resultó ser tan solo una pequeña capa adaptadora de poquísimos Megabytes. 

Ese adaptador se subió a Google Drive, desde donde pudimos descargarlo a nuestra computadora y empaquetarlo limpiamente dentro del contenedor Docker (`backend/app/modelo...`). Cuando el backend se enciende, carga el modelo genérico de 3GB de internet y luego *le pone encima nuestra máscara de entrenamiento local*, obteniendo como resultado un Experto en Text-to-SQL liviano y portable.
