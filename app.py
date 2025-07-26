from flask import Flask, render_template, request, send_file
import os
import tempfile
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        merged_writer = PdfWriter()

        file_ids = request.form.getlist("file_ids")

        for file_id in file_ids:
            remove_first = int(request.form.get(f'remove_first_{file_id}', 0))
            remove_last = int(request.form.get(f'remove_last_{file_id}', 0))
            uploaded_file = request.files.getlist("pdfs")[file_ids.index(file_id)]

            reader = PdfReader(uploaded_file)
            total_pages = len(reader.pages)
            writer = PdfWriter()

            start = remove_first
            end = total_pages - remove_last

            for i in range(start, end):
                writer.add_page(reader.pages[i])

            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_output:
                writer.write(temp_output)
                temp_output.close()

                trimmed_reader = PdfReader(temp_output.name)
                for page in trimmed_reader.pages:
                    merged_writer.add_page(page)

                os.remove(temp_output.name)

        output_path = os.path.join(tempfile.gettempdir(), "merged_trimmed.pdf")
        with open(output_path, "wb") as out_file:
            merged_writer.write(out_file)

        return send_file(output_path, as_attachment=True, download_name="merged_trimmed.pdf")

    return render_template("index.html")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
