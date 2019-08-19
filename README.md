# Passport MRZ Reader Web Service
## prerequisites
- Python 3.7.2

------------------------------
## install

    pip install -r requirements.txt

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
- need permission on Temp directory for write image
- image must be horizontal layout

