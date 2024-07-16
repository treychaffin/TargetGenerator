import os
import re

from flask import Flask, redirect, render_template, request, url_for
from werkzeug.security import safe_join

from pdf_gen import target

app = Flask(__name__)


@app.route("/")
def download_page():
    return render_template("targetgenerator.html")


@app.route("/create_target", methods=["GET", "POST"])
def run_function():
    global filename
    if request.method == "POST":
        moa = request.form.get("moa", "0.25")
        yardage = request.form.get("yardage", "100")
        diagonal_thickness = request.form.get("diagonal_thickness", "0.125")
        scope_adjustment_text = request.form.get("scope_adjustment_text", False)

        # Ensure variables are the correct types
        moa = "0" + moa if moa.startswith(".") else moa  # float
        diagonal_thickness = (
            "0" + diagonal_thickness
            if diagonal_thickness.startswith(".")
            else diagonal_thickness
        )  # float

        Target = target(
            float(yardage),
            float(moa),
            float(diagonal_thickness),
            bool(scope_adjustment_text),
        )
        Target.create_target()
        filename = Target.filename
        return redirect(url_for("view_pdf", filename=filename))


@app.route("/pdf")
def view_pdf():
    return render_template("pdf.html", filename=filename)


@app.route("/delete_pdf", methods=["POST"])
def delete_pdf():
    """Delete the PDF file after exiting viewing/downloading it."""

    if filename is None:
        return "No file to delete", 400

    # prevent path injection
    print(f"filename[{type(filename)}]: {filename}")
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
