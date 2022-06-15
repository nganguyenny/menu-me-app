import streamlit as st
import pandas as pd
from PIL import Image
from google.cloud import storage
from google.oauth2 import service_account
import json
import requests
import time
from datetime import datetime
import os

###############################
######## Display menu #########
###############################
def display_menu_item(dish_name, img_url, translated_name, html_link):
    st.markdown(f'''<div class="card-product">
            <a href="{html_link}" target="_blank">
                <img src="{img_url}"/>
            </a>
            <a href='{html_link}' style="text-decoration: none;">
                <div class="card-product-infos">
                    <h2>{dish_name}</h2>
                    <p>{translated_name}</p>
                </div>
            </a>
        </div>''', unsafe_allow_html=True)

def save_item_details_html(dish_name, img_url, translated_name):
    result = f'''<html>
        <head>
            <!-- <link rel="stylesheet" href="https://storage.googleapis.com/menu_me_bucket/styles.css"> -->
            <link rel="stylesheet" href="styles-test.css">
        </head>
        <body>
            <div class="card-trip">
                <img src="{img_url}" />
                <div class="card-trip-infos">
                    <div>
                    <h2>{dish_name}</h2>
                    <h3>{translated_name}</h3>
                    <h4>Allergy Information</h4>
                    <p>Ok</p>
                    <h4>Ingredients</h4>
                    <ul>
                        <li>Sample Ingredients</li>
                    </ul>
                    <h4>Recipe</h4>
                    <ol>
                        <li>Sample step</li>
                    </ul>
                    </div>
                </div>
                </div>
        </body>
        </html>'''
    return result


################### LOCAL TEST ###############
# import os
# from dotenv import load_dotenv, find_dotenv
# #Connecting with GCP
# env_path = find_dotenv()
# load_dotenv(env_path)
# CREDENTIALS_JSON_GOOGLE_CLOUD = os.getenv('CREDENTIALS_JSON_GOOGLE_CLOUD')
##############################################

##################################
####     Google Cloud Run     ####
##################################
import os

CREDENTIALS_JSON_GOOGLE_CLOUD = os.environ['CREDENTIALS_JSON_GOOGLE_CLOUD']

st.set_page_config(page_title="Menu.me", page_icon="🍕")

from streamlit import legacy_caching
legacy_caching.clear_cache()


with open('front-end/styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title('Menu.me')
# time.sleep(10)
target_language = 'en'

with st.sidebar:
    # Select translation target language
    target_language = st.selectbox("1. Select Your Language", ["en", "vi", "nl", "fr", "tl"])

    uploaded_file = st.file_uploader("2. Upload or take a photo")
if uploaded_file is not None:
    # Get current time to put into img name
    date_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    # Get photo from user
    img = Image.open(uploaded_file)
    rgb_im = img.convert("RGB")
    rgb_im.save(f"menu-{date_time}.jpg")

    # Setup the Google Storage
    credentials = service_account.Credentials.from_service_account_info(json.loads(CREDENTIALS_JSON_GOOGLE_CLOUD))
    client = storage.Client(credentials=credentials, project='menu-me-352703')
    bucket = client.get_bucket('menu_me_bucket')

    # Upload photo to Google Storage
    blob = bucket.blob(f"menu-{date_time}.jpg")
    blob.upload_from_filename(f"menu-{date_time}.jpg")

    # Show progress bar for uploading image
    my_bar = st.sidebar.progress(0)
    for i in range(100):
        time.sleep(0.1)
        my_bar.progress(i+1)
    st.sidebar.write('Photo is uploaded 🥳')

    # Start calling API to get dish name
    base_url = f'https://menu-me-api-rmype5shcq-as.a.run.app'
    menu_img_url = f"{base_url}/dish?path=https://storage.googleapis.com/menu_me_bucket/menu-{date_time}.jpg"
    print(menu_img_url)
    all_dishnames = requests.get(menu_img_url).json()

    # st.write(all_dishnames)

    st.sidebar.image(rgb_im)

    # Display full menu
    with st.spinner('Your menu is coming soon... 🌮 🌯 🥙'):
        count = 0
        cwd = os.getcwd()
        for dish in all_dishnames:
            item_details = requests.get(f"{base_url}/item?item={dish}&language={target_language}").json()
            if item_details['img_url'] != None:
                dish_name = item_details['dish_name'].title()
                img_url = item_details['img_url']
                translated_name = item_details['translated_name'].title()

                # save and store html render to cloud storage:
                item_html = save_item_details_html(dish_name, img_url, translated_name)
                item_html_url = f'{count}_{date_time}_{dish_name.replace(" ", "-")}.html'

                with open(item_html_url, 'w') as file:
                    file.write(item_html)


                item_html_blob = bucket.blob(item_html_url)
                item_html_blob.upload_from_filename(item_html_url)

                # full path to html link in cloud storage:
                html_link = f"https://storage.googleapis.com/menu_me_bucket/{item_html_url}"
                print(html_link)

                display_menu_item(dish_name, img_url, translated_name, html_link)
            count+=1

    st.write('Enjoy your meals! 🥰')

    # blob.delete()
    # os.remove(rgb_im)
