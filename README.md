# 🌿 Be Rural - Plataforma para la Repoblación Rural 🏡

## 📖 Descripción

Be Rural es una Web App desarrollada en Django como parte de la asignatura Proyectos II. Su misión es incentivar y facilitar la repoblación de municipios en riesgo de despoblación en España, conectando a potenciales nuevos residentes con localidades interesadas en atraer población.


## 🚀 Funcionalidades Principales

✅ Exploración de municipios con información clave

✅ Sistema de comunicación entre usuarios y ayuntamientos

✅ Acceso a oportunidades de teletrabajo y emprendimiento

✅ Visualización de incentivos y beneficios para nuevos residentes

✅ Interacción con la comunidad mediante foros y experiencias


## 🛠️ Tecnologías Utilizadas

- 🐍 Backend: Django (Python)

- 🎨 Frontend: HTML, CSS, JavaScript

- 🗄️ Base de Datos: PostgreSQL / SQLite


## 🏗️ Instalación

### 📌 Requisitos Previos

Asegúrate de contar en tu editor (preferiblemente VSCode) y tu equipo:
- Python 3.8 o superior
- Extensión de "Django" de VS Code

### 🛠️ Pasos de Instalación:
1️⃣ Clona el repositorio:
En una carpeta vacía abre una terminal de git y ejecuta los siguientes comandos
```sh
   git init
   git clone https://github.com/usuario/BeRural.git
   cd BeRural
   ```
2️⃣ Crea y activa un entorno virtual:
En la misma terminal ejecuta los siguientes comandos
```sh
   python -m venv venv
   source venv/bin/activate  # En Windows usa: .venv\Scripts\activate
   ```
En el caso de que el primer comando no funcione ❌ prueba lo siguiente
```sh
   py.exe -m venv venv
   source venv/bin/activate  # En Windows usa: .venv\Scripts\activate
   ```
3️⃣ Instala las dependencias:
Una vez activo el entorno virtual (venv) ejecuta el siguiente comando en la terminal
```sh
   pip install -r requirements.txt
   ```
Con este comando se instalarán todas las dependencias necesarias para soportar el proyecto

4️⃣ Realiza migraciones y ejecuta el servidor:
```sh
   python manage.py migrate
   python manage.py runserver
   ```
Después de ejecutar el último comando en la terminal aparecerá un link "http://127.0.0.1:8000/". Si haces click en él se te redirigirá a la pantalla principal de la app. 

## 🎯 Uso
1️⃣ Accede a http://127.0.0.1:8000/ en tu navegador.

2️⃣ Regístrate o inicia sesión.

3️⃣ Explora los municipios disponibles y sus incentivos.

4️⃣ Contacta con ayuntamientos y otros usuarios interesados.
