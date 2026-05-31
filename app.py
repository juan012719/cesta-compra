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

st.title("🛒 Cesta de la Compra")

# --- CREAR LAS DOS PESTAÑAS ---
tab_principal, tab_despensa = st.tabs(["🛒 Comprar", "📦 Mi Despensa"])

# ==========================================
# PESTAÑA 1: LO QUE USAS EN EL SUPERMERCADO
# ==========================================
with tab_principal:
    
    st.subheader("⚡ Añadir rápido")
    # Botones de tu despensa (3 por fila para que quepan bien en el móvil)
    if productos_habituales:
        cols = st.columns(3) 
        for i, prod in enumerate(productos_habituales):
            if cols[i % 3].button(prod, key=f"cat_{i}", use_container_width=True):
                requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": prod}, headers=HEADERS)
                st.rerun()
    
    # Por si un día quieres comprar algo raro que no está en tu despensa
    producto_nuevo = st.text_input("✍️ O escribir algo puntual:")
    if st.button("Añadir a la lista", key="btn_nuevo") and producto_nuevo != "":
        requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": producto_nuevo}, headers=HEADERS)
        st.rerun()

    st.divider()

    # La lista de la compra en sí
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


# ==========================================
# PESTAÑA 2: GESTIÓN DE TU BASE DE DATOS
# ==========================================
with tab_despensa:
    st.subheader("Añadir a mis habituales")
    st.write("Lo que guardes aquí aparecerá como un botón rápido en la pestaña principal.")
    
    nuevo_catalogo = st.text_input("Nombre del producto:")
    if st.button("Guardar en despensa") and nuevo_catalogo != "":
        requests.post(f"{URL}/rest/v1/catalogo", json={"nombre": nuevo_catalogo}, headers=HEADERS)
        st.success(f"¡{nuevo_catalogo} añadido a tu despensa!")
        st.rerun()
        
    st.divider()
    
    st.write("**Tus productos guardados actualmente:**")
    for p in productos_habituales:
        st.markdown(f"- {p}")
