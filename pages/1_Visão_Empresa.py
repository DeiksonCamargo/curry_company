#Libraries

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

#bibliotecas necessárias
import pandas as pd
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config( page_title = 'Visão Empresa', page_icon='📊', layout='wide' )

#-----------------------------------------------------
#Funcoes
#-----------------------------------------------------

#==========================================
# tabcontainer 03 "MAP"
#==========================================
def country_maps ( df ):
	cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
	df_aux = ( df.loc[:, cols]
			  .groupby( ['City', 'Road_traffic_density'])
			  .median()
			  .reset_index() )
	#removendo linhas 'NaN'
	df_aux = df_aux.loc[df_aux['City'] != "NaN", :]
	df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN']

	map = folium.Map()

	#laço para percorrer as latitudes e longitudes e gerar pinos no mapa
	for index, location_info in df_aux.iterrows():
		folium.Marker( [location_info['Delivery_location_latitude'],
							location_info['Delivery_location_longitude']],
							popup=location_info[['City', 'Road_traffic_density']]).add_to(map)

	folium_static( map, width=1024, height=600 )

#==========================================
# tabcontainer 02 "ORDER_SHARE_BY_WEEK"
#==========================================
def order_share_by_week ( df ):
	#Quantidade de pedidos por semana / número único de entregadores por semana
	df_aux01 = ( df.loc[:, ['ID', 'week_of_year']]
				.groupby( 'week_of_year')
				.count()
				.reset_index() )
	df_aux02 = ( df.loc[:, ['Delivery_person_ID', 'week_of_year']]
				.groupby( 'week_of_year' )
				.nunique()
				.reset_index() )
	df_aux = pd.merge( df_aux01, df_aux02, how='inner' )
	df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']

	fig = px.line(df_aux, x='week_of_year', y='order_by_delivery' )
			
	return fig

#===================================
# tabcontainer 02 "ORDER_BY_WEEK"
#===================================
def order_by_week( df ):
#criar a coluna de semana
#comando importante para transformar lista em datas '.dt.strftime ('%U')' para dias que iniciam em domingo ('%W') dias iniciam na segunda
	df['week_of_year'] = df['Order_Date'].dt.strftime( '%U')
	df_aux = df.loc[: , ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
	df_aux.head()
	fig = px.line( df_aux, x='week_of_year', y='ID' )

	return fig

#===================================
# tabcontainer 01 "ORDER_CITY"
#===================================
def traffic_order_city( df ):
	df_aux = ( df.loc[:, ['ID', 'City', 'Road_traffic_density']]
				  .groupby( ['City', 'Road_traffic_density'] )
				  .count()
				  .reset_index() )
	#removendo linhas 'NaN'
	df_aux = df_aux.loc[df_aux['City'] != "NaN", :]
	df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN']

	fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City' )
	
	return fig

#===================================
# tabcontainer 01 "ORDER_SHARE"
#===================================
def traffic_order_share( df ):
	df_aux = ( df.loc[:, ['ID', 'Road_traffic_density']]
				  .groupby( 'Road_traffic_density' )
				  .count()
				  .reset_index() )
	#removendo linhas 'NaN'
	df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN", :]
	df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

	fig = px.pie( df_aux, values='entregas_perc', names='Road_traffic_density' )

	return fig

#===================================
# tabcontainer 01 "ORDER_METRIC"
#===================================
def order_metric( df ):
	#colunas
	cols = ['ID', 'Order_Date']
	#selecao de linhas
	df_aux = df.loc[:, cols].groupby( 'Order_Date' ).count().reset_index()
	#desenhar grafico de linhas
	fig = px.bar( df_aux, x='Order_Date', y='ID' )
	
	return fig

#=====================
# Limpeza dataframe
#=====================
def clean_code( df ):
	""" Esta funcao tem a responsabilidade de limpar o dataframe
	
		Tipos de limpeza:
		1. Remocao dos dados NaN
		2. Mudanca do tipo de coluna de dados
		3. Remocao dos espacos das variaveis de texto
		4. Formatacao da coluna de datas
		5. Limpeza da coluna de tempo( remocao do texto da variavel numerica )
		
		Input: Dataframe
		Output: Dataframe
	"""
	# Remover espaco da string/texto/object
	df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
	df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
	df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
	df.loc[:, 'Tipe_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
	df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
	df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()


	# Excluir as linhas com a idade dos entregadores vazia
	# ( Conceitos de seleção condicional )
	linhas_vazias = df['Delivery_person_Age'] != 'NaN '
	df = df.loc[linhas_vazias, :]

	# Conversao de texto/categoria/string para numeros inteiros
	df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )

	# Conversao de texto/categoria/strings para numeros decimais
	df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )

	# Conversao de texto para data
	df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

	# Remove as linhas da coluna multiple_deliveries que tenham o 
	# conteudo igual a 'NaN '
	linhas_vazias = df['multiple_deliveries'] != 'NaN '
	df = df.loc[linhas_vazias, :]
	df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

	linhas_selecionadas = (df['City'] != 'NaN')
	df = df.loc[linhas_selecionadas, :].copy()

	linhas_selecionadas = (df['Festival'] != 'NaN')
	df = df.loc[linhas_selecionadas, :].copy()

	linhas_selecionadas = (df['Road_traffic_density'] != 'NaN')
	df = df.loc[linhas_selecionadas, :].copy()


	#limpando a coluna de time taken
	df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split( '(min)' )[1] )
	df['Time_taken(min)'] = df['Time_taken(min)'].astype( int )

	return df
#-----------------------------Inicio do codigo------------------------------
#------------------------------
#Importar dataset
#------------------------------
df_raw = pd.read_csv( 'dataset/train.csv' )

#Limpando os dados
df = clean_code( df_raw )

# ==========================================
#            Barra Lateral
# ==========================================
st.header( 'Marketplace - Visão Cliente ' )

image_path = 'logo.jpg'
image = Image.open( image_path )
st.sidebar.image( image, width=120 )

st.sidebar.markdown( '# Curry Company' )
st.sidebar.markdown( '## Fast Delivery in Town' )
st.sidebar.markdown( """---""" )

st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime( 2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY' )

st.sidebar.markdown( """---""" )


traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default= ['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown( """---""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )

#Filtro de data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

#Filtro de transito
linhas_selecionadas = df[ 'Road_traffic_density' ].isin( traffic_options )
df = df.loc[linhas_selecionadas, :]

# ==========================================
#             Layout no Streamlit
# ==========================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial' ,'Visão Tática' , 'Visão Geográfica'] )

with tab1:
	with st.container():
		st.markdown( '# Orders by Day' )
		fig = order_metric( df )
		st.plotly_chart( fig, use_container_width=True )

		
	with st.container():
		col1, col2 = st.columns( 2 )
		
		with col1:
			fig = traffic_order_share( df )
			st.header( "Traffic Order Share" )
			st.plotly_chart( fig, use_container_width=True )
			
		with col2:
			fig = traffic_order_city ( df )
			st.header( "Traffic Order City" )
			st.plotly_chart( fig, use_container_width=True )

with tab2:
	with st.container():
		fig = order_by_week ( df )
		st.markdown(" # Order by Week")
		st.plotly_chart( fig, use_container_width=True )

		
	
	with st.container():
		st.markdown( " # Order Share by Week" )
		fig = order_share_by_week ( df )
		st.plotly_chart( fig, use_container_width=True )

		
with tab3:
	st.markdown("# Country maps")
	country_maps ( df )

	
