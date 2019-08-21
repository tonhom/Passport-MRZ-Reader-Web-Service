import os
from flask import Flask, flash, request, redirect, url_for, json
from flask_cors import CORS
from werkzeug.utils import secure_filename
import uuid
from passport_mrz import get_passport_data
import argparse

parser = argparse.ArgumentParser(prog='Passport MRZ Reader Web Service', description='Extract information from Passport MRZ (TD3 format)')
parser.add_argument('-ip', '--host', type=str, default="127.0.0.1")
parser.add_argument('-p', '--port', type=int, default=5000)
args = parser.parse_args()

cer = os.path.join(os.path.dirname(__file__), 'Cert/mrz_reader.crt')
key = os.path.join(os.path.dirname(__file__), 'Cert/mrz_reader.key')

UPLOAD_FOLDER = './Temp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "dsfmdskojfdsjfkdshfjkds"
# app.debug = True

cors = CORS(app)


class Response():
    status: bool
    message: str
    data: object

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    resp = Response()
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            # flash('No file part')
            resp.status = False
            resp.message = 'No file part'
            # return redirect(request.url)
        else:
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                # flash('No selected file')
                # return redirect(request.url)
                resp.status = False
                resp.message = 'No selected file'
            elif file and allowed_file(file.filename):
                id = uuid.uuid4()
                filename = secure_filename(file.filename)
                filename = str(id) + "--" + filename
                imgPath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(imgPath)
                try:
                    resp.data = get_passport_data(imgPath)
                    if resp.data is not None:
                        resp.status = True
                    else:
                        resp.status = False
                        resp.message = 'Can not get passport information'

                except Exception as identifier:
                    resp.status = False
                    resp.message = str(identifier)
                    resp.data = None
                
                # remove file
                os.remove(imgPath)
            else:
                resp.status = False
                resp.message = "unexpectred"
                resp.data = file.filename
                # return redirect(url_for('uploaded_file', filename=filename))
    else:
        resp.status = False
        resp.message = 'Method not allow'
        # resp.data = {'test' : "test data"}

    # print("None" if resp is None else resp.toJSON())
    response = app.response_class(
        response=resp.toJSON(),
        status=200,
        mimetype='application/json'
    )
    return response

    # return '''
    # <!doctype html>
    # <title>Upload new File</title>
    # <h1>Upload new File</h1>
    # <form method=post enctype=multipart/form-data>
    #   <input type=file name=file>
    #   <input type=submit value=Upload>
    # </form>
    # '''


if __name__ == "__main__":
    os.environ['DEBUG'] = "1"
    app.run(debug=True, ssl_context=(cer, key), host=args.host, port=args.port)
