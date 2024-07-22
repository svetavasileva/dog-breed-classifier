from flask import Flask, request, redirect, render_template  # type: ignore
from werkzeug.utils import secure_filename  # type: ignore
import os
import time

from predict import predict_dog_breed

app = Flask(__name__)

# Set the upload folder and allowed extensions
UPLOAD_FOLDER = 'static/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB


# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = time.strftime("%Y%m%d-%H%M%S") + \
            '-' + secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        file.save(file_path)

        try:
            dog_prediction = predict_dog_breed(file_path)
        except(Exception):
            dog_prediction = "Could not predict the dog" + \
                  "breed. Please, try again."
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
        return render_template("upload.html",
                               prediction=dog_prediction, img_path=file_path)
    return 'File type not allowed'


if __name__ == '__main__':
    app.run(debug=True)
