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

# --- DESCARGAR DATOS CON CHIVATO DE ERROR ---
resp_catalogo = requests.get(f"{URL}/rest/v1/catalogo?order=nombre.asc", headers=HEADERS)
if resp_catalogo.status_code == 200:
    productos_habituales = [item["nombre"] for item in resp_catalogo.json()]
else:
    st.error(f"Error al leer catálogo: {resp_catalogo.text}")
    productos_habituales = []

response_lista = requests.get(f"{URL}/rest/v1/lista_compra?order=fecha_creacion.desc", headers=HEADERS)
items_lista = response_lista.json() if response_lista.status_code == 200 else []

st.title("🛒 Cesta de la Compra")

tab_principal, tab_despensa = st.tabs(["🛒 Comprar", "📦 Mi Despensa"])

with tab_principal:
    st.subheader("⚡ Añadir rápido")
    if productos_habituales:
        cols = st.columns(3) 
        for i, prod in enumerate(productos_habituales):
            if cols[i % 3].button(prod, key=f"cat_{i}", use_container_width=True):
                requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": prod}, headers=HEADERS)
                st.rerun()
    
    producto_nuevo = st.text_input("✍️ O escribir algo puntual:")
    if st.button("Añadir a la lista", key="btn_nuevo") and producto_nuevo != "":
        requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": producto_nuevo}, headers=HEADERS)
        st.rerun()

    st.divider()

    st.subheader("📝 Pendientes")
    for item in [i for i in items_lista if not i["comprado"]]:
        if st.checkbox(item["producto"], key=f"pend_{item['id']}"):
            requests.patch(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", json={"comprado": True}, headers=HEADERS)
            st.rerun()

    st.subheader("🛒 En el carro")
    for item in [i for i in items_lista if i["comprado"]]:
        if st.checkbox(item["producto"], value=True, key=f"comp_{item['id']}"):
            requests.patch(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", json={"comprado": False}, headers=HEADERS)
            st.rerun()

with tab_despensa:
    st.subheader("Añadir a mis habituales")
    nuevo_catalogo = st.text_input("Nombre del producto:")
    if st.button("Guardar en despensa"):
        if nuevo_catalogo != "":
            # --- GUARDAR DATOS CON CHIVATO DE ERROR ---
            res = requests.post(f"{URL}/rest/v1/catalogo", json={"nombre": nuevo_catalogo}, headers=HEADERS)
            
            if res.status_code in [200, 201]:
                st.success(f"¡{nuevo_catalogo} añadido a tu despensa!")
                st.rerun()
            else:
                st.error(f"Error al guardar: {res.text}")
        
    st.divider()
    st.write("**Tus productos guardados:**")
    for p in productos_habituales:
        st.markdown(f"- {p}")
