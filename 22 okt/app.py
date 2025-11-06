from flask import Flask, request, render_template_string, redirect, url_for, send_file
from pymongo import MongoClient
import gridfs
from io import BytesIO
from bson import ObjectId

app = Flask(__name__)

# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["fileDB"]
fs = gridfs.GridFS(db)

# Красивый HTML-шаблон с Tailwind
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Файловый менеджер</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 font-sans">
    <div class="container mx-auto p-6">
        <h1 class="text-3xl font-bold mb-6 text-center text-gray-800">Файловый менеджер</h1>

        <div class="bg-white shadow-md rounded p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">Загрузка файла</h2>
            <form method="POST" action="/upload" enctype="multipart/form-data" class="flex gap-2">
                <input type="file" name="file" class="border rounded px-3 py-2 flex-1">
                <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Загрузить</button>
            </form>
        </div>

        <div class="bg-white shadow-md rounded p-6">
            <h2 class="text-xl font-semibold mb-4">Список файлов</h2>
            <div class="overflow-x-auto">
            <table class="min-w-full bg-white">
                <thead class="bg-gray-200">
                    <tr>
                        <th class="py-2 px-4 text-left">Название</th>
                        <th class="py-2 px-4 text-left">Размер (байт)</th>
                        <th class="py-2 px-4 text-left">Размер чанка</th>
                        <th class="py-2 px-4 text-left">Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {% for file in files %}
                    <tr class="border-b hover:bg-gray-50">
                        <td class="py-2 px-4">{{ file.filename }}</td>
                        <td class="py-2 px-4">{{ file.length }}</td>
                        <td class="py-2 px-4">{{ file.chunkSize }}</td>
                        <td class="py-2 px-4 flex gap-2">
                            <a href="{{ url_for('download_file', file_id=file._id) }}" class="text-white bg-green-500 px-3 py-1 rounded hover:bg-green-600">Скачать</a>
                            <a href="{{ url_for('delete_file', file_id=file._id) }}" class="text-white bg-red-500 px-3 py-1 rounded hover:bg-red-600">Удалить</a>
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="4" class="py-2 px-4 text-center text-gray-500">Файлов нет</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    files = fs.find()
    return render_template_string(HTML_TEMPLATE, files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files.get('file')
    if uploaded_file:
        data = uploaded_file.read()
        fs.put(data, filename=uploaded_file.filename)
    return redirect(url_for('index'))

@app.route('/download/<file_id>')
def download_file(file_id):
    file = fs.get(ObjectId(file_id))  # конвертируем обратно в ObjectId
    return send_file(
        BytesIO(file.read()),
        download_name=file.filename,
        as_attachment=True
    )

@app.route('/delete/<file_id>')
def delete_file(file_id):
    fs.delete(ObjectId(file_id))  # конвертируем обратно в ObjectId
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
