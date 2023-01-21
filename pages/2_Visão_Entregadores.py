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

st.set_page_config( page_title = 'Visão Entregadores', page_icon='🛵', layout='wide' )


#-----------------------------------------------------
#Funcoes
#-----------------------------------------------------

#===============================================
# Funcao Top entregadores ( rapidos e lentos )
#===============================================

def top_delivers( df, top_asc ):
	df1 = ( df.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
				.groupby( ['City', 'Delivery_person_ID'] )
				.mean()
				.sort_values( [ 'City', 'Time_taken(min)'], ascending=top_asc ).reset_index() )

	df_aux01 = df1.loc[df1['City'] == 'Metropolitian', :].head(10)
	df_aux02 = df1.loc[df1['City'] == 'Urban', :].head(10)
	df_aux03 = df1.loc[df1['City'] == 'Semi-Urban', :].head(10)

	df2 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index( drop=True )
				
	return df2

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
st.header( 'Marketplace - Visão Entregadores ' )

#image_path = 'logo.jpg'
image = Image.open( 'logo.jpg' )
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

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial' ,'_' , '_'] )

with tab1:
	with st.container():
		st.title( 'Overall Metrics' )
		
		col1, col2, col3, col4 = st.columns( 4, gap='large' )
		with col1:
			#a maior idade dos entregaodres
			maior_idade = df.loc[:, 'Delivery_person_Age'].max()
			col1.metric( 'Maior de idade', maior_idade )
			
		with col2:
			#a menor idade dos entregadores
			menor_idade = df.loc[:, 'Delivery_person_Age'].min()
			col2.metric( 'Maior de idade', menor_idade )
			
		with col3:
			#a melhor condicao dos veiculos
			melhor_condicao = df.loc[:, 'Vehicle_condition' ].max()
			col3.metric( 'Melhor condição', melhor_condicao )
		
		with col4:
			#a pior condicao dos veiculos
			pior_condicao = df.loc[:, 'Vehicle_condition' ].min()
			col4.metric( 'Pior condição', pior_condicao )
	
	with st.container():
		st.markdown( """___""" )
		st.title( 'Avaliações' )
		
		col1, col2 = st.columns ( 2 )
		with col1:
			# ==========================================
			#      Avaliações medias por entregador
			# ==========================================
			st.markdown( '##### Avaliações medias por entregador' )
			df_avg_ratings_per_deliver = ( df.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
											 .groupby( 'Delivery_person_ID' )
											 .mean()
											 .reset_index() )
			
			#mostrar dataframe
			st.dataframe( df_avg_ratings_per_deliver )
			
		with col2:
			# ==========================================
			#      Avaliações medias por transito
			# ==========================================
			st.markdown( '##### Avaliação media por trânsito' )
			df_avg_std_rating_by_traffic = ( df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
											 .groupby( 'Road_traffic_density' )
											 .agg( { 'Delivery_person_Ratings': ['mean', 'std']} ) )
			
			#mudanca de nome das colunas
			df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']
			
			#reset do index
			df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
			
			#mostrar dataframe
			st.dataframe( df_avg_std_rating_by_traffic )
			
			# ==========================================
			#      Avaliações medias por clima
			# ==========================================
			st.markdown( '##### Avaliação media por clima' )
			df_avg_std_rating_by_weather = ( df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
											 .groupby( 'Weatherconditions' )
											 .agg( { 'Delivery_person_Ratings': ['mean', 'std']} ) )
			
			#mudanca de nome das colunas
			df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']
			
			#reset do index
			df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()
			
			#mostrar dataframe
			st.dataframe( df_avg_std_rating_by_weather )
			
			
			
	with st.container():
		st.markdown( """___""" )
		st.title( 'Velocidade de entrega' )
		
		col1, col2 = st.columns( 2 )
		
		with col1:
			st.markdown( '##### Top entregadores mais rápidos' )
			df2 = top_delivers( df, top_asc=True )
			st.dataframe( df2 )
			
		with col2:
			st.markdown( '##### Top entregadores mais lentos' )
			df2 = top_delivers( df, top_asc=False )
			st.dataframe( df2 )
			
			
