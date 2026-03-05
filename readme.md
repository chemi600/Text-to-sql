# Traductor Natural Language a SQL (AI)

Esta aplicación utiliza Inteligencia Artificial (un modelo base Qwen de 1.5 Billones de parámetros ajustado mediante LoRA) para traducir preguntas en lenguaje natural a consultas SQL, basándose en un esquma de base de datos dado.

## 🏗 Arquitectura

El proyecto está dockerizado y desacoplado en dos microservicios:
1. **Frontend (`frontend/`)**: Interfaz gráfica de usuario interactiva construida con **Streamlit**. Accesible en el puerto `8501`.
2. **Backend (`backend/`)**: API REST de alto rendimiento construida con **FastAPI**. Aloja el motor de inferencia pesado de PyTorch/HuggingFace de forma asíncrona. Accesible en el puerto `8000`.

## 🚀 Requisitos Previos
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y en ejecución en tu ordenador. No es necesario instalar Python ni librerías localmente.

## 🛠 Instalación y Ejecución Rápida (Cualquier Ordenador)

1. Navega hasta la carpeta raíz del proyecto en tu terminal (donde se encuentra el archivo `docker-compose.yml`).
2. Ejecuta el siguiente comando para construir y levantar toda la arquitectura:

   ```bash
   docker-compose up --build -d
   ```

3. **¡Importante! La primera vez que ejecutes esto:** El backend tiene que descargar el "Cerebro Base" de la IA (`Qwen/Qwen2.5-Coder-1.5B`) desde los servidores de HuggingFace (Aprox. 3 GB de peso). Todo es automático, pero dependiendo de tu velocidad de internet, tardará algunos minutos. El Frontend te avisará amigablemente cuando esté listo.

4. Accede a las aplicaciones desde tu navegador web:
   - **Aplicación Web (Streamlit):** [http://localhost:8501](http://localhost:8501)
   - **Documentación de la API (FastAPI Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

## 💡 Ejemplos de Prueba
Una vez que el Frontend esté listo en `http://localhost:8501`, puedes copiar y pegar estos ejemplos para interactuar con la IA:

**Prueba Fácil:**
- **Pregunta:** Dame los nombres de todos los empleados
- **Contexto:** `CREATE TABLE empleados (id INT, nombre VARCHAR, departamento VARCHAR);`

**Prueba Intermedia (Agrupación):**
- **Pregunta:** ¿Cuántas ventas tiene cada tienda ordenado de mayor a menor?
- **Contexto:** `CREATE TABLE ventas (id INT, tienda_id INT, monto DECIMAL); CREATE TABLE tiendas (id INT, nombre VARCHAR);`

Para detener los contenedores cuando termines de trabajar:
```bash
docker-compose down
```

## 💾 Caché Persistente de Modelos
Para ahorrarte el hecho de descargar 3 Gigabytes cada vez que enciendes el proyecto, Docker ha sido configurado para mapear de forma transparente la carpeta de descargas de la IA a la ruta física `./backend/huggingface_cache/` en tu ordenador. 
El primer inicio tardará, pero los siguientes reinicios leerán el modelo directamente de tu disco duro y el sistema se levantará en apenas ~5 segundos.

## 💻 Compatibilidad Inteligente de Hardware (Mac vs Windows)
Este software contiene salvaguardas explícitas de bajo nivel para detectar automáticamente tu hardware y evitar bloqueos (OOM / Out Of Memory Errors). Funciona tanto en entornos de desarrollo Mac de gama alta como en entornos de producción Windows modestos:

- **Mac (Apple Silicon ARM64 - ej. M1/M4):** FastAPI detecta el chip nativo y utiliza la aceleración por hardware de Apple (`mps`) procesando los tensores en alta precisión matemática (`float16`).
- **Windows / Linux (Intel i5/AMD x86_64 sin GPU compatible):** FastAPI detecta la ausencia de tarjetas NVIDIA/Apple y aplica un Fallback forzoso al procesador primario (`cpu`). Crucialmente, comprime los cálculos matemáticos del modelo a la mitad (`bfloat16`) para reducir el consumo total de Memoria RAM de ~6GB a solo ~3GB.
   - *Nota de Rendimiento:* Al ejecutar en una CPU Intel pura sin GPU, la inferencia (el tiempo que tarda la IA en escribir el código SQL) tomará de 10 a 30 segundos, pero el proceso es completamente estable y funcional.
