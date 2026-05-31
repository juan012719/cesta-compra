import streamlit as st
import requests

st.set_page_config(page_title="Cesta", page_icon="🛒", layout="centered")

URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

st.title("🛒 Cesta")

# Pestañas claramente separadas para que no interfieran
tab_lista, tab_añadir, tab_despensa = st.tabs(["📝 Lista", "➕ Añadir", "📦 Base de datos"])

# --- PESTAÑA 1: LISTA ---
with tab_lista:
    st.subheader("Pendientes")
    response_lista = requests.get(f"{URL}/rest/v1/lista_compra?order=fecha_creacion.desc", headers=HEADERS)
    items_lista = response_lista.json() if response_lista.status_code == 200 else []
    
    for item in items_lista:
        if st.button(f"🛒 {item['producto']}", key=f"del_{item['id']}", use_container_width=True):
            requests.delete(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", headers=HEADERS)
            st.rerun()

    if st.button("🗑️ Vaciar TODA la lista", type="primary", use_container_width=True):
        # BORRAMOS DE FORMA SEGURA: solo la tabla lista_compra
        requests.delete(f"{URL}/rest/v1/lista_compra?id=not.is.null", headers=HEADERS)
        st.rerun()

# --- PESTAÑA 2: AÑADIR ---
with tab_añadir:
    resp_catalogo = requests.get(f"{URL}/rest/v1/catalogo?order=nombre.asc", headers=HEADERS)
    productos_habituales = [item["nombre"] for item in resp_catalogo.json()] if resp_catalogo.status_code == 200 else []
    
    cols = st.columns(2)
    for i, prod in enumerate(productos_habituales):
        if cols[i % 2].button(prod, key=f"cat_{i}", use_container_width=True):
            requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": prod}, headers=HEADERS)
            st.rerun()

# --- PESTAÑA 3: BASE DE DATOS ---
with tab_despensa:
    nuevo = st.text_input("Nuevo producto fijo:")
    if st.button("Guardar en despensa", use_container_width=True):
        requests.post(f"{URL}/rest/v1/catalogo", json={"nombre": nuevo}, headers=HEADERS)
        st.rerun()
