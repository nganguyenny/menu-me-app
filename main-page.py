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
            ingredients_str += f'<li>{ingredient}</li>'
        ingredients_html = f'''<h4>Ingredients</h4>
                        <ul>{ingredients_str}</ul>'''
    # Recipe
    if recipe == 'No recipe found':
        recipe_html = ''
    else:
        recipe_str = ''
        for step in recipe:
            recipe_str += f'<li>{step}</li>'
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

st.set_page_config(page_title="Menu.me", page_icon="🍕", layout='wide', initial_sidebar_state='expanded')

from streamlit import legacy_caching
legacy_caching.clear_cache()

with open('front-end/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.markdown('''<h1 style="font-size:48px;padding: 20px 0 0 0; padding-top: 20px;">Menu</h1>
<h1 style="color:#FE714C;font-size:48px;padding:0;">.me<h1>
<p style="color:gray;font-size:20px;padding:0;">Delicious meals</p>
''', unsafe_allow_html=True)

target_language = 'en'
# Setup the Google Storage
credentials = service_account.Credentials.from_service_account_info(json.loads(CREDENTIALS_JSON_GOOGLE_CLOUD))
client = storage.Client(credentials=credentials, project='menu-me-352703')
bucket = client.get_bucket('menu_me_bucket')

# sub_title = '👈 Open side bar to upload your menu'

with st.sidebar:
    st.title('Menu input')
    # Select translation target language
    supported_languages = {'Afrikaans':'af','Albanian':'sq','Amharic':'am','Arabic':'ar','Armenian':'hy','Azerbaijani':'az','Basque':'eu','Belarusian':'be','Bengali':'bn','Bosnian':'bs','Bulgarian':'bg','Catalan':'ca','Cebuano':'ceb','Chichewa':'ny','Chinese (Simplified)':'zh-CN','Chinese (Simplified)':'zh','Chinese (Traditional)':'zh-TW','Corsican':'co','Croatian':'hr','Czech':'cs','Danish':'da','Dutch':'nl','English':'en','Esperanto':'eo','Estonian':'et','Filipino':'tl','Finnish':'fi','French':'fr','Frisian':'fy','Galician':'gl','Georgian':'ka','German':'de','Greek':'el','Gujarati':'gu','Haitian Creole':'ht','Hausa':'ha','Hawaiian':'haw','Hebrew':'iw','Hebrew':'he','Hindi':'hi','Hmong':'hmn','Hungarian':'hu','Icelandic':'is','Igbo':'ig','Indonesian':'id','Irish':'ga','Italian':'it','Japanese':'ja','Javanese':'jw','Kannada':'kn','Kazakh':'kk','Khmer':'km','Kinyarwanda':'rw','Korean':'ko','Kurdish (Kurmanji)':'ku','Kyrgyz':'ky','Lao':'lo','Latin':'la','Latvian':'lv','Lithuanian':'lt','Luxembourgish':'lb','Macedonian':'mk','Malagasy':'mg','Malay':'ms','Malayalam':'ml','Maltese':'mt','Maori':'mi','Marathi':'mr','Mongolian':'mn','Myanmar (Burmese)':'my','Nepali':'ne','Norwegian':'no','Odia (Oriya)':'or','Pashto':'ps','Persian':'fa','Polish':'pl','Portuguese':'pt','Punjabi':'pa','Romanian':'ro','Russian':'ru','Samoan':'sm','Scots Gaelic':'gd','Serbian':'sr','Sesotho':'st','Shona':'sn','Sindhi':'sd','Sinhala':'si','Slovak':'sk','Slovenian':'sl','Somali':'so','Spanish':'es','Sundanese':'su','Swahili':'sw','Swedish':'sv','Tajik':'tg','Tamil':'ta','Tatar':'tt','Telugu':'te','Thai':'th','Turkish':'tr','Turkmen':'tk','Ukrainian':'uk','Urdu':'ur','Uyghur':'ug','Uzbek':'uz','Vietnamese':'vi','Welsh':'cy','Xhosa':'xh','Yiddish':'yi','Yoruba':'yo','Zulu':'zu'}
    language_input = st.selectbox("Step 1. Select your language", [*supported_languages])
    target_language = supported_languages[language_input]
    print(f'language_input:{language_input}, target_language:{target_language}')

    uploaded_file = st.file_uploader("Step 2. Upload or take a photo")
if uploaded_file is not None:
    # Get current time to put into img name
    date_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    print('----> current date_time: ', date_time)

    # Get photo from user
    img = Image.open(uploaded_file)
    rgb_im = img.convert("RGB")
    rgb_im.save(f"menu-{date_time}.jpg")
    print(f'----> rgb_im is save at: menu-{date_time}.jpg')
    st.sidebar.write("Menu photo is being transformed... ✨✨")
    # Upload photo to Google Storage
    with st.spinner('Menu photo is being transformed... ✨✨'):
        time.sleep(2)
        blob = bucket.blob(f"menu-{date_time}.jpg")
        blob.upload_from_filename(f"menu-{date_time}.jpg")
        print('----> blob just finished uploading to Google Storage')
        time.sleep(3)

    # Show progress bar for uploading image
    my_bar = st.sidebar.progress(0)
    for i in range(100):
        time.sleep(0.1)
        my_bar.progress(i+1)
    st.sidebar.write('Menu photo is successfully uploaded! 🥳')
    st.sidebar.subheader("Let's go to home page 👉")
    st.sidebar.write(" ")
    st.sidebar.image(rgb_im)


    # Start calling API to get dish name
    base_url = f'https://menu-me-api-rmype5shcq-as.a.run.app'
    menu_img_url = f"{base_url}/dish?path=https://storage.googleapis.com/menu_me_bucket/menu-{date_time}.jpg"
    print(f'----> PHOTO OF MENU saved on cloud storage: https://storage.googleapis.com/menu_me_bucket/menu-{date_time}.jpg')
    with st.spinner('Our kitchen is cooking the secret recipe, please wait... 👩‍🍳'):
        finish = False
        run_times = 0
        while finish != True:
            response = requests.get(menu_img_url)
            if response.status_code == 200:
                all_dishnames = response.json()
                print('----> successfully fetched API/dish')
                print('all_dishnames: ', all_dishnames)
                finish = True
            elif response.status_code == 503:
                st.write('Our kitchen is too busy, please come back in a few minutes! 🙏')
                print('response.status_code:', response.status_code)
                finish = True
            else:
                if run_times < 10:
                    time.sleep(1)
                    print('----> sleep for 1s, and try fetch API/dish again')
                    run_times += 1
                    print('response.status_code:', response.status_code)
                else:
                    finish = True
                    print('Tried 10 times, cant fetch API/dish')
                    st.write('Please try again later...')

    # st.write(all_dishnames)

    # Display full menu
    with st.spinner('Your menu is coming soon... 🌮 🌯 🥙'):
        count = 0
        for key, value in all_dishnames.items():
            print(f'----------------Item {count}-------------------')
            print('key: ', key)
            print('value: ', value)
            item_request_url = f"{base_url}/item?item={key}&language={target_language}"
            print(item_request_url)
            item_details = requests.get(item_request_url).json()
            print('----> item details api response: ', item_details)
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
                print('----> item_html: successfully save_item_details_html')
                item_html_url = f'{count}_{date_time}_{dish_name.replace(" ", "-")}.html'
                print('----> item_html_url: ', item_html_url)

                with open(item_html_url, 'w') as file:
                    file.write(item_html)

                item_html_blob = bucket.blob(item_html_url)
                item_html_blob.upload_from_filename(item_html_url)

                # full path to html link in cloud storage:
                html_link = f"https://storage.googleapis.com/menu_me_bucket/{item_html_url}"
                print('----> FULL HTML RENDER LINK for each item: ', html_link)

                display_menu_item(dish_name, img_url, translated_name, html_link)
                count+=1

    st.write('Enjoy your meals! 🥰')

    # blob.delete()
    # os.remove(rgb_im)
