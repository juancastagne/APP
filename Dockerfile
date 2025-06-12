# Usamos una imagen base de Python
FROM python:3.11-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos los archivos de requisitos primero
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente
COPY . .

# Agregamos el directorio actual al PYTHONPATH
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8080

# Exponemos el puerto que usará la aplicación
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD ["python", "src/main.py"] 