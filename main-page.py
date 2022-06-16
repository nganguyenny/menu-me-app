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


def save_item_details_html(dish_name, img_url, translated_name, allergy_information, ingredients, recipe,  menu_loc_url):
    # Allergy
    if allergy_information == 'No information found for this dish':
        allergy_html = ""
    else:
        allergy_html = f'''<h4>Allergy Information</h4>
                    <p>{allergy_information}</p>'''                
    # Ingredients
    if ingredients == 'No ingredients found':
        ingredients_html = ''
    else:
        ingredients_str = ''
        for ingredient in ingredients:
            ingredients_str += f"'<li>'{ingredient}'</li>'"
        ingredients_html = f'''<h4>Ingredients</h4>
                        <ul>{ingredients_str}</ul>'''
    # Recipe
    if recipe == 'No recipe found':
        recipe_html = ''
    else:
        recipe_str = ''
        for step in recipe:
            recipe_str += f"'<li>'{step}'</li>'"
        recipe_html = f'''<h4>Recipe</h4>
                        <ol>{recipe_str}</ol>'''
    # Dish item locator
    if menu_loc_url == None:
        menu_loc_html = ''
    else:
        menu_loc_html = f'''<h4>Location of dish on the menu ⭐️ 👇</h4>
                    <img class="img-star-menu" src="{menu_loc_url}">'''
    result = f'''<html>
        <head>
            <link rel="stylesheet" href="https://storage.googleapis.com/menu_me_bucket/styles.css">
            <meta name="viewport" content="width=device-width,initial-scale=1,shrink-to-fit=no">
            <title>Menu.me: {dish_name}</title>
            <link rel=”icon" href="hhttps://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/apple/325/pizza_1f355.png">
            <meta charset="UTF-8">
        </head>
        <body>
            <div class="card-trip">
                <img src="{img_url}" />
                <div class="card-trip-infos">
                    <div>
                    <h2>{dish_name}</h2>
                    <h3>{translated_name}</h3>
                    {allergy_html}
                    {ingredients_html}
                    {recipe_html}
                    {menu_loc_html}
                    </div>
                </div>
              </div>
        </body>
        </html>'''
    return result


################### LOCAL TEST ###############
# import os
# from dotenv import load_dotenv, find_dotenv

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

target_language = 'en'
# Setup the Google Storage
credentials = service_account.Credentials.from_service_account_info(json.loads(CREDENTIALS_JSON_GOOGLE_CLOUD))
client = storage.Client(credentials=credentials, project='menu-me-352703')
bucket = client.get_bucket('menu_me_bucket')

with st.sidebar:
    # Select translation target language
    target_language = st.selectbox("1. Select Your Language", ["en", "vi", "nl", "fr", "tl"])

    uploaded_file = st.file_uploader("2. Upload or take a photo")
if uploaded_file is not None:
    # Get current time to put into img name
    date_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    print('> current date_time: ', date_time)

    # Get photo from user
    img = Image.open(uploaded_file)
    rgb_im = img.convert("RGB")
    rgb_im.save(f"menu-{date_time}.jpg")
    print(f'> rgb_im is save at: menu-{date_time}.jpg')

    # Upload photo to Google Storage
    with st.spinner('Menu photo is being transformed... ✨✨'):
        time.sleep(2)
        blob = bucket.blob(f"menu-{date_time}.jpg")
        blob.upload_from_filename(f"menu-{date_time}.jpg")
        print('> blob just finished uploading to Google Storage')
        time.sleep(3)

    # Show progress bar for uploading image
    my_bar = st.sidebar.progress(0)
    for i in range(100):
        time.sleep(0.1)
        my_bar.progress(i+1)
    st.sidebar.write('Menu photo is successfully uploaded! 🥳')
    st.sidebar.write("Let's go to home page 👉")
    st.sidebar.write(" ")
    st.sidebar.image(rgb_im)


    # Start calling API to get dish name
    base_url = f'https://menu-me-api-rmype5shcq-as.a.run.app'
    menu_img_url = f"{base_url}/dish?path=https://storage.googleapis.com/menu_me_bucket/menu-{date_time}.jpg"
    print(f'> menu_img_url on cloud storage: https://storage.googleapis.com/menu_me_bucket/menu-{date_time}.jpg')
    with st.spinner('Our kitchen is cooking the secret recipe... 👩‍🍳'):
        finish = False
        run_times = 0
        while finish != True:
            response = requests.get(menu_img_url)
            if response.status_code == 200:
                all_dishnames = response.json()
                print('> successfully fetched API/dish')
                print('all_dishnames: ', all_dishnames)
                finish = True
            elif response.status_code == 503:
                st.write('Our kitchen is too busy, please come back in a few minutes! 🙏')
                print('response.status_code:', response.status_code)
                finish = True
            else:
                if run_times < 5:
                    time.sleep(1)
                    print('> sleep for 0.5s, and try fetch API/dish again')
                    run_times += 1
                    print('response.status_code:', response.status_code)
                else:
                    finish = True
                    print('Tried 5 times, cant fetch API/dish')

    # st.write(all_dishnames)

    # Display full menu
    with st.spinner('Your menu is coming soon... 🌮 🌯 🥙'):
        count = 0
        for key, value in all_dishnames.items():
            print('key: ', key)
            print('value: ', value)
            item_request_url = f"{base_url}/item?item={key}&language={target_language}"
            print(item_request_url)
            item_details = requests.get(item_request_url).json()
            print('> item details api response: ', item_details)
            if item_details['img_url'] != None:
                dish_name = item_details['dish_name'].title()
                img_url = item_details['img_url']
                translated_name = item_details['translated_name'].title()
                allergy_information = item_details['allergy_information']
                recipe = item_details['recipe']
                ingredients = item_details['ingredients']
                menu_loc_url = value

                # save and store html render to cloud storage:
                item_html = save_item_details_html(dish_name, img_url, translated_name, allergy_information, ingredients, recipe,  menu_loc_url)
                print('> item_html: successfully save_item_details_html')
                item_html_url = f'{count}_{date_time}_{dish_name.replace(" ", "-")}.html'
                print('> item_html_url: ', item_html_url)

                with open(item_html_url, 'w') as file:
                    file.write(item_html)

                item_html_blob = bucket.blob(item_html_url)
                item_html_blob.upload_from_filename(item_html_url)

                # full path to html link in cloud storage:
                html_link = f"https://storage.googleapis.com/menu_me_bucket/{item_html_url}"
                print('> full html render link for each item: ', html_link)

                display_menu_item(dish_name, img_url, translated_name, html_link)
                count+=1

    st.write('Enjoy your meals! 🥰')

    # blob.delete()
    # os.remove(rgb_im)
