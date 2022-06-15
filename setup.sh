mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \'nganguyen.ngocyen@gmail.com\'\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
enableXsrfProtection = false\n\
enableWebsocketCompression = false\n\
port = $PORT\n\
[theme]\n\
base = 'light'\n\
" > ~/.streamlit/config.toml
