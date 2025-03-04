from flask import Flask, render_template, request, redirect, url_for
from folder_parser import parse_folder
from folder_parser import parse_folder, simulate_ftp_upload
import os
import shutil
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    # Process the uploaded folder (call existing parsing logic)
    processed_folder = parse_folder(file_path)
    
    return redirect(url_for('review', folder=processed_folder))

@app.route('/review/<folder>')
def review(folder):
    csv_path = os.path.join(folder, 'metadata.csv')
    df = pd.read_csv(csv_path)
    return render_template('review.html', data=df.to_dict(orient='records'), folder=folder)

@app.route('/process/<folder>', methods=['POST'])
def process(folder):
    csv_path = os.path.join(folder, 'metadata.csv')
    simulate_ftp_upload(csv_path)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
