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

def load_tracking_data(tracking_file='voluntarios_tracking.json'):
    """Cargar datos de tracking de voluntarios"""
    if not os.path.exists(tracking_file):
        print(f"❌ Error: No se encuentra el archivo {tracking_file}")
        return None
    
    try:
        with open(tracking_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ {len(data)} registros de tracking cargados")
        return data
    except Exception as e:
        print(f"❌ Error cargando tracking: {e}")
        return None

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
    """Generar reporte final"""
    try:
        matched_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n✅ Reporte generado exitosamente: {output_file}")
        
        # Resumen por voluntario
        if 'codigo_voluntario' in matched_df.columns:
            volunteer_summary = matched_df.groupby('codigo_voluntario').size().sort_values(ascending=False)
            
            print("\n📊 Resumen por voluntario:")
            print("="*50)
            for volunteer, count in volunteer_summary.items():
                if pd.notna(volunteer):
                    print(f"  {volunteer}: {count} donaciones")
            
            # Guardar resumen
            summary_file = 'resumen_voluntarios.csv'
            volunteer_summary.to_csv(summary_file, header=['cantidad_donaciones'])
            print(f"\n✅ Resumen por voluntario guardado en: {summary_file}")
        
        return True
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")
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
    tracking_data = load_tracking_data()
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

