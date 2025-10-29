#!/usr/bin/env python3
"""
Backend para Educambio con PostgreSQL (Neon)
Este backend guarda las asociaciones voluntario-donante en una base de datos Neon
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import csv
import io

app = Flask(__name__)
CORS(app)

# URL de conexión a Neon (cámbiala por tu URL real)
# Formato: postgresql://usuario:password@host/database?sslmode=require
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:password@ep-xxx.neon.tech/neondb?sslmode=require')

def get_db_connection():
    """Crear conexión a la base de datos"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return None

def init_database():
    """Inicializar la base de datos con la tabla necesaria"""
    conn = get_db_connection()
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    try:
        cur = conn.cursor()
        
        # Crear tabla si no existe
        cur.execute("""
            CREATE TABLE IF NOT EXISTS volunteer_tracking (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                name VARCHAR(255),
                volunteer_code VARCHAR(100) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_agent TEXT,
                referrer TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Crear índice para búsquedas rápidas por email
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_email 
            ON volunteer_tracking(email);
        """)
        
        # Crear índice para búsquedas por código de voluntario
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_volunteer_code 
            ON volunteer_tracking(volunteer_code);
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("✅ Base de datos inicializada correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        return False

@app.route('/api/track', methods=['POST'])
def track_donation():
    """Endpoint para recibir tracking de donaciones"""
    data = request.get_json()
    
    email = data.get('email')
    name = data.get('name', '')
    volunteer_code = data.get('volunteerCode', 'SIN_CODIGO')
    timestamp = data.get('timestamp', datetime.now().isoformat())
    user_agent = data.get('userAgent', '')
    referrer = data.get('referrer', '')
    
    # Validar email
    if not email:
        return jsonify({
            'success': False,
            'error': 'Email es requerido'
        }), 400
    
    # Conectar a la base de datos
    conn = get_db_connection()
    if not conn:
        return jsonify({
            'success': False,
            'error': 'Error de conexión a la base de datos'
        }), 500
    
    try:
        cur = conn.cursor()
        
        # Insertar registro
        cur.execute("""
            INSERT INTO volunteer_tracking 
            (email, name, volunteer_code, timestamp, user_agent, referrer)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            email.lower().strip(),
            name,
            volunteer_code,
            timestamp,
            user_agent,
            referrer
        ))
        
        record_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ Nuevo tracking guardado: {email} -> {volunteer_code} (ID: {record_id})")
        
        return jsonify({
            'success': True,
            'message': 'Tracking guardado exitosamente',
            'recordId': record_id
        })
        
    except Exception as e:
        print(f"❌ Error guardando tracking: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tracks', methods=['GET'])
def get_tracks():
    """Obtener todos los trackings"""
    conn = get_db_connection()
    if not conn:
        return jsonify({
            'success': False,
            'error': 'Error de conexión a la base de datos'
        }), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, email, name, volunteer_code, timestamp, 
                   user_agent, referrer, created_at
            FROM volunteer_tracking
            ORDER BY created_at DESC
        """)
        
        records = cur.fetchall()
        cur.close()
        conn.close()
        
        # Convertir a formato JSON serializable
        data = []
        for record in records:
            data.append({
                'id': record['id'],
                'email': record['email'],
                'name': record['name'],
                'volunteerCode': record['volunteer_code'],
                'timestamp': record['timestamp'].isoformat() if record['timestamp'] else None,
                'userAgent': record['user_agent'],
                'referrer': record['referrer'],
                'createdAt': record['created_at'].isoformat() if record['created_at'] else None
            })
        
        return jsonify({
            'success': True,
            'count': len(data),
            'data': data
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo tracks: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Exportar tracking a CSV"""
    conn = get_db_connection()
    if not conn:
        return jsonify({
            'success': False,
            'error': 'Error de conexión a la base de datos'
        }), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT email, name, volunteer_code, timestamp, id
            FROM volunteer_tracking
            ORDER BY timestamp DESC
        """)
        
        records = cur.fetchall()
        cur.close()
        conn.close()
        
        if not records:
            return jsonify({
                'success': False,
                'error': 'No hay datos para exportar'
            }), 404
        
        # Crear CSV en memoria
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Encabezados
        writer.writerow(['Email', 'Nombre', 'Código Voluntario', 'Fecha/Hora', 'ID'])
        
        # Datos
        for record in records:
            writer.writerow([
                record['email'],
                record['name'],
                record['volunteer_code'],
                record['timestamp'].isoformat() if record['timestamp'] else '',
                record['id']
            ])
        
        # Preparar respuesta
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=voluntarios_tracking.csv'
            }
        )
        
    except Exception as e:
        print(f"❌ Error exportando CSV: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Obtener estadísticas por voluntario"""
    conn = get_db_connection()
    if not conn:
        return jsonify({
            'success': False,
            'error': 'Error de conexión a la base de datos'
        }), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                volunteer_code,
                COUNT(*) as total_clicks,
                COUNT(DISTINCT email) as unique_emails
            FROM volunteer_tracking
            GROUP BY volunteer_code
            ORDER BY total_clicks DESC
        """)
        
        stats = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': [dict(row) for row in stats]
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Estado del servidor y conexión a BD"""
    conn = get_db_connection()
    
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('SELECT 1')
            cur.close()
            conn.close()
            db_status = 'connected'
        except:
            db_status = 'error'
    else:
        db_status = 'disconnected'
    
    return jsonify({
        'status': 'ok',
        'message': 'Backend de tracking funcionando correctamente',
        'database': db_status
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Backend Educambio - PostgreSQL (Neon)")
    print("=" * 60)
    print("")
    
    # Inicializar base de datos
    print("📊 Inicializando base de datos...")
    if init_database():
        print("")
        print("✅ Servidor listo para recibir peticiones")
        print("")
        print(f"🌐 Servidor corriendo en: http://localhost:3000")
        print(f"🗄️  Base de datos: Neon PostgreSQL")
        print("")
        print("Endpoints disponibles:")
        print("  POST /api/track        - Guardar tracking")
        print("  GET  /api/tracks       - Ver todos los trackings")
        print("  GET  /api/export/csv   - Exportar a CSV")
        print("  GET  /api/stats        - Estadísticas por voluntario")
        print("  GET  /health           - Estado del servidor")
        print("")
        print("=" * 60)
        
        app.run(host='0.0.0.0', port=3000, debug=True)
    else:
        print("")
        print("❌ Error: No se pudo inicializar la base de datos")
        print("Verifica tu DATABASE_URL y que Neon esté activo")

