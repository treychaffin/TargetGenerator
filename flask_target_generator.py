"""Flask application for generating and viewing PDF targets."""

import logging
import os
import re

from flask import Flask, redirect, render_template, request, url_for
from werkzeug.security import safe_join

from pdf_gen import Target

app = Flask(__name__)

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


@app.route("/")
def download_page():
    """Render the main page for target generation."""
    return render_template("targetgenerator.html")


@app.route("/create_target", methods=["GET", "POST"])  # type: ignore
def run_function():
    """Handle target generation based on user input."""
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

        target = Target(
            yards=float(yardage),
            moa=float(moa),
            diagonal_thickness=float(diagonal_thickness),
            scope_adjustment_text=bool(scope_adjustment_text),
            flask=True,
        )
        filename = target.filename
        log.info(f"Generated target: {filename}")
        return redirect(url_for("view_pdf", filename=filename))


@app.route("/pdf")
def view_pdf():
    """Render the PDF viewing page."""
    return render_template("pdf.html", filename=filename)


@app.route("/delete_pdf", methods=["POST"])
def delete_pdf():
    """Delete the PDF file after exiting viewing/downloading it."""
    # prevent path injection
    sanitized_filename = re.sub(r"[^a-zA-Z0-9\-_\.]", "", filename)

    filepath = safe_join(os.getcwd(), "static", sanitized_filename)

    if not filepath:
        return "Invalid file path", 400

    normalized_path = os.path.normpath(filepath)

    base_path = os.path.normpath(os.getcwd())

    if not normalized_path.startswith(base_path):
        return "Invalid file path", 400

    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass
    return "", 204


if __name__ == "__main__":
    if not log.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
        handler.setFormatter(formatter)
        log.addHandler(handler)

    import argparse

    parser = argparse.ArgumentParser(
        description="Run the Flask Target Generator."
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=5000,
        help="Port to run the Flask application on (default: 5000)",
    )
    parser.add_argument(
        "--host",
        "-H",
        type=str,
        default="127.0.0.1",
        help="Host to run the Flask application on (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        default=False,
        help="Run the Flask application in debug mode",
    )
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, debug=args.debug)
