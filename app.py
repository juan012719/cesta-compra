import streamlit as st
import requests

st.set_page_config(page_title="Cesta", page_icon="🛒", layout="centered")

# --- CSS MEJORADO PARA MÓVIL ---
st.markdown("""
    <style>
    /* Forzar que los botones de la lista tengan el mismo alto y se alineen */
    div[data-testid="column"] { display: flex; align-items: center; }
    /* Ajustar espacios en móviles */
    .stButton button { width: 100%; height: 50px; }
    </style>
""", unsafe_allow_html=True)

URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

# --- LÓGICA DE DATOS ---
resp_catalogo = requests.get(f"{URL}/rest/v1/catalogo?order=nombre.asc", headers=HEADERS)
productos_habituales = [item["nombre"] for item in resp_catalogo.json()] if resp_catalogo.status_code == 200 else []

response_lista = requests.get(f"{URL}/rest/v1/lista_compra?order=fecha_creacion.desc", headers=HEADERS)
items_lista = response_lista.json() if response_lista.status_code == 200 else []

st.title("🛒 Cesta")
tab_lista, tab_comprar, tab_despensa = st.tabs(["📝 Lista", "➕ Añadir", "📦 Base de datos"])

with tab_lista:
    if st.button("🗑️ Vaciar lista", type="primary"):
        requests.delete(f"{URL}/rest/v1/lista_compra?id=gt.0", headers=HEADERS)
        st.rerun()
        
    st.subheader("Pendientes")
    for item in [i for i in items_lista if not i.get("comprado", False)]:
        # Fila única: 4 partes para producto, 1 parte para borrar
        c1, c2 = st.columns([4, 1])
        if c1.button(f"⬜ {item['producto']}", key=f"p_{item['id']}"):
            requests.patch(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", json={"comprado": True}, headers=HEADERS)
            st.rerun()
        if c2.button("❌", key=f"d_{item['id']}"):
            requests.delete(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", headers=HEADERS)
            st.rerun()

    st.subheader("🛒 En el carro")
    for item in [i for i in items_lista if i.get("comprado", False)]:
        c1, c2 = st.columns([4, 1])
        if c1.button(f"✅ {item['producto']}", key=f"c_{item['id']}"):
            requests.patch(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", json={"comprado": False}, headers=HEADERS)
            st.rerun()
        if c2.button("❌", key=f"x_{item['id']}"):
            requests.delete(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", headers=HEADERS)
            st.rerun()

with tab_comprar:
    cols = st.columns(2)
    for i, prod in enumerate(productos_habituales):
        if cols[i % 2].button(prod):
            requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": prod}, headers=HEADERS)
            st.rerun()

with tab_despensa:
    nuevo = st.text_input("Nombre del producto:")
    if st.button("Guardar en despensa"):
        requests.post(f"{URL}/rest/v1/catalogo", json={"nombre": nuevo}, headers=HEADERS)
        st.rerun()
