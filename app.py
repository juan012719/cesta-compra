import streamlit as st
import requests

st.set_page_config(page_title="Cesta", page_icon="🛒", layout="centered")

# --- CSS AGRESIVO PARA MÓVIL ---
st.markdown("""
    <style>
    /* Forzar que las columnas se mantengan en una sola fila */
    [data-testid="column"] {
        display: flex !important;
        align-items: center !important;
    }
    /* Eliminar márgenes de los botones para que quepan */
    div.stButton > button {
        margin: 0px !important;
        padding: 5px !important;
        height: 40px !important;
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

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

nombres_en_lista = [i["producto"].lower() for i in items_lista if "producto" in i]

st.title("🛒 Cesta")
tab_lista, tab_comprar, tab_despensa = st.tabs(["📝 Lista", "➕ Añadir", "📦 Base de datos"])

# --- PESTAÑA 1: MI LISTA ---
with tab_lista:
    if st.button("🗑️ Vaciar toda la lista", type="primary"):
        requests.delete(f"{URL}/rest/v1/lista_compra?id=gt.0", headers=HEADERS)
        st.rerun()
        
    st.subheader("Pendientes")
    for item in [i for i in items_lista if not i.get("comprado", False)]:
        c1, c2 = st.columns([4, 1])
        if c1.button(f"⬜ {item['producto']}", key=f"pend_{item['id']}"):
            requests.patch(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", json={"comprado": True}, headers=HEADERS)
            st.rerun()
        if c2.button("❌", key=f"del_{item['id']}"):
            requests.delete(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", headers=HEADERS)
            st.rerun()

    st.subheader("🛒 En el carro")
    for item in [i for i in items_lista if i.get("comprado", False)]:
        c1, c2 = st.columns([4, 1])
        if c1.button(f"✅ {item['producto']}", key=f"comp_{item['id']}"):
            requests.patch(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", json={"comprado": False}, headers=HEADERS)
            st.rerun()
        if c2.button("❌", key=f"delc_{item['id']}"):
            requests.delete(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", headers=HEADERS)
            st.rerun()

# --- PESTAÑA 2: AÑADIR ---
with tab_comprar:
    st.subheader("⚡ Añadir rápido")
    if productos_habituales:
        cols = st.columns(2)
        for i, prod in enumerate(productos_habituales):
            ya_esta = prod.lower() in nombres_en_lista
            if cols[i % 2].button(prod, key=f"cat_{i}", disabled=ya_esta):
                requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": prod}, headers=HEADERS)
                st.rerun()
    
    st.divider()
    producto_nuevo = st.text_input("✍️ Producto puntual:")
    if st.button("Añadir a la lista"):
        if producto_nuevo != "":
            requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": producto_nuevo}, headers=HEADERS)
            st.rerun()

# --- PESTAÑA 3: DESPENSA ---
with tab_despensa:
    st.subheader("Gestionar habituales")
    nuevo_catalogo = st.text_input("Nuevo nombre:")
    if st.button("Guardar en despensa"):
        if nuevo_catalogo != "":
            requests.post(f"{URL}/rest/v1/catalogo", json={"nombre": nuevo_catalogo}, headers=HEADERS)
            st.rerun()
    st.divider()
    for p in productos_habituales:
        st.write(f"- {p}")
