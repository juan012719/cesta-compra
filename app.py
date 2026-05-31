import streamlit as st
import requests

# Forzamos que la app se adapte bien al ancho del móvil
st.set_page_config(page_title="Lista de la Compra", page_icon="🛒", layout="centered")

URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

st.title("🛒 Cesta de la Compra")

# --- OBTENER EL CATÁLOGO DESDE SUPABASE ---
resp_catalogo = requests.get(f"{URL}/rest/v1/catalogo?order=nombre.asc", headers=HEADERS)
productos_habituales = [item["nombre"] for item in resp_catalogo.json()] if resp_catalogo.status_code == 200 else []

# --- BOTONES DIRECTOS (A GOLPE DE CLIC) ---
st.subheader("⚡ Añadir rápido")
if productos_habituales:
    # Crear una cuadrícula de 2 columnas para que los botones sean grandes en el móvil
    cols = st.columns(2)
    for i, producto in enumerate(productos_habituales):
        # use_container_width=True hace que el botón ocupe todo el ancho disponible
        if cols[i % 2].button(producto, key=f"btn_{i}", use_container_width=True):
            requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": producto}, headers=HEADERS)
            st.rerun()

st.divider()

# --- MOSTRAR LA LISTA ---
response = requests.get(f"{URL}/rest/v1/lista_compra?order=fecha_creacion.desc", headers=HEADERS)
if response.status_code == 200:
    items = response.json()
    
    st.subheader("📝 Pendientes")
    for item in [i for i in items if not i["comprado"]]:
        # Las casillas de verificación ya son de un solo clic
        if st.checkbox(item["producto"], key=f"pend_{item['id']}"):
            requests.patch(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", json={"comprado": True}, headers=HEADERS)
            st.rerun()
            
    st
