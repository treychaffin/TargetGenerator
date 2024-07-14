import os
import re

from flask import Flask, redirect, render_template, request, url_for
from werkzeug.utils import safe_join

from pdf_gen import create_target

app = Flask(__name__)


@app.route("/")
def download_page():
    return render_template("targetgenerator.html")


@app.route("/create_target", methods=["GET", "POST"])
def run_function():
    global filename
    if request.method == "POST":
        moa = request.form.get("moa")
        yardage = request.form.get("yardage")
        diagonal_thickness = request.form.get("diagonal_thickness")
        scope_adjustment_text = bool(request.form.get("scope_adjustment_text"))

        # Ensure variables are the correct types
        moa = "0" + moa if moa.startswith(".") else moa  # float
        diagonal_thickness = (
            "0" + diagonal_thickness
            if diagonal_thickness.startswith(".")
            else diagonal_thickness
        )  # float

        create_target(
            MOA=float(moa),
            yards=float(yardage),
            diagonal_thickness=float(diagonal_thickness),
            scope_adjustment_text=bool(scope_adjustment_text),
        )
        filename = f"{str(yardage)}yards_{str(moa).replace('.','-')}moa.pdf"
        return redirect(url_for("view_pdf", filename=filename))


@app.route("/pdf")
def view_pdf():
    filename = request.args.get("filename")
    return render_template("pdf.html", filename=filename)


@app.route("/delete_pdf", methods=["POST"])
def delete_pdf():
    """Delete the PDF file after exiting viewing/downloading it."""

    # prevent path injection
    sanitized_filename = re.sub(r"[^a-zA-Z0-9\-_\.]", "", filename)
    filepath = safe_join(os.getcwd(), "static", sanitized_filename)
    normalized_path = os.path.normpath(filepath)
    base_path = os.path.normpath(os.getcwd() + "/static")
    if not normalized_path.startswith(base_path):
        return "Invalid file path", 400

    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
