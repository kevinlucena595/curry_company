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
import numpy as np

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

def distance(df1):
    colunas = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
    df1['distance'] = df1.loc[:,colunas].apply( lambda x: 
                                            haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),
                                                        (x['Delivery_location_latitude'],x['Delivery_location_longitude']) ), axis=1 )
    distance_avg = np.round(df1.loc[:,'distance'].mean(), 2)

    return distance_avg

def abg_std_time_delivery(df1, festival, op):
    """
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
            Input:
                - df: Dataframe com os dados necessários para o cálculo
                - 'Time_mean': calcula o tempo médio de entrega
                - 'Time_std': calcula o desvio padrão do tempo de entrega
            Output:
                - df: Dataframe com 2 colunas e 1 linha          '
    """
    df_aux = ( df1.loc[:,['Festival','Time_taken(min)']]
            .groupby('Festival')
            .agg({'Time_taken(min)':['mean', 'std']})
            .reset_index() )
    df_aux.columns = ['Festival','Time_mean', 'Time_std']
    df_aux1 = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2)

    return df_aux1

def avg_std_time_graph(df1):
    df_aux = df1.loc[:,['City','Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean','std']}).reset_index()
    df_aux.columns = ['City','Time_mean','Time_std']

    fig = go.Figure()
    fig.add_trace( go.Bar( name = 'Control',
                            x = df_aux['City'],
                            y = df_aux['Time_mean'],
                            error_y = dict(type = 'data', array = df_aux['Time_std'] ) ) )
    fig.update_layout(barmode = 'group')

    return fig

def avg_time_by_city_pie_graph(df1):
    colunas = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']
    df1['distance'] = df1.loc[:,colunas].apply( lambda x:
                                            haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),
                                                        (x['Delivery_location_latitude'],x['Delivery_location_longitude']) ), axis=1 )

    distance_avg = df1.loc[:, ['City','distance']].groupby( 'City' ).mean().reset_index()
    fig = go.Figure( data=[ go.Pie( labels = distance_avg['City'], values = distance_avg['distance'], pull = [0.05, 0.05, 0.05] )])

    return fig

def avg_std_time_by_city_traffic_density(df1):
    df_aux = df1.loc[:,['City','Road_traffic_density','Time_taken(min)']].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean','std']}).reset_index()
    df_aux.columns = ['City','Road_traffic_density','Time_mean','Time_std']

    fig = px.sunburst(df_aux, path = ['City', 'Road_traffic_density'], values = 'Time_mean',
                    color = 'Time_std', color_continuous_scale='RdBu',
                    color_continuous_midpoint=np.average(df_aux['Time_std'] ) )
    return fig

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

st.markdown("# Market Place - Visão Restaurantes")

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title("Overall Metrics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('###### Entregadores Únicos')
            delivery_unique = len(df1['Delivery_person_ID'].unique())
            st.metric('' , delivery_unique)

        with col2:
            st.markdown('###### Distância Média (km)')
            distance_avg = distance(df1)
            st.metric('', distance_avg)

        with col3:
            st.markdown('###### Tempo Médio de Entrega c/ Festival')
            df_aux = abg_std_time_delivery(df1, festival='Yes', op='Time_mean')
            st.metric('', df_aux)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('###### Desvio Padrão Médio de Entrega c/ Festival')
            df_aux = abg_std_time_delivery(df1, festival='Yes', op='Time_std')
            st.metric('', df_aux)

        with col2:
            st.markdown('###### Tempo Médio de Entrega s/ Festival')
            df_aux = abg_std_time_delivery(df1, festival='No', op='Time_mean')
            st.metric('', df_aux)

        with col3:
            st.markdown('###### Desvio Padrão Médio de Entrega s/ Festival')
            df_aux = abg_std_time_delivery(df1, festival='No', op='Time_std')
            st.metric('', df_aux)

    with st.container():
        st.markdown("""---""")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('#### Tempo Médio e Desvio Padrão por Cidade')
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig, use_container_width = True)

        with col2:
            st.markdown('#### Distribuição da Distância')
            df_aux = ( df1.loc[:,['City','Type_of_order','Time_taken(min)']]
                    .groupby(['City','Type_of_order'])
                    .agg({'Time_taken(min)':['mean','std']})
                    .reset_index() )
            df_aux.columns = ['City','Type_of_order','Time_mean','Time_std']
            st.dataframe(df_aux)

    with st.container():
        st.markdown("""---""")
        st.title("Distribuição do Tempo")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('#### Tempo Médio de Entregadores por Cidade')
            fig = avg_time_by_city_pie_graph(df1)
            st.plotly_chart(fig, use_container_width = True)
            
        with col2:
            st.markdown('#### Tempo Médio e Desvio Padrão por Cidade e Tipo de Tráfego')
            fig = avg_std_time_by_city_traffic_density(df1)
            st.plotly_chart(fig, use_container_width = True)
        
    with st.container():
        st.markdown("""---""")

