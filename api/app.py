import os
from flask import Flask, request, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

app.secret_key = 'your_secret_key_here'  # Replace with a strong secret

UPLOAD_FOLDER = 'organized_files'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
        else:
            flash("⚠️ No valid files were uploaded.", "error")

        return redirect(url_for('upload_file'))

    return render_template('index.html')

# For testing
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))



