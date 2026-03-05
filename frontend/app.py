import streamlit as st
import requests
import os
import time

# Configuramos la página
st.set_page_config(page_title="Traductor Text-to-SQL", page_icon="🤖")

st.title("🤖 Traductor de Lenguaje Natural a SQL")
st.markdown(
    "Escribe tu pregunta y el contexto de la base de datos para generar la consulta SQL."
)

# Cajas de texto en español
pregunta = st.text_input(
    "Pregunta:", placeholder="Ej: ¿Quién es el empleado con mayor salario?"
)
contexto = st.text_area(
    "Contexto (Esquema de la base de datos):",
    placeholder="Ej: CREATE TABLE empleados (nombre VARCHAR, salario INT)",
)


# Funciones helper
def verify_backend_health(base_url):
    """Verifica si el modelo ya terminó de cargar en el backend"""
    try:
        res = requests.get(f"{base_url}/health", timeout=5)
        if res.status_code == 200:
            return True, "Listo"
        elif res.status_code == 503:
            return False, "Descargando modelo (HuggingFace)..."
        return False, f"Estado desconocido: {res.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Conectando al contenedor Backend..."
    except Exception as e:
        return False, f"Error de red: {str(e)}"


# Setup
url_base = os.getenv("BACKEND_URL", "http://backend:8000")

# Botón en español
if st.button("Generar SQL"):
    if pregunta and contexto:
        # 1. Fase de Healthcheck Polling
        is_ready, status_msg = verify_backend_health(url_base)

        if not is_ready:
            st.warning(
                "⏳ El Backend todavía se está iniciando. Por favor, espera mientras se descargan y cargan los pesos del modelo de IA (3GB) en memoria."
            )
            progress_text = st.empty()

            with st.spinner(
                "Esperando a que la Inteligencia Artificial esté lista... (no cierres esta ventana)"
            ):
                # Polling loop
                max_retries = 60  # 60 * 5s = 5 minutos de espera máxima
                for _ in range(max_retries):
                    is_ready, status_msg = verify_backend_health(url_base)
                    progress_text.text(f"Estado actual: {status_msg}")

                    if is_ready:
                        progress_text.empty()
                        break
                    time.sleep(5)

                if not is_ready:
                    st.error(
                        "🚨 Timeout: El backend tardó demasiado en iniciar. Revisa los logs de Docker."
                    )
                    st.stop()

        # 2. Fase de Inferencia
        with st.spinner(
            "🤖 Escribiendo consulta SQL... (Esto puede tardar unos segundos en CPU)"
        ):
            try:
                url_predict = f"{url_base}/predict"
                payload = {"pregunta": pregunta, "contexto": contexto}

                respuesta = requests.post(url_predict, json=payload, timeout=300)
                respuesta.raise_for_status()

                datos = respuesta.json()
                st.success("¡SQL Generado con éxito!")
                st.code(datos.get("sql", "No se recibió SQL"), language="sql")

            except requests.exceptions.ConnectionError:
                st.error("🚨 Error: No se pudo contectar al endpoint de predicción.")
            except Exception as e:
                st.error(f"🚨 Ocurrió un error en la inferencia: {e}")
    else:
        st.warning("⚠️ Por favor, rellena tanto la pregunta como el contexto.")
