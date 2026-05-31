import streamlit as st
import requests

st.set_page_config(page_title="Lista de la Compra", page_icon="🛒")

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

st.subheader("Añadir a la lista")
col1, col2 = st.columns(2)

with col1:
    producto_elegido = st.selectbox("De la despensa:", ["(Elige uno)"] + productos_habituales)
    if st.button("Añadir habitual") and producto_elegido != "(Elige uno)":
        requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": producto_elegido}, headers=HEADERS)
        st.rerun()

with col2:
    producto_nuevo = st.text_input("O algo puntual:")
    if st.button("Añadir puntual") and producto_nuevo != "":
        requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": producto_nuevo}, headers=HEADERS)
        st.rerun()

st.divider()

# --- MOSTRAR LA LISTA ---
response = requests.get(f"{URL}/rest/v1/lista_compra?order=fecha_creacion.desc", headers=HEADERS)
if response.status_code == 200:
    items = response.json()
    
    st.subheader("Pendientes")
    for item in [i for i in items if not i["comprado"]]:
        if st.checkbox(item["producto"], key=f"pend_{item['id']}"):
            requests.patch(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", json={"comprado": True}, headers=HEADERS)
            st.rerun()
            
    st.subheader("En el carro")
    for item in [i for i in items if i["comprado"]]:
        if st.checkbox(item["producto"], value=True, key=f"comp_{item['id']}"):
            requests.patch(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", json={"comprado": False}, headers=HEADERS)
            st.rerun()

st.divider()

# --- GESTIONAR EL CATÁLOGO (NUEVO) ---
with st.expander("⚙️ Gestionar mi base de datos (Catálogo)"):
    nuevo_catalogo = st.text_input("Añadir nuevo producto fijo al catálogo:")
    if st.button("Guardar en despensa") and nuevo_catalogo != "":
        requests.post(f"{URL}/rest/v1/catalogo", json={"nombre": nuevo_catalogo}, headers=HEADERS)
        st.rerun()