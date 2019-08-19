# Passport MRZ Reader Web Service
## prerequisites
- Python 3.7.2
- Tesseract 

    https://github.com/tesseract-ocr/tesseract/wiki/4.0-with-LSTM#400-alpha-for-windows



------------------------------
## install

> python packages

    pip install -r requirements.txt

> tesseract for windows

download and install then add directory to tesseract installed location to PATH in system variables section

-------------------------------
## how to run

first is set main script

> linux

    export FLASK_APP=hello.py

> on windows (cmd)

    set FLASK_APP=main.py

> on windows (powershell)

    $env:FLASK_APP = "main.py"


command to run
> linux

    flask run

> windows

    python -m flask run


upload from method post enctype = multipart/form-data

    input type file name = 'file'


----------------------------
##  Conditions
- need permission in Temp directory for write image
- image must be horizontal layout

