# app.py
import streamlit as st
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from datetime import datetime, timedelta
import altair as alt
from typing import Optional, List
import json

# Inicializar FastAPI dentro de Streamlit
st.set_page_config(page_title="Luxury Items Rental", layout="wide")

# Crear la instancia de FastAPI
api = FastAPI()

# Configurar CORS
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Función para cargar datos (simulados)
@st.cache_data
def cargar_datos():
    # Datos de ejemplo
    datos_lujo = {
        'id': range(1, 16),
        'categoria': [
            'Yate', 'Yate', 'Yate',
            'Mansión', 'Mansión', 'Mansión', 'Mansión',
            'Vehículo', 'Vehículo', 'Vehículo', 'Vehículo', 'Vehículo',
            'Jet Privado', 'Jet Privado', 'Jet Privado'
        ],
        'nombre': [
            'Azimut 80', 'Sunseeker 95', 'Ferretti 920',
            'Villa Toscana', 'Mansión Beverly Hills', 'Palacio Madrid', 'Villa Saint-Tropez',
            'Rolls-Royce Phantom', 'Bentley Continental GT', 'Ferrari SF90', 'Lamborghini Urus', 'Porsche 911 GT3',
            'Gulfstream G650', 'Bombardier Global 7500', 'Dassault Falcon 8X'
        ],
        'precio_por_dia': [
            15000, 20000, 25000,
            8000, 12000, 10000, 15000,
            2000, 1500, 3000, 2500, 2000,
            45000, 50000, 40000
        ],
        'ubicacion': [
            'Mónaco', 'Miami', 'Ibiza',
            'Toscana, Italia', 'Los Ángeles, USA', 'Madrid, España', 'Saint-Tropez, Francia',
            'Dubai', 'Londres', 'Mónaco', 'Miami', 'Stuttgart',
            'Nueva York', 'Londres', 'París'
        ],
        'capacidad': [
            12, 14, 16,
            20, 25, 18, 15,
            4, 4, 2, 5, 2,
            16, 19, 14
        ],
        'estado': ['Disponible'] * 15,
        'proxima_fecha_disponible': [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(15)]
    }
    return pd.DataFrame(datos_lujo)

# Funciones de la API integradas
def filtrar_items(
    df: pd.DataFrame,
    categoria: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    ubicacion: Optional[str] = None
):
    resultado = df.copy()
    
    if categoria and categoria != "Todos":
        resultado = resultado[resultado['categoria'] == categoria]
    
    if fecha_inicio:
        fecha = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        resultado = resultado[pd.to_datetime(resultado['proxima_fecha_disponible']) <= fecha]
    
    if ubicacion:
        resultado = resultado[resultado['ubicacion'].str.contains(ubicacion, case=False)]
    
    return resultado[resultado['estado'] == 'Disponible']

# Interfaz de Streamlit
st.title("🎯 Sistema de Reservas de Artículos de Lujo")

# Sidebar para filtros
st.sidebar.header("Filtros de Búsqueda")

# Filtros
categoria = st.sidebar.selectbox(
    "Selecciona Categoría",
    ["Todos", "Yate", "Mansión", "Vehículo", "Jet Privado"]
)

fecha = st.sidebar.date_input(
    "Fecha deseada",
    min_value=datetime.now(),
    value=datetime.now() + timedelta(days=1)
)

ubicacion = st.sidebar.text_input("Ubicación (opcional)")

# Botón de búsqueda
if st.sidebar.button("Buscar"):
    # Cargar y filtrar datos directamente
    df = cargar_datos()
    df_filtrado = filtrar_items(
        df,
        categoria=categoria,
        fecha_inicio=fecha.strftime('%Y-%m-%d'),
        ubicacion=ubicacion
    )
    
    if not df_filtrado.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Artículos Disponibles")
            st.dataframe(
                df_filtrado[['nombre', 'categoria', 'ubicacion', 'precio_por_dia', 'capacidad', 'estado']],
                hide_index=True
            )
        
        with col2:
            st.subheader("Distribución de Precios")
            chart = alt.Chart(df_filtrado).mark_bar().encode(
                x='categoria:N',
                y='precio_por_dia:Q',
                color='categoria:N'
            ).properties(
                title='Precios por Categoría'
            )
            st.altair_chart(chart, use_container_width=True)
        
        # Estadísticas
        st.subheader("Resumen Estadístico")
        col3, col4, col5 = st.columns(3)
        with col3:
            st.metric("Precio Promedio", f"${df_filtrado['precio_por_dia'].mean():,.2f}")
        with col4:
            st.metric("Total Artículos", len(df_filtrado))
        with col5:
            st.metric("Capacidad Total", df_filtrado['capacidad'].sum())
        
        # Mapa
        st.subheader("Ubicaciones Disponibles")
        df_filtrado['lat'] = df_filtrado['ubicacion'].map(lambda x: 40 + pd.np.random.randn())
        df_filtrado['lon'] = df_filtrado['ubicacion'].map(lambda x: -3 + pd.np.random.randn())
        st.map(df_filtrado)
    else:
        st.warning("No se encontraron artículos disponibles con los criterios especificados.")

# Información del sistema
with st.expander("ℹ️ Información sobre el sistema"):
    st.markdown("""
    ### Cómo usar la aplicación:
    1. Selecciona la categoría de artículo que te interesa
    2. Elige la fecha deseada
    3. Opcionalmente, especifica una ubicación
    4. Haz clic en "Buscar" para ver los resultados disponibles
    
    ### Categorías disponibles:
    - 🛥️ Yates de lujo
    - 🏰 Mansiones exclusivas
    - 🚗 Vehículos de alta gama
    - ✈️ Jets privados
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Desarrollado con ❤️ por Tu Empresa")
