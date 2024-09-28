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

def top_delivers(df1, top_asc):

    df_aux1 = ( df1.loc[:,['Time_taken(min)','City','Delivery_person_ID']]
            .groupby(['City','Delivery_person_ID'])
            .mean()
            .sort_values(['City', 'Time_taken(min)'], ascending = top_asc)
            .reset_index() )
    df_aux1 = df_aux1.loc[df_aux1['City'] != 'NaN',:]
    df_aux2 = df_aux1.loc[:,:].groupby('City').head(10)

    return df_aux2

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

st.markdown("# Market Place - Visão Entregadores")

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title("Overall Metrics")
        col1, col2, col3, col4 = st.columns(4, gap = 'large')
        with col1:
            #A maior idade dos entregadores
            #st.markdown('#### Maior Idade')
            idade_max = df1['Delivery_person_Age'].max()
            st.metric('Maior Idade', idade_max)

        with col2:
            #A menor idade dos entregadores
            #st.markdown('#### Menor Idade')
            idade_min = df1['Delivery_person_Age'].min()
            st.metric('Menor Idade', idade_min)

        with col3:
            #A melhor condição de veículos
            #st.markdown('#### Maior Condição de Veículos')
            condicao_veiculo_max = df1['Vehicle_condition'].max()
            st.metric('Melhor Condição', condicao_veiculo_max)

        with col4:
            #A pior condição de veículos
            #st.markdown('#### Pior Condição de Veículos')
            condicao_veiculo_min = df1['Vehicle_condition'].min()
            st.metric('Pior Condição', condicao_veiculo_min)

    with st.container():
        st.markdown("---")
        st.title('Avaliações')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliações Médias por Entregador')
            df_aux = ( df1.loc[:,['Delivery_person_Ratings','Delivery_person_ID']]
                      .groupby('Delivery_person_ID')
                      .mean()
                      .reset_index() )
            st.dataframe(df_aux)


        with col2:
            st.markdown('##### Avaliação Média por Trânsito')
            df_avg_std_rating_by_traffic =( df1.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                                           .groupby('Road_traffic_density')
                                           .agg({'Delivery_person_Ratings': ['mean','std']})
                                           .reset_index() )
            df_avg_std_rating_by_traffic.columns = ['Road_traffic_density','Delivery_mean','Delivery_std']
            st.dataframe(df_avg_std_rating_by_traffic)

            st.markdown('##### Avaliação Média por Clima')
            df_avg_std_rating_by_weather =( df1.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                                           .groupby('Weatherconditions')
                                           .agg({'Delivery_person_Ratings': ['mean','std']})
                                           .reset_index() )
            df_avg_std_rating_by_weather.columns = ['Weatherconditions','Delivery_mean','Delivery_std']
            st.dataframe(df_avg_std_rating_by_weather)

    with st.container():
        st.markdown('---')
        st.title('Velocidade de Entrega')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top Entregadores mais Rápidos')
            df_aux = top_delivers(df1,top_asc=True)
            st.dataframe(df_aux)


        with col2:
            st.markdown('##### Top Entregadores mais Lentos')
            df_aux = top_delivers(df1,top_asc=False)
            st.dataframe(df_aux)
