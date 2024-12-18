# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessárias
import pandas as pd
import folium
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', layout='wide')

# ============================================================================
# Funções
# ============================================================================
def clean_code(df1):
    """" Esta função tem a responsabilidade de limpar o dataframe

        Tipos de Limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)

    Input: Dataframe
    Output: Dataframe
    """
    # 1. convertendo a coluna Age para numero
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # 2. tirando os 'NaN ' da coluna Road_traffic_density
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # 3. tirando os 'NaN ' da coluna City
    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # 4. tirando os 'NaN ' da coluna Festival
    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    # 5. convertendo Ratings de texto para numero decimal (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # 6. convertendo Order_Date de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )

    # 7. convertendo multiple_deliveries para numero inteiro
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    # 5. removendo os espacos dentro de string/texto/object
    #df1 = df1.reset_index( drop=True )
    #for i in range( len(df1) ):
    #   df1.loc[i, 'ID' ] = df1.loc[i, 'ID' ].strip()

    # 8. removendo os espacos dentro de string/texto/object
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    # 9. limpando a coluna de Time_taken(min)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] ).astype(int)

    return df1

def order_metric(df1):
    cols = ['ID','Order_Date']

    #contagem de IDs por data agrupada
    df_aux = df1.loc[:,cols].groupby('Order_Date').count().reset_index()

    #desenhar gráfico de linhas
    fig = px.bar(df_aux, x='Order_Date', y='ID')

    return fig

def traffic_order_share(df1):
    df_aux =( df1.loc[:,['ID','Road_traffic_density']]
             .groupby('Road_traffic_density')
             .count()
             .reset_index() )
    
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN',:]
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

    fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')

    return fig

def traffic_order_city(df1):
    df_aux = ( df1.loc[:,['ID','City','Road_traffic_density']]
              .groupby(['City','Road_traffic_density'])
              .count()
              .reset_index() )
    
    fig = px.scatter(df_aux, x = 'City', y = 'Road_traffic_density', size = 'ID', color = 'City')

    return fig

def order_by_week(df1):
    #criar coluna da semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )

    df_aux = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()

    fig = px.line(df_aux, x='week_of_year', y='ID')

    return fig

def order_share_by_week(df1):
    df_aux1 = ( df1.loc[:,['ID','week_of_year']]
               .groupby('week_of_year')
               .count()
               .reset_index() )

    df_aux2 = ( df1.loc[:,['Delivery_person_ID','week_of_year']]
               .groupby('week_of_year')
               .nunique()
               .reset_index() )

    df_aux = pd.merge(df_aux1, df_aux2, how='inner')

    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')

    return fig

def country_maps(df1):
    cols = ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
    df_aux = ( df1.loc[:,cols]
            .groupby(['City','Road_traffic_density'])
            .median()
            .reset_index() )

    #Pegamos a mediana pq a média muda o número, já a mediana pega número que estão dentro do conjunto de dados (se for impar pega exatamente o valor, se for par pega a média dos dois centrais)

    df_aux = df_aux.loc[df_aux['City'] != 'NaN',:]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN',:]

    map = folium.Map()

    #for i in range( len(df_aux) ):   - O marker não funciona desse jeito
    for index,location_info in df_aux.iterrows():
    #folium.Marker(location=[df_aux.loc[i,'Delivery_location_latitude'],df_aux.loc[i,'Delivery_location_longitude']]).add_to(map)
        folium.Marker( [location_info['Delivery_location_latitude'],
                    location_info['Delivery_location_longitude']],
                    popup = location_info[['City', 'Road_traffic_density']]).add_to(map)

    folium_static(map, width = 1024, height = 600)

    




#============================== Início da Estrutura Lógica do Código ==============================
# =============================
# import dataset
# =============================
df = pd.read_csv( 'dataset/train.csv' )
df1 = df.copy()

# =============================
# Limpando os Dados
# =============================
df1 = clean_code( df )

# ============================================================================
# BARRA LATERAL
# ============================================================================

#image_path = r'C:\Users\kevin\OneDrive\Documentos\repos\FTC_analisando_dados_com_python\logo.png'
image = Image.open('logo.png')
st.sidebar.image (image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.to_datetime('2022-04-05').date(),  # Corrigido para uma data entre min e max
    min_value=pd.to_datetime('2022-02-11').date(),
    max_value=pd.to_datetime('2022-04-13').date(),  # Corrigido para ser maior que o min_value
    format='DD-MM-YYYY'  # Corrigido para o formato adequado
)

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

#Filtro de data
linhas_selecionadas = df1['Order_Date'] <= pd.to_datetime(date_slider)
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de trânsico
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# ============================================================================
# LAYOUT
# ============================================================================

st.markdown("# Market Place - Visão Empresa")

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order Metric    
        fig = order_metric(df1)
        st.markdown('# Orders by Day')
        st.plotly_chart(fig, use_container_width = True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic Order Share')
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width = True)

        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width = True)
            
with tab2:
    with st.container():
        st.markdown('# Orders by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width = True)

    with st.container():
        st.header('Orders by Deliver by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width = True)

with tab3:
    st.markdown('# Country Maps')
    country_maps(df1)
