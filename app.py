import streamlit as st
import requests

st.set_page_config(page_title="Cesta", page_icon="🛒", layout="centered")

URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

HEADERS = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- DESCARGAR DATOS ---
resp_catalogo = requests.get(f"{URL}/rest/v1/catalogo?order=nombre.asc", headers=HEADERS)
productos_habituales = [item["nombre"] for item in resp_catalogo.json()] if resp_catalogo.status_code == 200 else []

response_lista = requests.get(f"{URL}/rest/v1/lista_compra?order=fecha_creacion.desc", headers=HEADERS)
items_lista = response_lista.json() if response_lista.status_code == 200 else []

# Creamos una lista invisible con los nombres en minúsculas para detectar duplicados
nombres_en_lista = [i["producto"].lower() for i in items_lista]

st.title("🛒 Cesta de la Compra")

# --- TRES PESTAÑAS ---
tab_comprar, tab_lista, tab_despensa = st.tabs(["➕ Añadir", "📝 Mi Lista", "📦 Despensa"])

# ==========================================
# PESTAÑA 1: AÑADIR AL CARRO
# ==========================================
with tab_comprar:
    st.subheader("⚡ Añadir rápido")
    if productos_habituales:
        cols = st.columns(3) 
        for i, prod in enumerate(productos_habituales):
            # Comprobamos si el producto ya está en la lista de la compra
            ya_esta_añadido = prod.lower() in nombres_en_lista
            
            # El botón se desactiva (disabled) si ya está en la lista
            if cols[i % 3].button(prod, key=f"cat_{i}", disabled=ya_esta_añadido, use_container_width=True):
                requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": prod}, headers=HEADERS)
                st.rerun()
    
    st.divider()
    producto_nuevo = st.text_input("✍️ O escribir algo puntual:")
    if st.button("Añadir a la lista", key="btn_nuevo"):
        if producto_nuevo != "":
            # Evitar duplicados por texto
            if producto_nuevo.lower() in nombres_en_lista:
                st.warning(f"¡{producto_nuevo} ya está en tu lista!")
            else:
                requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": producto_nuevo}, headers=HEADERS)
                st.rerun()

# ==========================================
# PESTAÑA 2: LA LISTA DEL SUPERMERCADO
# ==========================================
with tab_lista:
    # Botón gigante para limpiar todo cuando termines de comprar
    if st.button("🗑️ Vaciar toda la lista", type="primary", use_container_width=True):
        # Esta orden borra todos los registros de la lista de la compra
        requests.delete(f"{URL}/rest/v1/lista_compra?id=gt.0", headers=HEADERS)
        st.rerun()
        
    st.divider()

    st.
