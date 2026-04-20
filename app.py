import os
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'PseudoAI'
PSEUDO_CENSORSHIP = 'PseudoCensorship.png'
ALLOWED_EXTENSION = {'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    print("Получен запрос на /upload")
    if 'file' not in request.files:
        print("Нет файла в запросе")
        return jsonify({'error': 'Нет файла'}), 400

    file = request.files['file']

    if file.filename == '':
        print("Пустое имя файла")
        return jsonify({'error': 'Файл не выбран'}), 400

    if not allowed_file(file.filename):
        print(f"Неправильный формат: {file.filename}")
        return jsonify({'error': 'Только PNG файлы разрешены'}), 400

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    secure_name = secure_filename(f"{timestamp}_{file.filename}")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
    file.save(filepath)
    print(f"Файл сохранён: {filepath}")

    if os.path.exists(PSEUDO_CENSORSHIP):
        print(f"Используем существующий файл: {PSEUDO_CENSORSHIP}")
    else:
        print(f"ВНИМАНИЕ: {PSEUDO_CENSORSHIP} не найден!")

    result_url = url_for('download_result', filename='PseudoCensorship.png', _external=True)

    return jsonify({
        'message': 'Файл загружен',
        'filename': secure_name,
        'result_url': result_url,
        'preview_url': url_for('uploaded_file', filename=secure_name)
    })


@app.route('/process', methods=['POST'])
def process_image():
    print("Получен запрос на /process")
    if os.path.exists(PSEUDO_CENSORSHIP):
        result_url = url_for('download_result', filename='PseudoCensorship.png', _external=True)
        return jsonify({'result_url': result_url})
    else:
        return jsonify({'error': 'Файл заглушки не найден'}), 404


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/result/<filename>')
def download_result(filename):
    return send_from_directory('.', filename, as_attachment=False)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)