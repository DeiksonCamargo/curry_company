import streamlit as st
from PIL import Image

st.set_page_config(
	page_title="Home",
	page_icon="🎯"
)

#image_path = 'logo.jpg'
image = Image.open( 'logo.jpg' )
st.sidebar.image( image, width=120 )

st.sidebar.markdown( '# Curry Company' )
st.sidebar.markdown( '## Fast Delivery in Town' )
st.sidebar.markdown( """---""" )

st.write( "# Curry Company Growth Dashboard" )

st.markdown(
	"""
	Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
	### Como Utilizar esse Growth Dashboard?
	- Visão Empresa:
		- Visão Gerencia: Métricas gerais de comportamento.
		- Visão Tática: Indicadores semanais de crescimento.
		- Visão Geográfica: Insights de geolocalização.
	- Visão Entregador:
		- Acompanhamento dos indicadores semanais de crescimento.
	- Visão Restaurante:
		- Indicadores semanais de crescimento dos restaurantes.
	### Ask for Help
	- Time de Data Science no Discord
		- @deiksoncamargo
	"""
	)