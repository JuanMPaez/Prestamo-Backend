Como correr el servidor:

# Crear variables de entorno .env
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_NAME=

# Crear entorno
virtualenv .venv
# O
python -m venv .venv

# Activar entorno
source .venv\bin\activate

# Instalar dependencias en el entorno
pip install -r .\requirements.txt

# Correr servidor
flask run