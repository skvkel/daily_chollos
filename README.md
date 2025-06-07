# Daily Chollos - Plataforma para recolección de ofertas
[demo.webm](https://github.com/user-attachments/assets/aff965a4-a92e-4c06-a6a4-6b1278051acd)

---

## 🌟 Características del Proyecto

- **Arquitectura Limpia:** Alto desacoplamiento entre las capas, facilitando cambios o mejoras.
- **Inyección de dependencias:** utilización de la librería _dependency_injector_ para inversión de dependencias
- **Interfaz con FastAPI:** Adaptadores definidos para RESTful API.
- **ORM Modular:** Tortoise.
- **Scraping:** lanzamiento de scraper programados mediante asincronía. 
- **Búsqueda Avanzada:** Filtros por características.

---

## 📦 Construido con  

El proyecto ha sido desarrollado con **Python 3.12** y utiliza las siguientes tecnologías:  

- [FastAPI](https://fastapi.tiangolo.com/)
- [Tortoise ORM](https://tortoise-orm.readthedocs.io/)
- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)
- Herramientas de desarrollo: **ruff**, **Pre-commit**, **Aerich**, **dependency_injector** entre otras.

---

## 🚀 Getting Started

### Prerrequisitos

- Docker Desktop o Rancher Desktop.
- PostgreSQL o cualquier base de datos relacional.
- Redis para almacenamiento en caché 

### Instalación  

1. **Clonar el repositorio:**  
   ```bash
   git clone https://github.com/skvkel/clean_architecture_template
2. **Crear un entorno virtual y activar**
   ```bash
   python -m venv venv &&
   source venv/bin/activate &&
   pip install -r requirements.txt
3. **Instalar dependencias y pre-commit**
   ```bash
   pip install pre-commit ruff mypy &&
   pre-commit install --hook-type commit-msg
4. **Crear fichero .env y definir las variables necesarias**
````
# General
ENV=local
PRIVATE_SPORT_SHOP_URL=

# COOKIE SELECTOR
PRIVATE_SPORT_SHOP_COOKIE_SELECTOR=
PRIVATE_SPORT_SHOP_BUTTON_ACCEPT_COOKIE_SELECTOR=

# LOGIN SELECTORS
PRIVATE_SPORT_SHOP_BUTTON_DEPLOY_LOGIN_SELECTOR=
PRIVATE_SPORT_SHOP_LOGIN_USER_BOX_SELECTOR=
PRIVATE_SPORT_SHOP_LOGIN_PASSWORD_BOX_SELECTOR=
PRIVATE_SPORT_SHOP_BUTTON_LOGIN_SELECTOR=

# ITEMS HOMEPAGE SELECTOR
PRIVATE_SPORT_SHOP_ITEMS_HOMEPAGE_SELECTOR=

# CARD ITEMS SELECTORS
PRIVATE_SPORT_SHOP_PRODUCT_LIST=
PRIVATE_SPORT_SHOP_ITEMS_SELECTOR=

# ITEM AMOUNT SELECTOR
PRIVATE_SPORT_SHOP_AMOUNT_ITEMS_SELECTOR=
PRIVATE_SPORT_SHOP_AMOUNT_ITEMS_XPATH=

# ITEM PROPERTIES SELECTORS
PRIVATE_SPORT_SHOP_DESCRIPTION_ITEM_SELECTOR=
PRIVATE_SPORT_SHOP_CURRENT_PRICE_ITEM_SELECTOR=
PRIVATE_SPORT_SHOP_CURRENT_DISCOUNT_ITEM_SELECTOR=
PRIVATE_SPORT_SHOP_IMAGE_ITEM_SELECTOR=
PRIVATE_SPORT_SHOP_BRAND_ITEM_SELECTOR=
PRIVATE_SPORT_SHOP_PROPERTIES_SELECTOR=
PRIVATE_SPORT_SHOP_LINK_SELECTOR=
PRIVATE_SPORT_SHOP_COLOR_PATTERN_REGEX=
PRIVATE_SPORT_SHOP_LINK_PATTERN_REGEX=

EMAIL_PRIVATE_SPORT_SHOP=
PASSWORD_PRIVATE_SPORT_SHOP=

# REDIS
REDIS_HOST=
REDIS_PORT=
REDIS_TOKEN=

# POSTGRESQL
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_SCHEMA=
````
5. **Construir imagen y correr en local**
```shell
docker build -t daily_chollos . &&
docker run --env-file .env -d -v  %cd%:/app -w /app -p 8000:8000 daily_chollos 
```
6. **Ejecutar migraciones**

Deberemos ejecutar el fichero "make.py". Seleccionar la opción 1 (Inicializar base de datos),
a continuación la 2 (crear migración) y por último la 3 (Aplicar migraciones)

## Sobre el proyecto
El proyecto se compone de una arquitectura Clean, con FastAPI como 
adapter para la capa de interfaz y la implementación del patrón repository y 
modelos (capa domain e infraestructura) con Tortoise.
Gracias a dicha arquitectura, se puede cambiar la capa de interfaz por cualquier
otra implementación sin apenas esfuerzo, haciendo así que el proyecto no esté
acoplado a ningún framework concreto, así como a ningún ORM.

## 📚 Uso
Visita la documentación generada automáticamente por FastAPI:
http://127.0.0.1:8000/docs
(Recuerda habilitarla en main.py si está desactivada).

Página principal:
http://127.0.0.1:8000

### Lanzar ruff
````shell
ruff check daily_chollos/
````
### Lanzar mypy
````shell
mypy daily_chollos/
````
### Actualizar pre-commit
````shell
pre-commit autoupdate
````

## 🤝 Contacto
Álvaro Marín - alvaromarin144@gmail.com

Encuentra el proyecto en GitHub.
