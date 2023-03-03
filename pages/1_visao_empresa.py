# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessárias
import folium
import pandas as pd
import streamlit as st
from PIL import Image

from streamlit_folium import folium_static


st.set_page_config(page_title='Visão Entregadores', layout='wide')


#------------------------ FUNÇÕES ------------------#
def country_maps(df1):

    cols = ['City','Road_traffic_density', 'Delivery_location_latitude','Delivery_location_longitude']

    df_aux = (df1.loc[:, cols ]
                 .groupby(['City','Road_traffic_density'])
                 .median()
                 .reset_index())

    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                       popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )

    folium_static(map, width=1024, height=600 )
        
def order_share_by_week(df1):
    #Quantidade de pedidos por semana / Número único de entregadores por semana       
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

    df_aux = pd.merge(df_aux01, df_aux02, how='inner', on='week_of_year')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')

    return fig
        
        
def order_by_week(df1):
    #criar a coluna de semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()

    fig = px.line(df_aux, x='week_of_year', y='ID')

    return fig
        
def traffic_order_city(df1):
        df_aux =(df1.loc[:, ['ID','City','Road_traffic_density']]
                    .groupby(['City','Road_traffic_density'])
                    .count()
                    .reset_index())
        
        fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')

        return fig

def traffic_order_share(df1):
    df_aux =(df1.loc[:, ['ID','Road_traffic_density']]
                .groupby('Road_traffic_density')
                .count()
                .reset_index())
    
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

    fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')

    return fig

def order_metric(df1):
    cols = ['ID', 'Order_Date']

    # Selecao de linhas
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()

    # desenhar o gráfico de linhas

    fig = px.bar( df_aux, x='Order_Date', y='ID')

    return fig
        
def clear_code(df1):
    
    """
        Esta função tem a responsábilidade de limpar o dataframe.
        
        Limpeza: 
        1. Remoção dos dados NaN
        2. Remoção dos Espaços
        3. Mudança do tipo da coluna de dados
        4. Formatação da coluna de dadas
        5. Limpeza da coluna de tempo (remoção do texto varável numérica)
        
        input: Dataframe
        output: Dataframe
    """

    # 1. convertando a coluna Age de texto para numero
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['City'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Festival'] != 'NaN ') 
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # 2. convertando a coluna Ratings de texto para numero decimal ( float )
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # 3. convertando a coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )

    # 4. convertendo multiple_deliveries de texto para numero inteiro ( int )
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    ## 5. Removendo os espacos dentro de strings/texto/object
    #df1 = df1.reset_index( drop=True )
    #for i in range( len( df1 ) ):
    #  df1.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()


    # 6. Removendo os espacos dentro de strings/texto/object

    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    # 7. Limpando a coluna de time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)']  = df1['Time_taken(min)'].astype( int )
    
    return df1

# =======================================
# Import dos dados
# =======================================

# Import dataset
df = pd.read_csv( '../datasets/train.csv' )
#limpando os dados

df1 = clear_code(df)

# =======================================
# Barra Lateral
# =======================================
st.header( 'Marketplace - Visão Empresa' )

# image_path = '/Users/meigarom/repos/ftc_programacao_python/logo.png'
# image = Image.open( image_path )
# st.sidebar.image( image, width=120 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider( 
    'Até qual valor?',
    value=pd.datetime( 2022, 4, 13 ),
    min_value=pd.datetime(2022, 2, 11 ),
    max_value=pd.datetime( 2022, 4, 6 ),
    format='DD-MM-YYYY' )

st.sidebar.markdown( """---""" )


traffic_options = st.sidebar.multiselect( 
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'], 
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown( """---""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )

# Filtro de data
linhas_selecionadas = df1['Order_Date'] <  date_slider 
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

# =======================================
# Layout no Streamlit
# =======================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
    with st.container():
        # order metric
        st.markdown('# Orders by Day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():

        col1, col2 = st.columns(2)
        with col1:
            st.header("Trafic Order Share")            
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.header("Trafic Order City")           
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)
    
with tab2:
    with st.container():
        
        st.markdown("# Order by Week")
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, user_container_width=True)       
        
    
with tab3:
    st.markdown("# Contry Maps")
    country_maps(df1)
    
  
