import os
import zipfile
from io import BytesIO
from flask import Flask, request, render_template, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename

app = Flask(
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

app.secret_key = 'your_secret_key_here'

UPLOAD_FOLDER = 'organized_files'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the base upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_category(extension):
    categories = {
        'pdf': 'PDFs',
        'png': 'Images',
        'jpg': 'Images',
        'jpeg': 'Images',
        'gif': 'Images',
        'docx': 'Documents',
        'txt': 'TextFiles'
    }
    return categories.get(extension, 'Others')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('files')
        success = False

        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower()
                category = get_category(ext)

                save_path = os.path.join(app.config['UPLOAD_FOLDER'], category)
                os.makedirs(save_path, exist_ok=True)
                file.save(os.path.join(save_path, filename))
                success = True

        if success:
            flash("✅ Files uploaded and organized successfully!", "success")
            return redirect(url_for('upload_file', download='true'))
        else:
            flash("⚠️ No valid files were uploaded.", "error")
            return redirect(url_for('upload_file'))

    return render_template('index.html', download=request.args.get('download') == 'true')

@app.route('/download')
def download():
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zipf:
        for root, _, files in os.walk(UPLOAD_FOLDER):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, UPLOAD_FOLDER)
                zipf.write(file_path, arcname)
    memory_file.seek(0)
    return send_file(
        memory_file,
        download_name='organized.zip',
        as_attachment=True
    )

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
