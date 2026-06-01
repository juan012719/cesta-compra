import streamlit as st
import requests

# --- CONFIGURACIÓN OCULTA ---
st.set_page_config(page_title="Cesta", page_icon="🛒", layout="centered")

# --- CSS AVANZADO: ADIÓS BARRAS, HOLA DISEÑO MODERNO ---
st.markdown("""
    <style>
    /* Ocultar barra superior, menú y logo de GitHub/Fork */
    header {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    
    /* Diseño de botones estilo App Nativa */
    div.stButton > button {
        border-radius: 12px !important;
        border: 1px solid #e6e6e6 !important;
        background-color: #ffffff !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04) !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        height: 50px !important;
        margin-bottom: 2px !important;
        transition: all 0.15s ease-in-out !important;
    }
    div.stButton > button:active {
        transform: scale(0.97) !important;
        background-color: #f5f5f5 !important;
    }
    /* El botón de borrar carro lo ponemos destacable pero sin ser agresivo */
    button[kind="primary"] {
        background-color: #ff4b4b !important;
        color: white !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

# --- LÓGICA DE DATOS ---
# Descargamos el catálogo ordenado por tu nueva columna 'orden'
resp_catalogo = requests.get(f"{URL}/rest/v1/catalogo?order=orden.asc,nombre.asc", headers=HEADERS)
catalogo_items = resp_catalogo.json() if resp_catalogo.status_code == 200 else []

response_lista = requests.get(f"{URL}/rest/v1/lista_compra?order=fecha_creacion.desc", headers=HEADERS)
items_lista = response_lista.json() if response_lista.status_code == 200 else []

nombres_en_lista = [i["producto"].lower() for i in items_lista if "producto" in i]

st.title("🛒 Cesta")

tab_lista, tab_añadir, tab_despensa = st.tabs(["📝 Lista", "➕ Añadir", "⚙️ Despensa"])

# ==========================================
# PESTAÑA 1: LISTA
# ==========================================
with tab_lista:
    if st.button("🗑️ Vaciar carro", type="primary", use_container_width=True):
        requests.delete(f"{URL}/rest/v1/lista_compra?id=not.is.null", headers=HEADERS)
        st.rerun()
        
    if not items_lista:
        st.info("La cesta está vacía. ¡A descansar!")
        
    for item in items_lista:
        if st.button(f"🛒 {item['producto']}", key=f"del_{item['id']}", use_container_width=True):
            requests.delete(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", headers=HEADERS)
            st.rerun()

# ==========================================
# PESTAÑA 2: AÑADIR (Aparecen ordenados como tú elijas)
# ==========================================
with tab_añadir:
    st.subheader("Rápidos")
    cols = st.columns(2)
    for i, item in enumerate(catalogo_items):
        prod = item["nombre"]
        ya_esta = prod.lower() in nombres_en_lista
        if cols[i % 2].button(prod, key=f"add_{item.get('id', i)}", disabled=ya_esta, use_container_width=True):
            requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": prod}, headers=HEADERS)
            st.rerun()
    
    st.divider()
    st.subheader("Puntual")
    producto_nuevo = st.text_input("Escribe el nombre:", label_visibility="collapsed", placeholder="Ej: Pilas AA")
    if st.button("➕ Añadir a la lista", use_container_width=True):
        if producto_nuevo and producto_nuevo.lower() not in nombres_en_lista:
            requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": producto_nuevo}, headers=HEADERS)
            st.rerun()
        elif producto_nuevo.lower() in nombres_en_lista:
            st.warning("¡Ya lo tienes en la lista!")

# ==========================================
# PESTAÑA 3: ORDENAR Y GESTIONAR DESPENSA
# ==========================================
with tab_despensa:
    st.subheader("Guardar nuevo habitual")
    nuevo = st.text_input("Nombre:", label_visibility="collapsed", placeholder="Ej: Huevos XL")
    if st.button("💾 Añadir a despensa", use_container_width=True):
        if nuevo:
            requests.post(f"{URL}/rest/v1/catalogo", json={"nombre": nuevo, "orden": 99}, headers=HEADERS)
            st.rerun()
            
    st.divider()
    st.subheader("Ordena tus productos")
    st.caption("Usa las flechas para colocarlos en el orden del pasillo del súper.")
    
    for i, item in enumerate(catalogo_items):
        # Usamos columnas ajustadas para que las flechas quepan perfectas en el móvil
        c1, c2, c3, c4 = st.columns([4, 1.2, 1.2, 1.2])
        
        c1.markdown(f"<div style='margin-top:10px;'><b>{item['nombre']}</b></div>", unsafe_allow_html=True)
        
        # Botón Subir
        if c2.button("⬆️", key=f"up_{item.get('id', i)}"):
            nuevo_orden = item.get('orden', i) - 1
            requests.patch(f"{URL}/rest/v1/catalogo?id=eq.{item['id']}", json={"orden": nuevo_orden}, headers=HEADERS)
            st.rerun()
            
        # Botón Bajar
        if c3.button("⬇️", key=f"dw_{item.get('id', i)}"):
            nuevo_orden = item.get('orden', i) + 1
            requests.patch(f"{URL}/rest/v1/catalogo?id=eq.{item['id']}", json={"orden": nuevo_orden}, headers=HEADERS)
            st.rerun()
            
        # Botón Borrar de la despensa definitivamente
        if c4.button("❌", key=f"rm_{item.get('id', i)}"):
            requests.delete(f"{URL}/rest/v1/catalogo?id=eq.{item['id']}", headers=HEADERS)
            st.rerun()
