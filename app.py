import streamlit as st
import requests

st.set_page_config(page_title="Cesta", page_icon="🛒", layout="centered")

URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

# --- LÓGICA DE DATOS ---
resp_catalogo = requests.get(f"{URL}/rest/v1/catalogo?order=nombre.asc", headers=HEADERS)
productos_habituales = [item["nombre"] for item in resp_catalogo.json()] if resp_catalogo.status_code == 200 else []

response_lista = requests.get(f"{URL}/rest/v1/lista_compra?order=fecha_creacion.desc", headers=HEADERS)
items_lista = response_lista.json() if response_lista.status_code == 200 else []

# Lista de nombres que ya están en la cesta (para evitar duplicados)
nombres_en_lista = [i["producto"].lower() for i in items_lista]

st.title("🛒 Cesta")

tab_lista, tab_añadir, tab_despensa = st.tabs(["📝 Lista", "➕ Añadir", "📦 Base de datos"])

# --- PESTAÑA 1: LISTA ---
with tab_lista:
    if st.button("🗑️ Vaciar lista", type="primary", use_container_width=True):
        requests.delete(f"{URL}/rest/v1/lista_compra?id=not.is.null", headers=HEADERS)
        st.rerun()
        
    st.subheader("Pendientes")
    for item in [i for i in items_lista if not i.get("comprado", False)]:
        if st.button(f"⬜ {item['producto']}", key=f"p_{item['id']}", use_container_width=True):
            requests.patch(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", json={"comprado": True}, headers=HEADERS)
            st.rerun()

    st.subheader("🛒 En el carro")
    for item in [i for i in items_lista if i.get("comprado", False)]:
        if st.button(f"✅ {item['producto']}", key=f"c_{item['id']}", use_container_width=True):
            requests.patch(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", json={"comprado": False}, headers=HEADERS)
            st.rerun()

# --- PESTAÑA 2: AÑADIR (CON CONTROL DE DUPLICADOS) ---
with tab_añadir:
    st.subheader("⚡ Añadir rápido")
    cols = st.columns(2)
    for i, prod in enumerate(productos_habituales):
        ya_esta = prod.lower() in nombres_en_lista
        if cols[i % 2].button(prod, key=f"cat_{i}", disabled=ya_esta, use_container_width=True):
            requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": prod, "comprado": False}, headers=HEADERS)
            st.rerun()
    
    st.divider()
    st.subheader("✍️ Producto puntual")
    producto_nuevo = st.text_input("Escribe el nombre:")
    if st.button("Añadir producto", use_container_width=True):
        if producto_nuevo != "":
            if producto_nuevo.lower() in nombres_en_lista:
                st.warning(f"¡{producto_nuevo} ya está en tu lista!")
            else:
                requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": producto_nuevo, "comprado": False}, headers=HEADERS)
                st.rerun()

# --- PESTAÑA 3: BASE DE DATOS ---
with tab_despensa:
    st.subheader("Guardar nuevo habitual")
    nuevo = st.text_input("Nombre:")
    if st.button("Guardar en despensa", use_container_width=True):
        if nuevo != "":
            requests.post(f"{URL}/rest/v1/catalogo", json={"nombre": nuevo}, headers=HEADERS)
            st.rerun()
