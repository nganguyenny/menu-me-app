import streamlit as st
import pandas as pd
from PIL import Image
from google.cloud import storage
from google.oauth2 import service_account
import json
import requests

###############################
######## Display menu #########
###############################
def display_menu(path):
    df = pd.read_json(path)
    df = pd.DataFrame(df)
    with open('front-end/styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    for index, row in df.iterrows():
        st.markdown(f'''<div class="card-product">
            <img src="{row['img_url']}"/>
            <div class="card-product-infos">
                <h2>{row['dish_name']}</h2>
                <p>{row['translated_name']}</p>
            </div>
            </div>''', unsafe_allow_html=True)

##################################
####   Streamlit home page    ####
##################################
import os

CREDENTIALS_JSON_GOOGLE_CLOUD = os.environ['CREDENTIALS_JSON_GOOGLE_CLOUD']

# img_file_buffer = st.camera_input("Take a picture!")

# if img_file_buffer is not None:
from streamlit import legacy_caching
legacy_caching.clear_cache()

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    img = Image.open(uploaded_file)
    rgb_im = img.convert("RGB")
    rgb_im.save("img.jpg")
    credentials = service_account.Credentials.from_service_account_info(json.loads(CREDENTIALS_JSON_GOOGLE_CLOUD))
    client = storage.Cliesnt(credentials=credentials, project='menu-me-352703')
    bucket = client.get_bucket('menu_me_bucket')
    blob = bucket.blob("img.jpg")
    blob.upload_from_filename("img.jpg")
    st.write('Photo is uploaded 🥳')

    with st.spinner('Your menu is coming soon... 🌮 🌯 🥙'):
        # TEST WITH SEED DATABASE
        path = 'seed_db.json'
        display_menu(path)
        

        # # REAL API link
        # url = '/dish'
        # response = requests.get(url).json()

    st.write('Enjoy your meals! 🥰')

