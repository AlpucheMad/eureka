# Eureka

Eureka es una plataforma web donde los usuarios pueden gestionar sus colecciones de escritura a lo largo del tiempo. Permite a los usuarios crear colecciones (por ejemplo, "Poesía"), agregar entradas con títulos, fechas, horas y contenido, y gestionar sus entradas guardando borradores, marcándolas como favoritas o eliminándolas. Las entradas pueden ser privadas o públicas, y los usuarios pueden agregar amigos por nombre de usuario para ver sus entradas públicas.

## Características principales

- **Autenticación de usuarios**: Funcionalidad de inicio de sesión, registro y cierre de sesión.
- **Colecciones**: Los usuarios pueden crear colecciones para organizar sus entradas.
- **Entradas**: Los usuarios pueden crear entradas con título, fecha y hora, asociación a colecciones, contenido, estado y visibilidad.
- **Características sociales**: Agregar amigos por nombre de usuario y ver entradas públicas de amigos.
- **Seguimiento de actividad**: Ver la actividad de escritura a lo largo del tiempo.

## Tecnologías utilizadas

- **Backend**: Python 3.12, Django 4.2
- **Frontend**: React, Tailwind CSS
- **Base de datos**: SQLite (para desarrollo inicial)
- **Entorno**: Virtualenv para gestión del entorno Python

## Configuración del proyecto

### Requisitos previos

- Python 3.12
- Virtualenv

### Instalación

1. Clonar el repositorio:
   ```
   git clone <url-del-repositorio>
   cd eureka
   ```

2. Crear y activar el entorno virtual:
   ```
   python -m virtualenv venv
   # En Windows
   .\venv\Scripts\activate
   # En Unix o MacOS
   source venv/bin/activate
   ```

3. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Aplicar migraciones:
   ```
   python manage.py migrate
   ```

5. Iniciar el servidor de desarrollo:
   ```
   python manage.py runserver
   ```

6. Acceder a la aplicación en el navegador:
   ```
   http://localhost:8000/
   ```

## Estructura del proyecto

```
eureka/
  ├── eureka/              # Configuración del proyecto Django
  ├── core/                # Aplicación principal para autenticación y funciones principales
  ├── static/              # Archivos estáticos (CSS, JS, imágenes)
  ├── media/               # Archivos subidos por los usuarios
  ├── templates/           # Plantillas HTML
  ├── manage.py            # Script de gestión de Django
  ├── requirements.txt     # Dependencias del proyecto
  └── .gitignore           # Archivos y directorios ignorados por Git
```

## Paleta de colores

- Naranja: #f9b234
- Gris oscuro: #1d1d1b