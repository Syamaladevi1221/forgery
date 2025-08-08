import os
from flask import Flask, render_template, request
from forgery_checker import calculate_md5, compare_hashes, detect_changes
import cv2

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'original' not in request.files or 'test' not in request.files:
        return "Missing files"

    original = request.files['original']
    test = request.files['test']

    orig_path = os.path.join(app.config['UPLOAD_FOLDER'], 'original.png')
    test_path = os.path.join(app.config['UPLOAD_FOLDER'], 'test.png')

    original.save(orig_path)
    test.save(test_path)

    # MD5 Hashes
    hash1 = calculate_md5(orig_path)
    hash2 = calculate_md5(test_path)
    hashes_match = compare_hashes(hash1, hash2)

    # Visual Detection
    image1 = cv2.imread(orig_path)
    image2 = cv2.imread(test_path)
    diff_img = detect_changes(image1, image2)
    diff_path = os.path.join(app.config['UPLOAD_FOLDER'], 'diff.png')
    cv2.imwrite(diff_path, diff_img)

    return render_template('result.html',
                           hash1=hash1,
                           hash2=hash2,
                           match=hashes_match,
                           diff_img='uploads/diff.png')

if __name__ == '__main__':
    app.run(debug=True)
