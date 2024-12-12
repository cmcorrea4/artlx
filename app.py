import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import altair as alt

# Configuración de la página
st.set_page_config(page_title="Luxury Items Rental", layout="wide")

# Título y descripción
st.title("🎯 Sistema de Reservas de Artículos de Lujo")
st.markdown("""
Esta aplicación te permite buscar y visualizar la disponibilidad de artículos de lujo como yates, 
mansiones, vehículos de alta gama y jets privados.
""")

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
    # Construir parámetros de búsqueda
    params = {}
    if categoria != "Todos":
        params['categoria'] = categoria
    if ubicacion:
        params['ubicacion'] = ubicacion
    params['fecha_inicio'] = fecha.strftime('%Y-%m-%d')
    
    # Realizar petición a la API
    try:
        response = requests.get('http://localhost:8000/items/disponibles', params=params)
        if response.status_code == 200:
            datos = response.json()
            if datos:
                # Convertir a DataFrame
                df = pd.DataFrame(datos)
                
                # Mostrar resultados
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("Artículos Disponibles")
                    st.dataframe(
                        df[['nombre', 'categoria', 'ubicacion', 'precio_por_dia', 'capacidad', 'estado']],
                        hide_index=True
                    )
                
                with col2:
                    st.subheader("Distribución de Precios")
                    # Crear gráfico con Altair
                    chart = alt.Chart(df).mark_bar().encode(
                        x='categoria:N',
                        y='precio_por_dia:Q',
                        color='categoria:N'
                    ).properties(
                        title='Precios por Categoría'
                    )
                    st.altair_chart(chart, use_container_width=True)
                
                # Estadísticas resumidas
                st.subheader("Resumen Estadístico")
                col3, col4, col5 = st.columns(3)
                with col3:
                    st.metric("Precio Promedio", f"${df['precio_por_dia'].mean():,.2f}")
                with col4:
                    st.metric("Total Artículos", len(df))
                with col5:
                    st.metric("Capacidad Total", df['capacidad'].sum())
                
                # Mapa de ubicaciones
                st.subheader("Ubicaciones Disponibles")
                df['lat'] = df['ubicacion'].map(lambda x: 40 + pd.np.random.randn())  # Simulado
                df['lon'] = df['ubicacion'].map(lambda x: -3 + pd.np.random.randn())  # Simulado
                st.map(df)
                
                # Tabla de disponibilidad por categoría
                st.subheader("Disponibilidad por Categoría")
                disponibilidad = df['categoria'].value_counts().reset_index()
                disponibilidad.columns = ['Categoría', 'Cantidad']
                st.bar_chart(disponibilidad.set_index('Categoría'))
                
            else:
                st.warning("No se encontraron artículos disponibles con los criterios especificados.")
        else:
            st.error("Error al consultar la API")
    except requests.exceptions.ConnectionError:
        st.error("No se pudo conectar con la API. Asegúrate de que esté en ejecución.")

# Información adicional
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
