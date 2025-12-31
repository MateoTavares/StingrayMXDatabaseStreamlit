
import streamlit as st
import psycopg2
import pandas as pd

def init_connection():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASS"]
    )

# Función para ejecutar consultas (Outputs)
def run_query(query):
    conn = init_connection()
    try:
        df = pd.read_sql(query, conn) # Pandas lee SQL directo y lo vuelve tabla
        return df
    finally:
        conn.close()

# Función para insertar datos (Inputs)
def insert_data(nombre, tipo, precio, stock):
    conn = init_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO productos (nombre, tipo_piel, precio, stock)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (nombre, tipo, precio, stock))
        conn.commit()
        st.success(f"Producto '{nombre}' agregado correctamente.")
    except Exception as e:
        st.error(f"Error al guardar: {e}")
    finally:
        conn.close()

# --- Interfaz Gráfica con Streamlit ---
st.title("🐊 Inventario: Pieles Exóticas")

# 1. SECCIÓN DE INPUTS (Formulario)
st.header("Agregar Nuevo Producto")
with st.form("entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        nombre_input = st.text_input("Nombre del Artículo")
        tipo_piel_input = st.selectbox("Tipo de Piel", ["Cocodrilo", "Avestruz", "Mantarraya", "Pitón", "Otro"])
    with col2:
        precio_input = st.number_input("Precio ($)", min_value=0.0, format="%.2f")
        stock_input = st.number_input("Cantidad en Stock", min_value=0, step=1)
    
    submitted = st.form_submit_button("Guardar Producto")
    
    if submitted:
        if nombre_input:
            insert_data(nombre_input, tipo_piel_input, precio_input, stock_input)
        else:
            st.warning("Por favor escribe un nombre.")

# 2. SECCIÓN DE OUTPUTS (Tabla)
st.divider()
st.header("Inventario Actual")

# Botón para refrescar manualmente
if st.button("Actualizar Tabla"):
    st.rerun()

# Cargar y mostrar datos
try:
    df_productos = run_query("SELECT * FROM productos ORDER BY id DESC;")
    st.dataframe(df_productos, use_container_width=True)
except Exception as e:
    st.error(f"Error de conexión: {e}")