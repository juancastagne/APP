# Stream Views - Monitor de Métricas de YouTube

Aplicación para monitorear métricas de streams de YouTube en tiempo real.

## Estructura del Proyecto

```
stream-views/
├── app/
│   ├── api/                 # Clientes de API externas
│   │   └── youtube.py
│   ├── core/               # Componentes centrales
│   │   ├── config.py
│   │   └── logger.py
│   ├── models/             # Modelos de datos
│   │   └── stream.py
│   ├── repositories/       # Acceso a datos
│   │   └── stream_repository.py
│   ├── services/          # Lógica de negocio
│   │   └── stream_service.py
│   └── ui/                # Componentes de interfaz
│       ├── components/
│       └── pages/
├── tests/                 # Pruebas unitarias y de integración
├── .env.example          # Ejemplo de variables de entorno
├── docker-compose.yml    # Configuración de Docker
├── Dockerfile           # Configuración de la imagen Docker
├── requirements.txt     # Dependencias del proyecto
└── main.py             # Punto de entrada de la aplicación
```

## Requisitos

- Python 3.8+
- Docker y Docker Compose
- Cuenta de Google Cloud con API de YouTube habilitada

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Copiar `.env.example` a `.env` y configurar las variables de entorno
5. Ejecutar la aplicación:
   ```bash
   python main.py
   ```

## Despliegue con Docker

```bash
docker-compose up -d
```

## Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request 