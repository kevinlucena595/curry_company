import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='⚡️🔥',
    layout='wide'
)

#st.set_page_config( page_title='Visão Empresa', layout='wide')

# ============================================================================
# BARRA LATERAL
# ============================================================================

#image_path = r'C:\Users\kevin\OneDrive\Documentos\repos\FTC_analisando_dados_com_python\logo.png'
image = Image.open('logo.png')
st.sidebar.image (image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento
        - Visão Tática: Indicadores semanais de crescimento
        - Visão Geográfica: Insights de geolocalização
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Kevin Lucena
""" )