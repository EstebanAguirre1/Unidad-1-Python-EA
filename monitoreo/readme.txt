# Sistema de Monitoreo Energético - EcoEnergy

Sistema Django para monitoreo de consumo energético de dispositivos.

## 🚀 Características

- Catálogo de productos y categorías
- Reglas de alerta personalizables  
- Monitoreo en tiempo real
- Panel de administración Django
- Base de datos MySQL

## 📋 Requisitos

- Python 3.8+
- MySQL Server
- WAMP Server (recomendado)
- Django 5.2

## 🗄️ Base de Datos

**Motor:** MySQL  
**Base de datos:** `ecoenergy`  
**Usuario:** `esteban`  
**Contraseña:** `esteban`  
**Host:** `localhost:3306`

### Configuración BD en .env:
```bash
# .env
DB_ENGINE=mysql
DB_NAME=ecoenergy
DB_USER=esteban
DB_PASSWORD=esteban
DB_HOST=localhost
DB_PORT=3306


Instalación
Clonar repositorio:


git clone [tu-repo-url]
cd Unidad-1-Python-EA

Cambiar de rama:
git checkout -b nombre-de-rama origin/nombre-de-rama

Ver ramas remotas disponibles:
git branch -r

Crear entorno virtual:


python -m venv venv
venv\Scripts\activate  # Windows
Instalar dependencias:

pip install -r requirements.txt
Configurar base de datos:

Asegurar que WAMP/MySQL esté funcionando

La BD ecoenergy se crea automáticamente

Aplicar migraciones:


python manage.py migrate
🌱 Cargar Datos de Prueba
Opción 1: Comando personalizado (Recomendado)

python manage.py seed_catalog_es
Carga catálogo completo en español: categorías, productos, reglas de alerta y organización demo.

Opción 2: Fixtures (alternativa)

python manage.py loaddata catalog_data.json
👤 Acceso al Administrador
URL: http://127.0.0.1:8000/admin
Usuario: admin
Contraseña: admin123

Nota: Crear superusuario si no existe:


python manage.py createsuperuser
🏃 Ejecutar el Proyecto
Iniciar WAMP Server (ícono verde)

Ejecutar servidor Django:


python manage.py runserver
Abrir en navegador: http://127.0.0.1:8000

📊 Estructura del Proyecto

monitoreo/
├── dispositivos/          # App principal
│   ├── models.py         # Modelos: Product, Category, Device, etc.
│   ├── admin.py          # Configuración panel administración
│   └── management/       # Comandos personalizados
│       └── commands/
│           └── seed_catalog_es.py
├── monitoreo/            # Configuración proyecto
│   └── settings.py       # Configuración BD y apps
└── db.sqlite3           # BD SQLite (backup)
🔧 Comandos Útiles

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ejecutar tests
python manage.py test

# Shell interactivo
python manage.py shell
📞 Soporte
Para problemas técnicos, contactar al desarrollador o revisar la documentación de Django.


## **📁 Guardar el archivo**

Guárdalo como `README.md` en la raíz de tu proyecto:
Unidad-1-Python-EA/
├── README.md # ← Este archivo
├── manage.py
├── monitoreo/
└── dispositivos/


## **🚀 Para evidenciar en el PDF:**

**Captura:**
1. **Archivo README.md** abierto en tu editor
2. **Contenido completo** mostrando las secciones importantes
3. **Commiteado en Git** (opcional)

**Texto para PDF:**
Evidencia 5: README.md en repositorio

Documentación completa incluye:

Configuración de MySQL con credenciales

Instrucciones de instalación paso a paso

Comando para cargar semillas (seed_catalog_es.py)

Credenciales de acceso al administrador

Estructura del proyecto y comandos útiles



