from flask import Flask, render_template, request, send_file, session
from PIL import Image
import pytesseract
from io import BytesIO
import os

pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def find_matching_files(directory, substring):
    matching_files = []

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                content = file.read()
                if substring in content:
                    matching_files.append(filename)

    return matching_files

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract_text():
    uploaded_image = request.files['image']
    if uploaded_image:
        image = Image.open(uploaded_image)
        text = pytesseract.image_to_string(image)
        session['extracted_text'] = text
        print("Extracted Text:", text)
        return text
    return "No text to extract"

@app.route('/download')
def download_text():
    extracted_text = session.get('extracted_text', default='')
    if extracted_text:
        text_file = BytesIO(extracted_text.encode('utf-8'))
        text_file.seek(0)
        response = send_file(text_file, as_attachment=True, download_name='extracted_text.txt', mimetype='text/plain')
        return response
    else:
        return "No text to download"

@app.route('/category')
def category():
    directory = "./text_file"  # Replace with the actual path to your files
    substrings = session.get('extracted_text', default='').split()

    matching_files = []

    for substring in substrings:
        files = find_matching_files(directory, substring)
        if files:
            matching_files.extend(files)

    if matching_files:
        result = "\n".join(set(matching_files))  # Using set to remove duplicates
    else:
        result = "Unidentified Category"
    return result.replace('.txt', '')

if __name__ == '__main__':
    app.run(debug=True)