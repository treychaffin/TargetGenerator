from flask import Flask, send_file, render_template

app = Flask(__name__)

@app.route('/')
def download_page():
    return render_template('targetgenerator.html')

@app.route('/download_pdf')
def run_function():
    # Run your function here
    return send_file('100yards_0-5moa.pdf',as_attachment=True)

if __name__ == '__main__':
    app.run(port=5000)