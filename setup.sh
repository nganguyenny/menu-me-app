mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"nganguyen.ngocyen@gmail.com\"\n\
" > ~/.streamlit/credentials.toml

# echo "\
# [server]\n\
# headless = true\n\
# enableCORS=false\n\
# port = $PORT\n\
# [theme]
# base = 'light'\n\
# " > ~/.streamlit/config.toml

echo .streamlit/config.toml > ~/.streamlit/config.toml
