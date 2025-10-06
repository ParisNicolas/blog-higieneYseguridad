# Blog de Higiene y Seguridad - Sistema de Reportes

## 📋 Descripción del Proyecto

Sistema web desarrollado en Flask para la gestión y reporte de incidencias relacionadas con higiene y seguridad en instituciones educativas. La aplicación permite a usuarios reportar riesgos mediante fotografías y descripciones, mientras que los administradores pueden clasificar, priorizar y gestionar la resolución de estos reportes.

### 🎯 Características Principales

- **Reportes Visuales**: Los usuarios pueden subir fotografías de incidencias junto con descripciones detalladas
- **Clasificación Automática de Riesgos**: Sistema inteligente que clasifica automáticamente el nivel de riesgo (0-5) basado en palabras clave y tipo de riesgo
- **10 Categorías de Riesgo**: Eléctrico, Mecánico, Químico, Incendio, Biológico, Ergonómico, Psicosocial, Infraestructura, Señalización, Ambiental
- **Sistema de Likes y Comentarios**: Interacción social para priorizar reportes importantes
- **Panel de Administración**: Herramientas para gestionar reportes, modificar clasificaciones y marcar como resueltos
- **Filtros Avanzados**: Filtrado por tipo de riesgo y estado de resolución
- **Arquitectura Escalable**: Preparado para producción con AWS S3 y EC2

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.13+**
- **Flask 3.0.0** - Framework web
- **Flask-SQLAlchemy 3.0.5** - ORM para base de datos
- **Flask-Migrate 4.0.5** - Migraciones de base de datos
- **PyMySQL 1.1.1** - Conector MySQL
- **Werkzeug 3.0.0** - Utilidades WSGI y seguridad
- **python-dotenv 1.0.1** - Gestión de variables de entorno

### Frontend
- **Bootstrap 5.3.0** - Framework CSS
- **Bootstrap Icons 1.10.5** - Iconografía
- **JavaScript (Vanilla)** - Interactividad cliente
- **HTML5 + Jinja2** - Templates dinámicos

### Base de Datos
- **MySQL/MariaDB** - Base de datos principal
- **SQLAlchemy ORM** - Mapeo objeto-relacional

### Cloud & Deployment
- **AWS S3** - Almacenamiento de imágenes (producción)
- **AWS EC2** - Servidor de aplicación (producción)
- **boto3 1.40.16** - SDK de AWS

## 🗄️ Estructura de la Base de Datos

### Tablas Principales

```sql
-- Usuarios del sistema
User(
    id: INTEGER PRIMARY KEY,
    username: VARCHAR(50) UNIQUE,
    password_hash: VARCHAR(200),
    is_admin: BOOLEAN DEFAULT FALSE
)

-- Publicaciones/Reportes
Post(
    id: INTEGER PRIMARY KEY,
    title: VARCHAR(200),           -- Descripción breve del reporte
    image_path: VARCHAR(300),      -- Ruta de la imagen
    created_at: DATETIME,          -- Fecha de creación
    username: VARCHAR(50),         -- Autor del reporte
    descripcion: TEXT,             -- Tipo de riesgo clasificado
    score: INTEGER DEFAULT 2,      -- Nivel de riesgo (0-5)
    solucionado: BOOLEAN DEFAULT FALSE -- Estado de resolución
)

-- Sistema de likes
Like(
    id: INTEGER PRIMARY KEY,
    post_id: INTEGER FOREIGN KEY,
    username: VARCHAR(50)
)

-- Sistema de comentarios  
Comment(
    id: INTEGER PRIMARY KEY,
    post_id: INTEGER FOREIGN KEY,
    username: VARCHAR(50),
    text: VARCHAR(300)
)
```

## 🚀 Instalación y Configuración

### Prerequisitos
- Python 3.13+
- MySQL/MariaDB
- XAMPP (para desarrollo local)

