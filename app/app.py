import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)

# Configuración de la conexión a la base de datos
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'), # 'localhost'
        database=os.getenv('DB_NAME'), # 'postgres'
        user=os.getenv('DB_USER'), # 'worker'
        password=os.getenv('DB_PASSWORD'), # 'password'
        port=os.getenv('DB_PORT')
    )
    return conn

# Endpoint para agregar tipos de préstamo
@app.route('/api/tipos-prestamo', methods=['POST'])
def agregar_tipo_prestamo():
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO tipos_prestamo (name, annualInterestRate, minimumAmount, maximumAmount, minimumTerm, maximumTerm) VALUES (%s, %s, %s, %s, %s, %s)',
            (data['name'], data['annualInterestRate'], data['minimumAmount'], data['maximumAmount'], data['minimumTerm'], data['maximumTerm'])
        )
        conn.commit()
        return jsonify({'status': True}), 201
    except Exception as e:
        return jsonify({'error': f'Error al enviar los datos: {str(e)}'}), 400
    finally:
        cur.close()
        conn.close()

# Endpoint para recuperar los tipos de préstamos
@app.route('/api/tipos-prestamo', methods=['GET'])
def obtener_tipos_prestamo():
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM tipos_prestamo ORDER BY name')
        conn.commit()
        columnas = [obj[0] for obj in cur.description]
        tipos_prestamos = [
            {
                columnas[index]: val for index, val in enumerate(obj)
            } for obj in cur.fetchall()
        ]
        return jsonify({
            'resultados': tipos_prestamos
        })
    except Exception as e:
        return jsonify({'error': f'Error al obtener los datos: {str(e)}'}), 400
    finally:
        cur.close()
        conn.close()

# Endpoint para recuperar un tipo de préstamo y calcular la simulación
@app.route('/api/tipos-prestamo/<int:id>/simulacion', methods=['GET'])
def simular_prestamo(id):
    monto = request.args.get('monto', type=float)
    plazo = request.args.get('plazo', type=int)

    if monto is None or plazo is None:
        return jsonify({'error': 'Se requieren monto y plazo'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tipos_prestamo WHERE id = %s', (id,))
    tipo_prestamo = cur.fetchone()

    if tipo_prestamo is None:
            cur.close()
            conn.close()
            return jsonify({'error': 'Tipo de préstamo no encontrado'}), 404
    
    tasa_interes = float(tipo_prestamo[2]) if tipo_prestamo[2] is not None else None
    
    if tasa_interes is None:
        cur.close()
        conn.close()
        return jsonify({'error': 'Tasa de interés no definida para este tipo de préstamo'}), 500

    try:
        cuota_mensual = calcular_cuota(monto, plazo, tasa_interes)  # Interes anual es el tercer elemento
        costo_total = cuota_mensual * plazo
    except Exception as e:
        cur.close()
        conn.close()
        return jsonify({'error': f'Error al calcular la cuota: {str(e)}'}), 500

    cur.close()
    conn.close()
    
    return jsonify({
        'cuota_mensual': cuota_mensual,
        'costo_total': costo_total
    })

# Función para calcular la cuota mensual
def calcular_cuota(monto, plazo, tasaInteres):
    tasa_mensual = tasaInteres / 12 / 100
    numerador = monto * tasa_mensual * (1 + tasa_mensual) ** plazo
    denominador = (1 + tasa_mensual) ** plazo - 1

    if denominador == 0:
        return 0  # Manejo de error
    return numerador / denominador

# Iniciar el servidor
if __name__ == '__main__':
    app.run(debug=True)