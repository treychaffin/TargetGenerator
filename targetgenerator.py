from flask import Flask, send_file, render_template, request

app = Flask(__name__)


@app.route("/")
def download_page():
    return render_template("targetgenerator.html")


@app.route("/download_pdf", methods=["GET", "POST"])
def run_function():
    # Run your function here
    if request.method == "POST":
        moa = request.form.get("moa")
        yardage = request.form.get("yardage")
        diagonal_thickness = request.form.get("diagonal_thickness")
        print(moa, yardage, diagonal_thickness)
    return send_file("100yards_0-5moa.pdf", as_attachment=True)


if __name__ == "__main__":
    app.run(port=5000)