### Instalación Local

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd blog-higieneYseguridad
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
Crear archivo `.env` en el directorio raíz:
```env
# Base de datos
SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:@localhost:3306/hygiene_safety_db

# Seguridad
SECRET_KEY=tu_clave_secreta_muy_segura

# Almacenamiento local
UPLOAD_FOLDER=static/uploads

# AWS (solo para producción)
S3_BUCKET=tu-bucket-s3
S3_REGION=us-east-1
S3_ACCESS_KEY=tu-access-key
S3_SECRET_KEY=tu-secret-key

# Entorno
FLASK_ENV=development
```

5. **Configurar base de datos**
```bash
# Inicializar migraciones
flask db init

# Crear tablas
flask db migrate -m "Initial migration"
flask db upgrade
```

6. **Crear usuario administrador**
```bash
flask create-admin
```

7. **Ejecutar aplicación**
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## 🌟 Sistema de Clasificación de Riesgos

### Algoritmo de Puntuación Automática

El sistema implementa un algoritmo inteligente que asigna automáticamente un nivel de riesgo (0-5) basado en:

1. **Peso Base por Categoría**:
   - Químico/Incendio: 5 puntos base (Alto riesgo)
   - Eléctrico: 4 puntos base
   - Mecánico/Infraestructura/Biológico: 3 puntos base
   - Ergonómico/Psicosocial/Señalización: 2 puntos base
   - Ambiental: 1 punto base (Bajo riesgo)

2. **Palabras Clave Contextuales**:
   - Cada categoría tiene palabras clave específicas con puntajes adicionales
   - Ejemplo: "electrocución" (+2), "derrame" (+2), "colapso" (+2)

3. **Normalización Final**:
   - El puntaje se normaliza entre 0-5
   - 0-1: Riesgo Bajo (Verde)
   - 2-3: Riesgo Medio (Amarillo) 
   - 4-5: Riesgo Alto (Rojo)

### Categorías de Riesgo Implementadas

| Categoría | Peso Base | Ejemplos de Palabras Clave |
|-----------|-----------|----------------------------|
| **Químico** | 5 | ácido, tóxico, derrame, corrosivo |
| **Incendio** | 5 | fuego, inflamable, extintor, quemadura |
| **Eléctrico** | 4 | cable, electrocución, cortocircuito |
| **Mecánico** | 3 | herramienta, máquina, corte, accidente |
| **Infraestructura** | 3 | techo, grieta, desprendimiento, colapso |
| **Biológico** | 3 | moho, bacteria, virus, plaga |
| **Ergonómico** | 2 | postura, peso, esfuerzo, dolor |
| **Psicosocial** | 2 | acoso, estrés, violencia, discriminación |
| **Señalización** | 2 | salida, emergencia, evacuación |
| **Ambiental** | 1 | ruido, temperatura, iluminación |

## 👥 Roles de Usuario

### Usuario Regular
- Crear reportes con fotografías y descripciones
- Dar "like" a reportes importantes
- Comentar en reportes
- Ver historial de sus propios reportes
- Eliminar sus propios reportes y comentarios

### Administrador
- Todas las funciones de usuario regular
- Modificar clasificación de riesgo de cualquier reporte
- Marcar reportes como "Solucionados"
- Eliminar cualquier reporte o comentario
- Filtrar reportes por estado (resueltos/pendientes)
- Acceso a estadísticas y métricas del sistema

## 🔧 Funcionalidades Técnicas

### Gestión de Archivos
- **Desarrollo**: Almacenamiento local en `static/uploads/`
- **Producción**: Integración con AWS S3 para escalabilidad
- Generación de nombres únicos con UUID
- Validación de tipos de archivo
- Limitación de tamaño (32MB máximo)

### Seguridad
- Autenticación basada en sesiones Flask
- Hash de contraseñas con Werkzeug
- Validación CSRF en formularios
- Autorización basada en roles
- Sanitización de entradas de usuario

### Base de Datos
- Migraciones automáticas con Flask-Migrate
- Conexiones pooling con SQLAlchemy
- Logging de operaciones críticas
- Respaldos automáticos (configurables)

## 🚀 Despliegue en Producción (AWS EC2)

### Arquitectura de Producción

```
[Internet] → [Application Load Balancer] → [EC2 Instance]
                                              ├── Nginx (Proxy Reverso)
                                              ├── Gunicorn (WSGI Server)  
                                              ├── Flask App
                                              ├── MySQL (Local)
                                              └── [AWS S3] (Imágenes)
```

