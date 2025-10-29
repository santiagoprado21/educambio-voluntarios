#!/usr/bin/env python3
"""
Script para hacer matching entre el tracking de voluntarios 
y las exportaciones de suscripciones.co
"""

import json
import csv
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import requests

# URL del backend en Render
BACKEND_URL = 'https://educambio-voluntarios.onrender.com'

def load_tracking_data_from_api(backend_url=BACKEND_URL):
    """Cargar datos de tracking desde la API de Render"""
    try:
        print(f"🔗 Conectando con el backend...")
        print(f"   URL: {backend_url}")
        
        response = requests.get(f"{backend_url}/api/tracks", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'data' in data:
                tracking_records = data['data']
                print(f"✅ {len(tracking_records)} registros de tracking obtenidos desde Render")
                return tracking_records
            else:
                print(f"⚠️ Respuesta inesperada del backend")
                return None
        else:
            print(f"❌ Error del backend: Status {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"⚠️ Timeout conectando al backend (puede estar 'despertando'...)")
        print(f"   Esperando 30 segundos más...")
        try:
            response = requests.get(f"{backend_url}/api/tracks", timeout=60)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'data' in data:
                    tracking_records = data['data']
                    print(f"✅ {len(tracking_records)} registros de tracking obtenidos")
                    return tracking_records
        except Exception as e:
            print(f"❌ Error después del segundo intento: {e}")
            return None
    except Exception as e:
        print(f"❌ Error conectando con el backend: {e}")
        return None

def load_tracking_data_from_file(tracking_file='voluntarios_tracking.json'):
    """Cargar datos de tracking desde archivo local (fallback)"""
    if not os.path.exists(tracking_file):
        return None
    
    try:
        with open(tracking_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ {len(data)} registros de tracking cargados desde archivo local")
        return data
    except Exception as e:
        print(f"❌ Error cargando tracking desde archivo: {e}")
        return None

def load_tracking_data(backend_url=BACKEND_URL):
    """Cargar datos de tracking (primero desde API, luego desde archivo local)"""
    print("\n📥 Obteniendo tracking de voluntarios...")
    
    # Intentar primero desde la API
    data = load_tracking_data_from_api(backend_url)
    
    # Si falla, intentar desde archivo local
    if data is None:
        print("\n⚠️ No se pudo obtener datos desde la API")
        print("📂 Intentando cargar desde archivo local...")
        data = load_tracking_data_from_file()
    
    if data is None:
        print("\n❌ Error: No se pudieron cargar los datos de tracking")
        print("\nOpciones:")
        print("  1. Verifica que el backend esté activo:")
        print(f"     {backend_url}/health")
        print("  2. O asegúrate de tener el archivo 'voluntarios_tracking.json'")
    
    return data

def load_donations_export(export_file):
    """Cargar exportación de suscripciones.co"""
    if not os.path.exists(export_file):
        print(f"❌ Error: No se encuentra el archivo {export_file}")
        return None
    
    try:
        # Intentar detectar el formato (CSV o Excel)
        if export_file.endswith('.csv'):
            df = pd.read_csv(export_file)
        elif export_file.endswith('.xlsx') or export_file.endswith('.xls'):
            df = pd.read_excel(export_file)
        else:
            print("❌ Error: El archivo debe ser CSV o Excel (.csv, .xlsx, .xls)")
            return None
        
        print(f"✅ {len(df)} donaciones cargadas desde la exportación")
        print(f"📋 Columnas disponibles: {', '.join(df.columns)}")
        return df
    except Exception as e:
        print(f"❌ Error cargando donaciones: {e}")
        return None

def normalize_email(email):
    """Normalizar email para matching"""
    if pd.isna(email):
        return None
    return str(email).lower().strip()

def match_donations(tracking_data, donations_df, email_column='email', 
                   date_column=None, time_window_hours=48):
    """
    Hacer matching entre tracking y donaciones
    
    Args:
        tracking_data: Lista de diccionarios con tracking
        donations_df: DataFrame con donaciones de suscripciones.co
        email_column: Nombre de la columna de email en donations_df
        date_column: Nombre de la columna de fecha en donations_df (opcional)
        time_window_hours: Ventana de tiempo para matching por fecha (default: 48 horas)
    """
    
    # Verificar que existe la columna de email
    if email_column not in donations_df.columns:
        print(f"❌ Error: La columna '{email_column}' no existe en la exportación")
        print(f"Columnas disponibles: {', '.join(donations_df.columns)}")
        return None
    
    # Normalizar emails en donaciones
    donations_df['email_normalized'] = donations_df[email_column].apply(normalize_email)
    
    # Crear diccionario de tracking por email
    tracking_dict = {}
    for record in tracking_data:
        email = normalize_email(record['email'])
        if email:
            if email not in tracking_dict:
                tracking_dict[email] = []
            tracking_dict[email].append(record)
    
    # Agregar columna de código de voluntario
    donations_df['codigo_voluntario'] = None
    donations_df['tracking_timestamp'] = None
    donations_df['match_method'] = None
    
    matches = 0
    no_matches = 0
    
    for idx, row in donations_df.iterrows():
        email = row['email_normalized']
        
        if email in tracking_dict:
            tracking_records = tracking_dict[email]
            
            # Si solo hay un registro, usar ese
            if len(tracking_records) == 1:
                donations_df.at[idx, 'codigo_voluntario'] = tracking_records[0]['volunteerCode']
                donations_df.at[idx, 'tracking_timestamp'] = tracking_records[0]['timestamp']
                donations_df.at[idx, 'match_method'] = 'exact_email'
                matches += 1
            else:
                # Si hay múltiples registros, intentar matching por fecha si está disponible
                if date_column and date_column in donations_df.columns:
                    donation_date = pd.to_datetime(row[date_column], errors='coerce')
                    
                    if not pd.isna(donation_date):
                        # Buscar el tracking más cercano en tiempo
                        best_match = None
                        min_diff = timedelta(hours=time_window_hours)
                        
                        for record in tracking_records:
                            tracking_date = pd.to_datetime(record['timestamp'], errors='coerce')
                            if not pd.isna(tracking_date):
                                diff = abs(donation_date - tracking_date)
                                if diff < min_diff:
                                    min_diff = diff
                                    best_match = record
                        
                        if best_match:
                            donations_df.at[idx, 'codigo_voluntario'] = best_match['volunteerCode']
                            donations_df.at[idx, 'tracking_timestamp'] = best_match['timestamp']
                            donations_df.at[idx, 'match_method'] = 'email_and_date'
                            matches += 1
                        else:
                            # Usar el más reciente
                            tracking_records.sort(key=lambda x: x['timestamp'], reverse=True)
                            donations_df.at[idx, 'codigo_voluntario'] = tracking_records[0]['volunteerCode']
                            donations_df.at[idx, 'tracking_timestamp'] = tracking_records[0]['timestamp']
                            donations_df.at[idx, 'match_method'] = 'email_latest'
                            matches += 1
                else:
                    # Sin fecha, usar el más reciente
                    tracking_records.sort(key=lambda x: x['timestamp'], reverse=True)
                    donations_df.at[idx, 'codigo_voluntario'] = tracking_records[0]['volunteerCode']
                    donations_df.at[idx, 'tracking_timestamp'] = tracking_records[0]['timestamp']
                    donations_df.at[idx, 'match_method'] = 'email_latest'
                    matches += 1
        else:
            no_matches += 1
    
    print(f"\n📊 Resultados del matching:")
    print(f"  ✅ Matches encontrados: {matches} ({matches/len(donations_df)*100:.1f}%)")
    print(f"  ❌ Sin match: {no_matches} ({no_matches/len(donations_df)*100:.1f}%)")
    
    return donations_df

def generate_report(matched_df, output_file='donaciones_con_voluntarios.csv'):
    """Generar reporte final con análisis completo"""
    try:
        matched_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n✅ Reporte detallado generado: {output_file}")
        
        # Resumen por voluntario con análisis completo
        if 'codigo_voluntario' in matched_df.columns:
            # Preparar datos
            volunteer_data = matched_df[pd.notna(matched_df['codigo_voluntario'])].copy()
            
            if len(volunteer_data) == 0:
                print("\n⚠️ No hay donaciones con voluntarios asignados")
                return True
            
            # Detectar columna de monto
            amount_col = None
            for col in ['amount', 'monto', 'valor', 'total']:
                if col in volunteer_data.columns:
                    amount_col = col
                    break
            
            # Crear resumen completo
            summary_data = []
            
            for volunteer in volunteer_data['codigo_voluntario'].unique():
                volunteer_donations = volunteer_data[volunteer_data['codigo_voluntario'] == volunteer]
                
                # Estadísticas básicas
                total_donations = len(volunteer_donations)
                
                # Estadísticas de monto (si existe columna)
                if amount_col:
                    amounts = pd.to_numeric(volunteer_donations[amount_col], errors='coerce')
                    total_amount = amounts.sum()
                    avg_amount = amounts.mean()
                    max_amount = amounts.max()
                else:
                    total_amount = 0
                    avg_amount = 0
                    max_amount = 0
                
                # Fechas (si existen)
                date_cols = [col for col in volunteer_donations.columns if 'date' in col.lower() or 'fecha' in col.lower()]
                if date_cols:
                    dates = pd.to_datetime(volunteer_donations[date_cols[0]], errors='coerce')
                    first_date = dates.min()
                    last_date = dates.max()
                else:
                    first_date = None
                    last_date = None
                
                summary_data.append({
                    'voluntario': volunteer,
                    'total_donaciones': total_donations,
                    'monto_total': total_amount,
                    'monto_promedio': avg_amount,
                    'donacion_maxima': max_amount,
                    'primera_donacion': first_date,
                    'ultima_donacion': last_date
                })
            
            # Crear DataFrame del resumen
            summary_df = pd.DataFrame(summary_data)
            summary_df = summary_df.sort_values('monto_total', ascending=False)
            
            # Guardar resumen completo
            summary_file = 'resumen_voluntarios.csv'
            summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')
            print(f"\n✅ Resumen completo guardado en: {summary_file}")
            
            # Mostrar resumen en consola
            print("\n📊 RESUMEN POR VOLUNTARIO:")
            print("="*80)
            
            for _, row in summary_df.iterrows():
                volunteer = row['voluntario']
                count = int(row['total_donaciones'])
                
                if amount_col and row['monto_total'] > 0:
                    total = f"${row['monto_total']:,.0f}"
                    avg = f"${row['monto_promedio']:,.0f}"
                    max_don = f"${row['donacion_maxima']:,.0f}"
                    print(f"  🏆 {volunteer}:")
                    print(f"     • {count} donaciones")
                    print(f"     • Total: {total}")
                    print(f"     • Promedio: {avg}")
                    print(f"     • Donación máxima: {max_don}")
                else:
                    print(f"  🏆 {volunteer}: {count} donaciones")
            
            print("="*80)
            
            # Mostrar TOP 3
            if len(summary_df) > 0:
                print("\n🥇 TOP 3 VOLUNTARIOS:")
                print("-"*80)
                for idx, (_, row) in enumerate(summary_df.head(3).iterrows(), 1):
                    emoji = ['🥇', '🥈', '🥉'][idx-1]
                    volunteer = row['voluntario']
                    count = int(row['total_donaciones'])
                    
                    if amount_col and row['monto_total'] > 0:
                        total = f"${row['monto_total']:,.0f}"
                        print(f"  {emoji} {volunteer}: {count} donaciones - {total}")
                    else:
                        print(f"  {emoji} {volunteer}: {count} donaciones")
                print("-"*80)
            
            # Calcular tasa de conversión (si tenemos datos de tracking)
            # Esta información vendría del backend
            print("\n💡 Tip: Para ver la tasa de conversión (clicks vs donaciones),")
            print("   visita: https://educambio-voluntarios.onrender.com/api/stats")
        
        return True
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("="*60)
    print("🎯 MATCHER DE DONACIONES Y VOLUNTARIOS - EDUCAMBIO")
    print("="*60)
    
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("\n📝 Uso:")
        print("  python matcher.py <archivo_exportacion_suscripciones>")
        print("\nEjemplos:")
        print("  python matcher.py donaciones.csv")
        print("  python matcher.py donaciones.xlsx")
        print("\nOpciones avanzadas:")
        print("  python matcher.py donaciones.csv --email-column correo --date-column fecha")
        return
    
    export_file = sys.argv[1]
    
    # Parámetros opcionales
    email_column = 'email'
    date_column = None
    
    # Parsear argumentos adicionales
    for i in range(2, len(sys.argv)):
        if sys.argv[i] == '--email-column' and i + 1 < len(sys.argv):
            email_column = sys.argv[i + 1]
        elif sys.argv[i] == '--date-column' and i + 1 < len(sys.argv):
            date_column = sys.argv[i + 1]
    
    print(f"\n📂 Archivo de donaciones: {export_file}")
    print(f"📧 Columna de email: {email_column}")
    if date_column:
        print(f"📅 Columna de fecha: {date_column}")
    
    # Cargar datos
    print("\n" + "="*60)
    tracking_data = load_tracking_data(BACKEND_URL)
    if tracking_data is None:
        return
    
    donations_df = load_donations_export(export_file)
    if donations_df is None:
        return
    
    # Hacer matching
    print("\n" + "="*60)
    print("🔍 Haciendo matching...")
    matched_df = match_donations(tracking_data, donations_df, email_column, date_column)
    
    if matched_df is None:
        return
    
    # Generar reporte
    print("\n" + "="*60)
    generate_report(matched_df)
    
    print("\n" + "="*60)
    print("✅ Proceso completado exitosamente!")
    print("="*60)

if __name__ == '__main__':
    main()

