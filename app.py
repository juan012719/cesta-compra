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

    st.subheader("📝 Pendientes")
    for item in [i for i in items_lista if not i["comprado"]]:
        # Dividimos la fila: 80% para la casilla, 20% para el botón de borrar
        col_check, col_del = st.columns([8, 2])
        with col_check:
            if st.checkbox(item["producto"], key=f"pend_{item['id']}"):
                requests.patch(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", json={"comprado": True}, headers=HEADERS)
                st.rerun()
        with col_del:
            if st.button("❌", key=f"del_{item['id']}"):
                requests.delete(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", headers=HEADERS)
                st.rerun()

    st.divider()
    
    st.subheader("🛒 En el carro")
    for item in [i for i in items_lista if i["comprado"]]:
        col_check, col_del = st.columns([8, 2])
        with col_check:
            if st.checkbox(item["producto"], value=True, key=f"comp_{item['id']}"):
                requests.patch(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", json={"comprado": False}, headers=HEADERS)
                st.rerun()
        with col_del:
            if st.button("❌", key=f"del_comp_{item['id']}"):
                requests.delete(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", headers=HEADERS)
                st.rerun()

# ==========================================
# PESTAÑA 3: GESTIÓN DE TU BASE DE DATOS
# ==========================================
with tab_despensa:
    st.subheader("Añadir a mis habituales")
    nuevo_catalogo = st.text_input("Nombre del producto:")
    if st.button("Guardar en despensa"):
        if nuevo_catalogo != "":
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
