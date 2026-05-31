import streamlit as st
import requests

# Configuración de página
st.set_page_config(page_title="Cesta", page_icon="🛒", layout="centered")

URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- LÓGICA DE DATOS ---
resp_catalogo = requests.get(f"{URL}/rest/v1/catalogo?order=nombre.asc", headers=HEADERS)
productos_habituales = [item["nombre"] for item in resp_catalogo.json()] if resp_catalogo.status_code == 200 else []

response_lista = requests.get(f"{URL}/rest/v1/lista_compra?order=fecha_creacion.desc", headers=HEADERS)
items_lista = response_lista.json() if response_lista.status_code == 200 else []

st.title("🛒 Cesta de la Compra")

tab_lista, tab_comprar, tab_despensa = st.tabs(["📝 Lista", "➕ Añadir", "📦 Base de datos"])

# --- PESTAÑA 1: MI LISTA ---
with tab_lista:
    if st.button("🗑️ Vaciar carro completo", type="primary", use_container_width=True):
        # Borra solo los marcados como comprados (true)
        requests.delete(f"{URL}/rest/v1/lista_compra?comprado=eq.true", headers=HEADERS)
        st.rerun()
        
    st.subheader("Pendientes")
    for item in [i for i in items_lista if not i.get("comprado", False)]:
        # Al quitar la X, el botón ocupa todo el ancho y no hay riesgo de saltos
        if st.button(f"⬜ {item['producto']}", key=f"pend_{item['id']}", use_container_width=True):
            requests.patch(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", json={"comprado": True}, headers=HEADERS)
            st.rerun()

    st.subheader("🛒 En el carro")
    for item in [i for i in items_lista if i.get("comprado", False)]:
        if st.button(f"✅ {item['producto']}", key=f"comp_{item['id']}", use_container_width=True):
            requests.patch(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", json={"comprado": False}, headers=HEADERS)
            st.rerun()

# --- PESTAÑA 2: AÑADIR ---
with tab_comprar:
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

# --- PESTAÑA 3: DESPENSA ---
with tab_despensa:
    st.subheader("Gestionar habituales")
    nuevo_catalogo = st.text_input("Nombre del producto:")
    if st.button("Guardar en despensa", use_container_width=True):
        if nuevo_catalogo != "":
            requests.post(f"{URL}/rest/v1/catalogo", json={"nombre": nuevo_catalogo}, headers=HEADERS)
            st.rerun()
    st.divider()
    for p in productos_habituales:
        st.write(f"- {p}")
