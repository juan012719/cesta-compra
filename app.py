import streamlit as st
import requests

# Configuración de página
st.set_page_config(page_title="Cesta", page_icon="🛒", layout="centered")

# Credenciales desde los secretos de Streamlit
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- LÓGICA DE DATOS ---
# Descargamos los productos fijos
resp_catalogo = requests.get(f"{URL}/rest/v1/catalogo?order=nombre.asc", headers=HEADERS)
productos_habituales = [item["nombre"] for item in resp_catalogo.json()] if resp_catalogo.status_code == 200 else []

# Descargamos la lista activa
response_lista = requests.get(f"{URL}/rest/v1/lista_compra?order=fecha_creacion.desc", headers=HEADERS)
items_lista = response_lista.json() if response_lista.status_code == 200 else []

st.title("🛒 Cesta de la Compra")

tab_lista, tab_añadir = st.tabs(["📝 Mi Lista", "➕ Añadir"])

# --- PESTAÑA 1: MI LISTA ---
with tab_lista:
    if st.button("🗑️ Vaciar lista", type="primary", use_container_width=True):
        requests.delete(f"{URL}/rest/v1/lista_compra?id=gt.0", headers=HEADERS)
        st.rerun()
        
    st.subheader("Pendientes")
    for item in items_lista:
        # Al pulsar el producto, se elimina directamente de la base de datos (infalible)
        if st.button(f"🛒 {item['producto']}", key=f"del_{item['id']}", use_container_width=True):
            requests.delete(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", headers=HEADERS)
            st.rerun()

# --- PESTAÑA 2: AÑADIR ---
with tab_añadir:
    st.subheader("⚡ Añadir rápido")
    cols = st.columns(2)
    for i, prod in enumerate(productos_habituales):
        if cols[i % 2].button(prod, key=f"cat_{i}", use_container_width=True):
            requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": prod}, headers=HEADERS)
            st.rerun()
    
    st.divider()
    producto_nuevo = st.text_input("✍️ O escribir algo puntual:")
    if st.button("Añadir a la lista", use_container_width=True):
        if producto_nuevo != "":
            requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": producto_nuevo}, headers=HEADERS)
            st.rerun()
