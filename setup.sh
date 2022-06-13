mkdir -p ~/.streamlit/

echo "\
[general]\n\
<<<<<<< HEAD
email = \"pornpanthongdee02@gmail.com\"\n\
=======
email = \"nganguyen.ngocyen@gmail.com\"\n\
>>>>>>> d1450ba50b29deae198fad60f9429a31135a407c
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
