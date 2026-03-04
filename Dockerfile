# Imagen base nginx
FROM nginx:latest

# Instalar Python y pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio para la app
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiar código backend
COPY main.py .

# Copiar frontend a nginx
COPY contents/ /usr/share/nginx/html/

# Exponer puertos
EXPOSE 8000
EXPOSE 8001

# Copiar configuración personalizada de nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Comando para arrancar ambos servicios
CMD service nginx start && uvicorn main:app --host 0.0.0.0 --port 8001