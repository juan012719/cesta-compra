import streamlit as st
import requests

st.set_page_config(page_title="Cesta", page_icon="🛒", layout="centered")

# CSS limpio: solo oculta la barra de arriba, sin tocar los botones
st.markdown("""
    <style>
    header {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    </style>
""", unsafe_allow_html=True)

URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}

CATEGORIAS = ["🍏 Frutería/Verdura", "🥩 Carne/Pescado", "🥛 Lácteos/Frío", "🥫 Despensa", "🧼 Limpieza/Baño", "📦 Otros"]

# --- DATOS ---
resp_catalogo = requests.get(f"{URL}/rest/v1/catalogo", headers=HEADERS)
catalogo_items = resp_catalogo.json() if resp_catalogo.status_code == 200 else []

response_lista = requests.get(f"{URL}/rest/v1/lista_compra?order=fecha_creacion.desc", headers=HEADERS)
items_lista = response_lista.json() if response_lista.status_code == 200 else []

nombres_en_lista = [i.get("producto", "").lower() for i in items_lista]

st.title("🛒 Cesta")

tab_lista, tab_añadir, tab_despensa = st.tabs(["📝 Lista", "➕ Añadir", "⚙️ Despensa"])

# ==========================================
# PESTAÑA 1: LISTA
# ==========================================
with tab_lista:
    c1, c2 = st.columns(2)
    if c1.button("🗑️ Vaciar Carro (✅)", type="primary", use_container_width=True):
        requests.delete(f"{URL}/rest/v1/lista_compra?comprado=eq.true", headers=HEADERS)
        st.rerun()
    if c2.button("⚠️ Vaciar TODA la lista", use_container_width=True):
        requests.delete(f"{URL}/rest/v1/lista_compra?id=not.is.null", headers=HEADERS)
        st.rerun()
        
    st.subheader("Pendientes")
    pendientes = [i for i in items_lista if not i.get("comprado", False)]
    if not pendientes:
        st.write("Nada pendiente.")
    for item in pendientes:
        if st.button(f"⬜ {item.get('producto', '')}", key=f"p_{item['id']}", use_container_width=True):
            requests.patch(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", json={"comprado": True}, headers=HEADERS)
            st.rerun()

    st.subheader("🛒 En el carro")
    comprados = [i for i in items_lista if i.get("comprado", False)]
    for item in comprados:
        if st.button(f"✅ {item.get('producto', '')}", key=f"c_{item['id']}", use_container_width=True):
            requests.patch(f"{URL}/rest/v1/lista_compra?id=eq.{item['id']}", json={"comprado": False}, headers=HEADERS)
            st.rerun()

# ==========================================
# PESTAÑA 2: AÑADIR (AGRUPADO)
# ==========================================
with tab_añadir:
    st.subheader("Habituales por zona")
    productos_por_cat = {cat: [] for cat in CATEGORIAS}
    
    for item in catalogo_items:
        cat = item.get("categoria")
        if cat not in productos_por_cat:
            cat = "📦 Otros"
        productos_por_cat[cat].append(item)
        
    for cat in CATEGORIAS:
        if productos_por_cat[cat]: 
            with st.expander(cat, expanded=True):
                cols = st.columns(2)
                for i, item in enumerate(productos_por_cat[cat]):
                    prod = item.get("nombre", "")
                    ya_esta = prod.lower() in nombres_en_lista
                    if cols[i % 2].button(prod, key=f"add_{item.get('id', i)}", disabled=ya_esta, use_container_width=True):
                        requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": prod, "comprado": False}, headers=HEADERS)
                        st.rerun()
    
    st.divider()
    st.subheader("Puntual")
    producto_nuevo = st.text_input("Escribe el nombre:", label_visibility="collapsed", placeholder="Ej: Pilas AA")
    if st.button("➕ Añadir a la lista", use_container_width=True):
        if producto_nuevo and producto_nuevo.lower() not in nombres_en_lista:
            requests.post(f"{URL}/rest/v1/lista_compra", json={"producto": producto_nuevo, "comprado": False}, headers=HEADERS)
            st.rerun()

# ==========================================
# PESTAÑA 3: DESPENSA
# ==========================================
with tab_despensa:
    st.subheader("Guardar nuevo habitual")
    nuevo_nom = st.text_input("Nombre:", label_visibility="collapsed", placeholder="Ej: Huevos XL", key="nuevo_habitual")
    nuevo_cat = st.selectbox("Elige la zona del súper:", CATEGORIAS)
    
    if st.button("💾 Añadir a despensa", use_container_width=True):
        if nuevo_nom:
            requests.post(f"{URL}/rest/v1/catalogo", json={"nombre": nuevo_nom, "categoria": nuevo_cat}, headers=HEADERS)
            st.rerun()
            
    st.divider()
    st.subheader("Tus productos habituales")
    
    for i, item in enumerate(catalogo_items):
        c1, c2 = st.columns([4, 1])
        cat_display = item.get("categoria", "📦 Otros")
        c1.markdown(f"<div style='margin-top:10px;'><b>{item.get('nombre', '')}</b> <span style='color:gray; font-size:12px'>({cat_display})</span></div>", unsafe_allow_html=True)
        if c2.button("❌", key=f"rm_{item.get('id', i)}"):
            requests.delete(f"{URL}/rest/v1/catalogo?id=eq.{item['id']}", headers=HEADERS)
            st.rerun()
