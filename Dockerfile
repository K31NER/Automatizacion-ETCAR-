# Definimos la imagen
FROM python:3.11-slim

# El directorio de trabajo
WORKDIR /app

# Copiamos las dependencias
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del proyecto
COPY . .

# Exponemso el puerto que usar uvicorn
EXPOSE 8000

# Ejecutamos el comando de arranque
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]