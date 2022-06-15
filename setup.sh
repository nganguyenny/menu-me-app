mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"nganguyen.ngocyen@gmail.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
[theme]
base = 'light'\n\
enableXsrfProtection = false\n
enableWebsocketCompression = false\n
serverAddress = 'https://menu-me-app.herokuapp.com/'\n
" > ~/.streamlit/config.toml
