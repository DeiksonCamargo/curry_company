#Libraries

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

#bibliotecas necessárias
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config( page_title = 'Visão Restaurantes', page_icon='🏪', layout='wide' )


#-----------------------------------------------------
#Funcoes
#-----------------------------------------------------
# ==========================================
#        Grafico de pizza da direita
# ==========================================
def avg_std_time_on_traffic( df ):
	df_aux = ( df.loc[:, [ 'City', 'Time_taken(min)', 'Road_traffic_density' ]]
			  .groupby( ['City', 'Road_traffic_density'] )
			  .agg( { 'Time_taken(min)': ['mean', 'std'] } ) )
	df_aux.columns = [ 'avg_time', 'std_time' ]
	df_aux = df_aux.reset_index()

	fig = px.sunburst( df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
					   color='std_time', color_continuous_scale='RdBu', 
					   color_continuous_midpoint=np.average(df_aux['std_time'] ) )

	return fig


# ==========================================
#        Grafico de barras col1
# ==========================================
def avg_std_time_graph( df ):
	df_aux = df.loc[:, [ 'City', 'Time_taken(min)']].groupby( 'City' ).agg( { 'Time_taken(min)': ['mean', 'std'] } )
	df_aux.columns = [ 'avg_time', 'std_time' ]
	df_aux = df_aux.reset_index()

	fig = go.Figure()
	fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))
	fig.update_layout(barmode='group')

	return fig

#======================================================================
# calcula o tempo médio e o desvio padrao do tempo de entrega ( col3 e col4 )
#======================================================================
def avg_std_time_delivery( df, festival, op):
	"""
	Esta funcao calcula o tempo médio e o desvio padrao do tempo de entrega.
	Parametros:
		Input: 
			- df: Dataframe com os dados necessários para o cálculo
			- op: Tipo de operação que precisa ser calculado
				'avg_time': Calcula o tempo médio
				'std_time': Calcula o desvio padrão do tempo
		Output:
			- df: Dataframe com 2 colunas e 1 linha					
	"""
	df_aux = ( df.loc[:, ['Time_taken(min)', 'Festival']]
				 .groupby( 'Festival' )
				 .agg( {'Time_taken(min)': ['mean', 'std']} ) )

	df_aux.columns = [ 'avg_time', 'std_time' ]
	df_aux = df_aux.reset_index()
	df_aux = np.round( df_aux.loc[ df_aux[ 'Festival' ] == festival, op], 2 )

	return df_aux


#================================================================
# Distance havernsine ( col2-layout e col1-grafico de Barras )
#================================================================
def distance( df, fig ):
	if fig == False:
		cols = [ 'Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude' ]
		df['distance'] = df.loc[:, cols].apply( lambda x:
									haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
											   (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ),axis=1 )

		avg_distance = np.round( df['distance'].mean(), 2 )

		return avg_distance
	else:
		cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
		df['distance'] = df.loc[:, cols].apply( lambda x:
									haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
											   (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ),axis=1 )
		
		avg_distance = df.loc[:, ['City', 'distance']].groupby( 'City' ).mean().reset_index()
		fig = go.Figure( data=[ go.Pie( labels=avg_distance[ 'City' ], values=avg_distance['distance'], pull=[0, 0.1, 0])])
		
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



	#for i in range( len( df ) ):
	#   df.loc[i, 'ID'] = df.loc[i, 'ID'].strip()
	#    df.loc[i, 'Delivery_person_ID'] = df.loc[i, 'Delivery_person_ID'].strip()

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

	# Comando para remover o texto de números
	#df = df.reset_index( drop=True )
	#for i in range( len( df ) ):
	#    df.loc[i, 'Time_taken(min)'] = re.findall( r'\d+', df.loc[i, 'Time_taken(min)'] )
	#df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

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
st.header( 'Marketplace - Visão Restaurantes ' )

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
		st.title( "Overal Metrics" )
		
		col1, col2, col3, col4, col5, col6 = st.columns( 6 )
		with col1:
			delivery_unique = len( df.loc[:, 'Delivery_person_ID'].unique() )
			col1.metric( 'Entregadores únicos', delivery_unique )
			
			
		with col2:
			avg_distance = distance( df, fig=False )
			col2.metric( 'A distancia media das entregas', avg_distance )
			
			
		with col3:
			df_aux = avg_std_time_delivery( df, 'Yes', 'avg_time' )
			col3.metric( 'Tempo médio de entrega c/ Festival', df_aux )
			
			
		with col4:
			df_aux = avg_std_time_delivery( df, 'Yes', 'std_time' )
			col4.metric( 'Desvio padrão médio de entrega c/ Festival', df_aux )
			
			
		with col5:
			df_aux = avg_std_time_delivery( df, 'No', 'avg_time' )
			col5.metric( 'Tempo médio de entrega s/ Festival', df_aux )
			
			
		with col6:
			df_aux = avg_std_time_delivery( df, 'No', 'std_time' )
			col6.metric( 'Desvio padrão médio de entrega s/ Festival', df_aux )
			
			
# ==========================================
#             Grafico de barras
# ==========================================
			
	with st.container():
		st.markdown( """___""" )
		col1, col2 = st.columns( 2 )
		
		with col1:			
			fig = avg_std_time_graph( df )
			st.plotly_chart( fig ) 
			
			
		with col2:
			df_aux = ( df.loc[:, [ 'City', 'Time_taken(min)', 'Type_of_order' ]]
						  .groupby( ['City', 'Type_of_order'] )
						  .agg( { 'Time_taken(min)': ['mean', 'std'] } ) )

			df_aux.columns = [ 'avg_time', 'std_time' ]
			df_aux = df_aux.reset_index()

			st.dataframe( df_aux )

# ==========================================
#        criando container na mesma linha
# ==========================================
	with st.container():
		st.markdown( """___""" )
		st.title( "Distribuicao do Tempo" )
		
		col1, col2 = st.columns( 2 )
		
# ==========================================
#        Grafico de pizza da esquerda
# ==========================================
		with col1:
			fig = distance( df, fig=True )
			st.plotly_chart( fig )
			
# ==========================================
#        Grafico de pizza da direita
# ==========================================
		with col2:
			fig = avg_std_time_on_traffic( df )
			st.plotly_chart( fig )
			
