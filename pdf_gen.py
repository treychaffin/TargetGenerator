"""Class for generating a shooting target PDF."""

import logging
import math
import os

from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class Target:
    """Class for generating a shooting target PDF."""

    def __init__(
        self,
        **kwargs,
    ) -> None:
        """Initialize Target object and create target PDF.

        **kwargs**: allows for optional parameters:
            * **yards**: float, distance in yards (default: 100)
            * **moa**: float, minute of angle (default: 0.25)
            * **diagonal_thickness**: float, thickness of diagonal lines in
                inches (default: 0.125)
            * **scope_adjustment_text**: bool, whether to include scope
                adjustment text (default: True)
            * **flask**: bool, whether to generate a filename for Flask
                (default: False)
            * **filename**: str, custom filename for the PDF
                (default: generated based on yards and moa)
            * **create_target**: bool, whether to create the target PDF

        Example:
            target = Target(yards=100, moa=0.25, diagonal_thickness=0.125)
        """
        self.yards: float = kwargs.get("yards", 100)

        self.moa: float = kwargs.get("moa", 0.25)

        self.diagonal_thickness: float = kwargs.get("diagonal_thickness", 0.125)

        self.scope_adjustment_text: bool = kwargs.get(
            "scope_adjustment_text", True
        )

        self.flask: bool = kwargs.get("flask", False)

        self.filename: str = kwargs.get("filename", self._filename())

        self.margin: float = float(0.5 * inch)

        self.page_size: tuple[float, float] = (8.5 * inch, 11 * inch)

        self.create_on_init: bool = kwargs.get("create_target", True)

        if self.create_on_init:
            self._create_target()

    def _filename(self) -> str:
        """Generate a filename based on the target parameters."""
        filename = f"{str(self.yards).replace('.', '-')}_yards_"
        filename += f"{str(self.moa).replace('.', '-')}_moa.pdf"
        return filename

    def _flask_filename(self) -> str:
        """Generate a filename for Flask based on the target parameters."""
        return f"static/{self._filename()}"

    def _minute_of_angle(self) -> float:
        """Calculate the size of a MOA.

        Calculates the size of a minute of angle at the yardage property.

        Returns:
            float: Size of MOA in inches.
        """
        moa_per_degree = self.moa / 60.0
        inches = self.yards * 3 * 12
        moa_inches = inches * math.radians(moa_per_degree / 2) * 2
        return moa_inches

    def _draw_centered_text(
        self,
        c: canvas.Canvas,
        text: str,
        x: float,
        y: float,
        font="Helvetica",
        font_size=12,
        font_color="black",
    ) -> None:
        """Draw text centered around a given point."""
        c.setFont(font, font_size)
        c.setFillColor(font_color)
        text_width = c.stringWidth(text, font, font_size)
        # Assuming the height of a single line of text is roughly the font size
        text_height = font_size
        # Adjust x and y to center the text
        c.drawString(x - (text_width / 2), y - (text_height / 3), text)

    def _create_target(self) -> None:
        """Create a target PDF.

        Creates a PDF file with a shooting target grid based on the
        specified yards and MOA. The grid is centered on the page, and
        includes diagonal lines and optional scope adjustment text.
        """
        if self.flask:
            if not os.path.exists("static"):
                os.makedirs("static")
            filename = os.path.join("static", self.filename)
        else:
            filename = self.filename
        pdf = canvas.Canvas(filename, pagesize=self.page_size)

        # Set the title of the PDF
        pdf.setTitle(
            f"Target - {int(self.yards)} yards - {self.moa} MOA per click"
        )

        pdf.setStrokeColor("black")
        pdf.setLineWidth(1)
        pdf.setLineCap(2)

        grid_size = self._minute_of_angle()

        text = f"{self.moa} MOA grid ({grid_size:.3f} in) at {self.yards} yards"
        pdf.setFillColor("black")
        pdf.setFont("Helvetica", 12)
        self._draw_centered_text(pdf, text, self.page_size[0] / 2, 0.5 * inch)

        available_width = (self.page_size[0] - 2 * self.margin) / inch  # inches
        available_height = (
            self.page_size[1] - 2 * self.margin
        ) / inch  # inches
        num_rows = math.floor(((available_width / grid_size) // 2) * 2)
        num_cols = num_rows
        grid_width = num_cols * grid_size
        grid_height = num_rows * grid_size

        # Center the grid on the page
        x_start = self.margin + (available_width * inch - grid_width * inch) / 2
        y_start = (
            self.margin + (available_height * inch - grid_height * inch) / 2
        )

        x_center = self.margin + available_width / 2 * inch
        y_center = self.margin + available_height / 2 * inch

        if self.scope_adjustment_text:
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
        pdf.setLineWidth(
            self.diagonal_thickness * 72
        )  # Convert from inches to points
        pdf.line(
            x_start,
            y_start,
            x_start + grid_width * inch,
            y_start + grid_height * inch,
        )
        pdf.line(
            x_start + grid_width * inch,
            y_start,
            x_start,
            y_start + grid_height * inch,
        )

        # Scope Adjustment Text
        if self.scope_adjustment_text:
            scope_adjustment_text_size = 72
            self._draw_centered_text(
                pdf,
                "R/U",
                x_center - (x_center - x_start) / 2,
                y_center - (y_center - y_start) / 2,
                font_size=scope_adjustment_text_size,
                font_color="gray",
            )
            self._draw_centered_text(
                pdf,
                "R/D",
                x_center - (x_center - x_start) / 2,
                y_center + (y_center - y_start) / 2,
                font_size=scope_adjustment_text_size,
                font_color="gray",
            )
            self._draw_centered_text(
                pdf,
                "L/U",
                x_center + (x_center - x_start) / 2,
                y_center - (y_center - y_start) / 2,
                font_size=scope_adjustment_text_size,
                font_color="gray",
            )
            self._draw_centered_text(
                pdf,
                "L/D",
                x_center + (x_center - x_start) / 2,
                y_center + (y_center - y_start) / 2,
                font_size=scope_adjustment_text_size,
                font_color="gray",
            )
        pdf.save()
        log.info(f"Target PDF created: {self.filename}")

    def create_target(self) -> str:
        """Create the target PDF and return the filename."""
        self._create_target()
        return self.filename


if __name__ == "__main__":
    if not log.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
        handler.setFormatter(formatter)
        log.addHandler(handler)
    Target(
        yards=100,
        moa=0.25,
        diagonal_thickness=0.125,
        scope_adjustment_text=True,
    )
