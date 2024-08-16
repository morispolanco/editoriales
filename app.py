import streamlit as st
import requests
import json
from datetime import datetime

# Configuración de las APIs (las claves se obtienen de los secretos de Streamlit)
TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]
SERPER_API_KEY = st.secrets["SERPER_API_KEY"]

def get_publishers_info(campo_publicacion, pais):
    # Construir el prompt para la API de Together
    prompt = f"Proporciona información sobre editoriales en {pais} que reciben manuscritos de obras literarias o de no ficción en español para el ámbito de {campo_publicacion}."
    prompt += " Incluye nombres de editoriales, requisitos básicos y enlaces si están disponibles."

    # Llamada a la API de Together
    response = requests.post(
        "https://api.together.xyz/inference",
        headers={
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "togethercomputer/llama-2-70b-chat",
            "prompt": prompt,
            "max_tokens": 512,
            "temperature": 0.7
        }
    )

    ai_response = response.json().get("choices", [{}])[0].get("text", "")

    # Llamada a la API de Serper para obtener resultados de búsqueda relacionados
    search_query = f"editoriales que reciben manuscritos {campo_publicacion} {pais}"
    serper_response = requests.post(
        "https://google.serper.dev/search",
        headers={
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "q": search_query
        }
    )

    search_results = serper_response.json().get("organic", [])  # Tomamos todos los resultados

    return ai_response, search_results

# Interfaz de Streamlit
st.title("Buscador de Editoriales")

campo_publicacion = st.text_input("Campo de publicación (Ej. Literatura, No Ficción)")
pais = st.text_input("País")
if st.button("Buscar editoriales"):
    if campo_publicacion and pais:
        ai_info, search_results = get_publishers_info(campo_publicacion, pais)

        st.subheader("Información de editoriales")
        st.write(ai_info)

        st.subheader("Resultados de búsqueda relacionados")
        if search_results:
            for result in search_results:
                st.write(f"- [{result.get('title')}]({result.get('link')})")
                st.write(result.get('snippet', ''))
        else:
            st.write("No se encontraron resultados de búsqueda.")
    else:
        st.warning("Por favor, completa todos los campos.")
