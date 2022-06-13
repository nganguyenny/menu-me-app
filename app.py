import streamlit as st
import pandas as pd
from PIL import Image
from google.cloud import storage
from google.oauth2 import service_account
import json
import requests
import time

###############################
######## Display menu #########
###############################
def display_menu(path):
    # df = pd.read_json(path)
    df = pd.DataFrame(path)
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


##################### LOCAL TEST ###############
# import os
# from dotenv import load_dotenv, find_dotenv
# #Connecting with GCP
# env_path = find_dotenv()
# load_dotenv(env_path)
# CREDENTIALS_JSON_GOOGLE_CLOUD = os.getenv('CREDENTIALS_JSON_GOOGLE_CLOUD')
################################################

##################################
####     Google Cloud Run     ####
##################################
import os

CREDENTIALS_JSON_GOOGLE_CLOUD = os.environ['CREDENTIALS_JSON_GOOGLE_CLOUD']


from streamlit import legacy_caching
legacy_caching.clear_cache()

# time.sleep(10)

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    img = Image.open(uploaded_file)
    rgb_im = img.convert("RGB")
    rgb_im.save("img.jpg")
    credentials = service_account.Credentials.from_service_account_info(json.loads(CREDENTIALS_JSON_GOOGLE_CLOUD))
    client = storage.Client(credentials=credentials, project='menu-me-352703')
    bucket = client.get_bucket('menu_me_bucket')
    blob = bucket.blob("img.jpg")
    blob.upload_from_filename("img.jpg")

    my_bar = st.progress(0)

    for i in range(100):
    # with st.spinner('Your photo is being uploaded...'):
        time.sleep(0.1)
        my_bar.progress(i+1)
        
    st.write('Photo is uploaded 🥳')

    with st.spinner('Your menu is coming soon... 🌮 🌯 🥙'):
        # # TEST WITH SEED DATABASE
        # path = 'seed_db.json'
        # display_menu(path)
        
        time.sleep(0.)
        # # REAL API link
        url = 'https://menu-me-api-rmype5shcq-ew.a.run.app/dish'
        response = requests.get(url).json()
        display_menu(response)

    st.write('Enjoy your meals! 🥰')

    credentials = service_account.Credentials.from_service_account_info(json.loads(CREDENTIALS_JSON_GOOGLE_CLOUD))
    client = storage.Client(credentials=credentials, project='menu-me-352703')
    bucket = client.get_bucket('menu_me_bucket')
    blob = bucket.blob("img.jpg")
    blob.delete()
