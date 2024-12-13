import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import altair as alt
from urllib.parse import quote, unquote

# Configuración de la página con tema oscuro elegante
st.set_page_config(
    page_title="Luxury Collection",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    /* Estilos generales */
    .stApp {
        background-color: #1A1A1A;
        color: #FFFFFF;
    }
    
    /* Estilo para headers */
    .luxury-header {
        color: #E8E8E8;
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        padding: 2rem;
        border-bottom: 2px solid #D4AF37;
    }
    
    /* Estilo para cards */
    .luxury-card {
        background-color: #2A2A2A;
        border-radius: 10px;
        padding: 1.5rem;
        border: 1px solid #E8E8E8;
        margin: 1rem 0;
        transition: transform 0.3s ease;
    }
    
    .luxury-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3);
    }
    
    /* Estilo para métricas */
    .metric-container {
        background-color: #2A2A2A;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #E8E8E8;
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .metric-container:hover {
        transform: scale(1.05);
    }
    
    .metric-value {
        color: #D4AF37;
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    /* Personalización de la barra lateral */
    .css-1d391kg {
        background-color: #2A2A2A;
    }
    
    /* Estilo para botones */
    .stButton>button {
        background-color: #D4AF37;
        color: #1A1A1A;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #FFD700;
        color: #1A1A1A;
        transform: scale(1.02);
    }
    
    /* Estilo para selectbox */
    .stSelectbox>div>div {
        background-color: #2A2A2A;
        color: #FFFFFF;
        border: 1px solid #D4AF37;
    }
    
    /* Estilo para tablas */
    .dataframe {
        background-color: #2A2A2A !important;
        color: #FFFFFF !important;
    }
    
    th {
        background-color: #D4AF37 !important;
        color: #1A1A1A !important;
    }
    
    /* Estilo para expansores */
    .streamlit-expanderHeader {
        background-color: #2A2A2A;
        color: #D4AF37;
        border: 1px solid #D4AF37;
    }
</style>
""", unsafe_allow_html=True)

# Coordenadas de ubicaciones
COORDENADAS = {
    'Mónaco': (43.7384, 7.4246),
    'Miami': (25.7617, -80.1918),
    'Ibiza': (38.9067, 1.4206),
    'Toscana, Italia': (43.7711, 11.2486),
    'Los Ángeles, USA': (34.0522, -118.2437),
    'Madrid, España': (40.4168, -3.7038),
    'Saint-Tropez, Francia': (43.2727, 6.6406),
    'Dubai': (25.2048, 55.2708),
    'Londres': (51.5074, -0.1278),
    'Stuttgart': (48.7758, 9.1829),
    'Nueva York': (40.7128, -74.0060),
    'París': (48.8566, 2.3522)
}

# Función para obtener coordenadas
def obtener_coordenadas(ubicacion):
    return COORDENADAS.get(ubicacion, (48.8566 + np.random.randn() * 0.1, 2.3522 + np.random.randn() * 0.1))

# Función para obtener parámetros de la URL
def get_query_params():
    query_params = st.experimental_get_query_params()
    return {
        'categoria': query_params.get('categoria', ['Todos'])[0],
        'ubicacion': query_params.get('ubicacion', [''])[0],
        'fecha': query_params.get('fecha', [datetime.now().strftime('%Y-%m-%d')])[0]
    }

# Función para establecer parámetros en la URL
def set_query_params(categoria, ubicacion, fecha):
    params = {
        'categoria': categoria if categoria != 'Todos' else None,
        'ubicacion': ubicacion if ubicacion else None,
        'fecha': fecha.strftime('%Y-%m-%d')
    }
    params = {k: v for k, v in params.items() if v is not None}
    st.experimental_set_query_params(**params)

# Función para cargar datos
@st.cache_data
def cargar_datos():
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
        'descripcion': [
            'Elegante yate con acabados de lujo y amplias áreas de entretenimiento',
            'Yate deportivo con interiores personalizados y tecnología de última generación',
            'Mega yate con helipuerto y spa privado',
            'Villa histórica con viñedos privados y vistas panorámicas',
            'Residencia contemporánea con cine privado y spa',
            'Palacio histórico restaurado con jardines del siglo XVIII',
            'Villa frente al mar con infinity pool y bodega',
            'La máxima expresión del lujo sobre ruedas',
            'Gran turismo con prestaciones deportivas',
            'Superdeportivo híbrido de última generación',
            'SUV deportivo con acabados artesanales',
            'Icono del automovilismo deportivo',
            'Ultra long-range con suite principal',
            'El jet privado más lujoso del mundo',
            'Aeronave ejecutiva con tecnología de punta'
        ],
        'estado': ['Disponible'] * 15,
        'proxima_fecha_disponible': [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(15)]
    }
    return pd.DataFrame(datos_lujo)

# Logo y título elegante
st.markdown("""
<div class="luxury-header">
    ✨ LUXURY COLLECTION ✨
    <div style='font-size: 1rem; color: #A8A8A8;'>Experiencias Exclusivas</div>
</div>
""", unsafe_allow_html=True)

# Obtener parámetros iniciales de la URL
params = get_query_params()

# Sidebar con filtros
st.sidebar.markdown("""
<div style='text-align: center; padding: 1rem;'>
    <h2 style='color: #D4AF37; font-family: "Playfair Display", serif;'>Filtros de Búsqueda</h2>
</div>
""", unsafe_allow_html=True)

categoria = st.sidebar.selectbox(
    "Categoría",
    ["Todos", "Yate", "Mansión", "Vehículo", "Jet Privado"],
    index=["Todos", "Yate", "Mansión", "Vehículo", "Jet Privado"].index(params['categoria'])
    if params['categoria'] in ["Todos", "Yate", "Mansión", "Vehículo", "Jet Privado"] else 0
)

try:
    fecha_inicial = datetime.strptime(params['fecha'], '%Y-%m-%d')
except ValueError:
    fecha_inicial = datetime.now() + timedelta(days=1)

fecha = st.sidebar.date_input(
    "Fecha de Reserva",
    min_value=datetime.now(),
    value=fecha_inicial
)

ubicacion = st.sidebar.text_input(
    "Destino", 
    value=unquote(params['ubicacion']),
    placeholder="ej. Mónaco, Dubai..."
)

# Botón de búsqueda
if st.sidebar.button("EXPLORAR COLECCIÓN"):
    # Actualizar URL
    set_query_params(categoria, ubicacion, fecha)
    
    # Cargar y filtrar datos
    df = cargar_datos()
    df_filtrado = df.copy()
    
    if categoria != "Todos":
        df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria]
    if ubicacion:
        df_filtrado = df_filtrado[df_filtrado['ubicacion'].str.contains(ubicacion, case=False)]
    
    if not df_filtrado.empty:
        # Mostrar resultados en tarjetas
        for _, item in df_filtrado.iterrows():
            st.markdown(f"""
            <div class="luxury-card">
                <h3 style="color: #D4AF37;">{item['nombre']}</h3>
                <p style="color: #A8A8A8; font-style: italic;">{item['categoria']}</p>
                <p>{item['descripcion']}</p>
                <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
                    <span style="color: #D4AF37;">💎 ${item['precio_por_dia']:,}/día</span>
                    <span>📍 {item['ubicacion']}</span>
                    <span>👥 Capacidad: {item['capacidad']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Métricas
        st.markdown("<h3 style='color: #D4AF37; text-align: center; margin: 2rem 0;'>Resumen de Colección</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">${df_filtrado['precio_por_dia'].mean():,.0f}</div>
                <div>Precio Promedio/Día</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{len(df_filtrado)}</div>
                <div>Artículos Disponibles</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{df_filtrado['capacidad'].sum()}</div>
                <div>Capacidad Total</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Mapa de ubicaciones
        st.markdown("<h3 style='color: #D4AF37; text-align: center; margin: 2rem 0;'>Ubicaciones Exclusivas</h3>", unsafe_allow_html=True)
        df_mapa = pd.DataFrame(
            [obtener_coordenadas(ubicacion) for ubicacion in df_filtrado['ubicacion']],
            columns=['lat', 'lon']
        )
        st.map(df_mapa, zoom=2)
        
    else:
        st.markdown("""
        <div style='text-align: center; padding: 2rem; color: #D4AF37;'>
            No se encontraron artículos que coincidan con sus criterios de búsqueda.
        </div>
        """, unsafe_allow_html=True)

# Información del sistema
with st.expander("ℹ️ Información sobre el sistema"):
    st.markdown("""
    ### Cómo usar la aplicación:
    1. Selecciona la categoría de artículo que te interesa
    2. Elige la fecha deseada
    3. Opcionalmente, especifica una ubicación
    4. Haz clic en "Buscar" para ver los resultados disponibles
    
   ### Consultas vía URL:
    Puedes realizar consultas directamente usando la URL con los siguientes parámetros:
    - `?categoria=Yate` (Yate, Mansión, Vehículo, Jet Privado)
    - `?ubicacion=Miami` (Cualquier ubicación disponible)
    - `?fecha=2024-12-25` (Formato YYYY-MM-DD)
    
    Ejemplos de URLs:
    ```
    https://[tu-app].streamlit.app/?categoria=Yate
    https://[tu-app].streamlit.app/?ubicacion=Miami
    https://[tu-app].streamlit.app/?categoria=Yate&ubicacion=Miami&fecha=2024-12-25
    ```
    
    ### Categorías disponibles:
    - 🛥️ Yates de lujo
    - 🏰 Mansiones exclusivas
    - 🚗 Vehículos de alta gama
    - ✈️ Jets privados
    """)

# Footer elegante
st.markdown("""
<div style='text-align: center; padding: 2rem; margin-top: 3rem; border-top: 1px solid #D4AF37;'>
    <p style='color: #A8A8A8;'>Luxury Collection © 2024</p>
    <p style='color: #A8A8A8; font-size: 0.8rem;'>Donde el lujo encuentra la excelencia</p>
    <div style='color: #D4AF37; font-size: 0.8rem; margin-top: 1rem;'>
        ✨ Experiencias Exclusivas | Servicio Premium | Disponibilidad 24/7 ✨
    </div>
</div>
""", unsafe_allow_html=True)
