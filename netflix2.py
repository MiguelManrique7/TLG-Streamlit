
# Se importan las librerias
import streamlit as st
import pandas as pd
# import firebase_admin
# from firebase_admin import credentials, firestore
from google.cloud import firestore
from google.oauth2 import service_account
import json

# Header del Dashboard
st.header("Netflix App")
st.write("Aquí puedes visualizar y filtrar películas.")

key_dict=json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)

# Función para obtener datos de Firestore y crear el DataFrame
def obtener_datos_firestore():
    # Obtiene la referencia a la colección 'movies'
    movies_ref = list(db.collection(u'movies').stream())
    movies_dict =  list(map(lambda x: x.to_dict(), movies_ref))
    movies_df = pd.DataFrame(movies_dict)

    return movies_df

# Cache
@st.cache_data
def load_data():
    data = obtener_datos_firestore()
    return data

# Llama a la función para obtener datos y crea el DataFrame
df = load_data()

# Sidebar
st.sidebar.header("Operaciones")

# Mostrar todos los filmes en un checkbox
mostrar_todos = st.sidebar.checkbox("Mostrar todos los filmes")
if mostrar_todos:
    st.subheader("Todos las películas")
    st.dataframe(df)

# Búsqueda por título
st.sidebar.subheader("Buscar por título")
titulo_buscar = st.sidebar.text_input("Ingrese el título:")
if st.sidebar.button("Buscar"):
    df_resultado_titulo = df[df['name'].str.contains(titulo_buscar, case=False)]
    st.write(f"Total de películas encontradas para {titulo_buscar}: {len(df_resultado_titulo)}")
    st.dataframe(df_resultado_titulo)


# Filtro por director
st.sidebar.subheader("Filtrar por director")
director_seleccionado = st.sidebar.selectbox("Seleccione el director:", df['director'].unique())
if st.sidebar.button("Filtrar por Director"):
    df_resultado_director = df[df['director'] == director_seleccionado]
    st.write(f"Total de películas  encontradas para {director_seleccionado}: {len(df_resultado_director)}")
    st.write(df_resultado_director)

# Formulario para insertar nueva película
st.sidebar.subheader("Insertar nuevo filme")
new_name= st.sidebar.text_input("Name:")
new_company = st.sidebar.text_input("Company:")
new_director = st.sidebar.text_input("Director:")
new_genre = st.sidebar.selectbox("Genre:", df['genre'].unique())

db = firestore.Client.from_service_account_json('keys.json')

# sumbit = st.sidebar.button("Crear nuevo registro")

# # Una vez cargada la información se realiza la actualización de la base
if st.sidebar.button("Crear nuevo registro"):
    new_movie = {
        'name': new_name,
        'company': new_company,
        'director' : new_director,
        'genre' : new_genre
    }
    db.collection('movies').add(new_movie)
    st.success("Nuevo filme insertado con éxito.")
