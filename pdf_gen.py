from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import math


def minute_of_angle(input, moa, input_unit="yard", output_unit="inch"):

    # One MOA is equal to 1/60 of a degree.
    moa_per_degree = moa / 60

    if input_unit == "yard":
        inches = input * 3 * 12

    if output_unit == "inch":
        # Calculate the MOA.
        moa = inches * math.radians(moa_per_degree / 2) * 2

    return moa


def draw_centered_text(
    c, text, x, y, font="Helvetica", font_size=12, font_color="black"
):
    c.setFont(font, font_size)
    c.setFillColor(font_color)
    text_width = c.stringWidth(text, font, font_size)
    # Assuming the height of a single line of text is roughly the font size
    text_height = font_size
    # Adjust x and y to center the text
    c.drawString(x - (text_width / 2), y - (text_height / 3), text)


def create_target(
    yards=100,
    MOA=1,
    page_size=(8.5 * inch, 11 * inch),
    margin=0.5 * inch,
    diagonal_thickness=5,
):
    # Create a PDF canvas
    filename = f"{yards}yards_{str(MOA).replace('.','-')}moa.pdf"
    pdf = canvas.Canvas(filename, pagesize=page_size)

    pdf.setStrokeColor("black")
    pdf.setLineWidth(1)
    pdf.setLineCap(2)

    grid_size = minute_of_angle(yards, MOA)

    text = f"{MOA} MOA grid ({grid_size:.3f} in) at {yards} yards"
    pdf.setFillColor("black")
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(page_size[0] / 2, 0.5 * inch, text)

    available_width = (page_size[0] - 2 * margin) / inch  # inches
    available_height = (page_size[1] - 2 * margin) / inch  # inches
    num_rows = math.floor(((available_width / grid_size) // 2) * 2)
    num_cols = num_rows
    grid_width = num_cols * grid_size
    grid_height = num_rows * grid_size

    # Center the grid on the page
    x_start = margin + (available_width * inch - grid_width * inch) / 2
    y_start = margin + (available_height * inch - grid_height * inch) / 2

    x_center = margin + available_width / 2 * inch
    y_center = margin + available_height / 2 * inch

    # Quadrant lines
    pdf.setStrokeColor("gray")
    pdf.setLineWidth(5)
    pdf.line(x_center, y_start, x_center, y_start + grid_height * inch)
    pdf.line(x_start, y_center, x_start + grid_width * inch, y_center)
    pdf.setStrokeColor("black")
    pdf.setLineWidth(1)

    # Draw horizontal lines
    for i in range(num_rows + 1):
        y = y_start + i * grid_size * inch
        pdf.line(x_start, y, x_start + grid_width * inch, y)

    # Draw vertical lines
    for i in range(num_cols + 1):
        x = x_start + i * grid_size * inch
        pdf.line(x, y_start, x, y_start + grid_height * inch)

    # Draw diagonal lines
    pdf.setLineWidth(diagonal_thickness)
    pdf.line(
        x_start, y_start, x_start + grid_width * inch, y_start + grid_height * inch
    )
    pdf.line(
        x_start + grid_width * inch, y_start, x_start, y_start + grid_height * inch
    )

    # Scope Adjustment Text
    scope_adjustment_text_size = 72
    draw_centered_text(
        pdf,
        "R/U",
        x_center - (x_center - x_start) / 2,
        y_center - (y_center - y_start) / 2,
        font_size=scope_adjustment_text_size,
        font_color="gray",
    )
    draw_centered_text(
        pdf,
        "R/D",
        x_center - (x_center - x_start) / 2,
        y_center + (y_center - y_start) / 2,
        font_size=scope_adjustment_text_size,
        font_color="gray",
    )
    draw_centered_text(
        pdf,
        "L/U",
        x_center + (x_center - x_start) / 2,
        y_center - (y_center - y_start) / 2,
        font_size=scope_adjustment_text_size,
        font_color="gray",
    )
    draw_centered_text(
        pdf,
        "L/D",
        x_center + (x_center - x_start) / 2,
        y_center + (y_center - y_start) / 2,
        font_size=scope_adjustment_text_size,
        font_color="gray",
    )

    pdf.save()


if __name__ == "__main__":
    create_target()