### Configuración AWS EC2

1. **Instancia EC2**
   - **Tipo**: t3.small o superior
   - **OS**: Ubuntu 22.04 LTS
   - **Storage**: 2GB SSD mínimo
   - **Security Groups**: 
     - Puerto 22 (SSH)
     - Puerto 80 (HTTP)
     - Puerto 443 (HTTPS)
     - Puerto 3306 (MySQL - solo internal)

2. **Instalación en EC2**
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install python3-pip python3-venv nginx mysql-server git -y

# Clonar proyecto
git clone <repository-url> /var/www/blog-hygiene
cd /var/www/blog-hygiene

# Configurar entorno
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Configurar MySQL
sudo mysql_secure_installation
sudo mysql -u root -p
CREATE DATABASE hygiene_safety_db;
GRANT ALL PRIVILEGES ON hygiene_safety_db.* TO 'appuser'@'localhost' IDENTIFIED BY 'secure_password';
FLUSH PRIVILEGES;
EXIT;

# Variables de entorno producción
cp .env.example .env
# Editar .env con configuraciones de producción
```

3. **Configuración Nginx**
```nginx
# /etc/nginx/sites-available/blog-hygiene
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /var/www/blog-hygiene/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

4. **Servicio Systemd**
```ini
# /etc/systemd/system/blog-hygiene.service
[Unit]
Description=Blog Hygiene Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/blog-hygiene
Environment="PATH=/var/www/blog-hygiene/venv/bin"
ExecStart=/var/www/blog-hygiene/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Activar servicios**
```bash
sudo ln -s /etc/nginx/sites-available/blog-hygiene /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable blog-hygiene
sudo systemctl start blog-hygiene
```

### Configuración AWS S3

1. **Crear bucket S3**
2. **Configurar políticas IAM**
3. **Actualizar variables de entorno**
```env
FLASK_ENV=production
S3_BUCKET=mi-bucket-hygiene-prod
S3_REGION=us-east-1
S3_ACCESS_KEY=AKIAXXXXXXXXXXXXX
S3_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
```

## 📊 Monitoreo y Logs

### Sistema de Logging
- Logs de aplicación: `app.log`
- Logs de errores críticos
- Registro de accesos de usuarios
- Métricas de performance

### Monitoreo Recomendado
- **CloudWatch** (AWS)
- **Uptime monitoring**
- **Database performance metrics**
- **Storage usage tracking**

## 🔐 Variables de Entorno

```env
# Aplicación
FLASK_ENV=development|production
SECRET_KEY=clave-secreta-muy-segura

# Base de Datos
SQLALCHEMY_DATABASE_URI=mysql+pymysql://user:pass@host:port/db_name

# Almacenamiento
UPLOAD_FOLDER=static/uploads

# AWS (Producción)
S3_BUCKET=nombre-bucket
S3_REGION=us-east-1  
S3_ACCESS_KEY=access-key
S3_SECRET_KEY=secret-key
```

## 📝 Comandos Útiles

```bash
# Crear administrador
flask create-admin

# Cambiar contraseña de admin
flask change-admin-password

# Migraciones
flask db migrate -m "Descripción del cambio"
flask db upgrade

# Ejecutar en desarrollo
python app.py

# Ejecutar en producción
gunicorn --workers 3 --bind 0.0.0.0:8000 app:app
```

## 🤝 Contribución

1. Fork del proyecto
2. Crear branch de feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit de cambios (`git commit -am 'Agregar nueva característica'`)
4. Push al branch (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍🎓 Equipo de trabajo

- **Desarrollador**: Paris Nicolas 🗼
- **Testers**: Michel Paul y Ariza Marcos 🦖
- **Base de Datos**: Tomas Cipriano ✈️


## 🔄 Versiones

- **v1.0** - Sistema básico de reportes
- **v1.1** - Clasificación automática de riesgos
- **v1.2** - Sistema de likes y comentarios
- **v1.3** - Panel de administración avanzado
- **v2.0** - Integración AWS y escalabilidad (Actual)

---

**Desarrollado con ❤️ para mejorar la seguridad en instituciones educativas**
