"""Module containing the Target class, used for generating PDF targets."""

from math import floor, radians

from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


class Target:
    """Initialize the target object with the given parameters."""
    def __init__(self, **kwargs):
        """Initialize the target object with the given parameters.

        Args:
            **kwargs: Arbitrary keyword arguments.
                * **yards**: The distance in yards for the target.
                Defaults to 100.
                * **MOA**: The minute of angle (MOA) per click.
                Defaults to 0.25.
                * **diagonal_thickness**: The thickness of the diagonal lines in
                  inches. Defaults to 0.125.
                * **scope_adjustment_text**: Whether to include scope adjustment
                  text. Defaults to True.
                * **page_size**: The size of the PDF page. Defaults to
                  (8.5 * inch, 11 * inch).
                * **margin**: The margin around the grid in inches.
                  Defaults to 0.5 * inch.
                * **docker**: Whether running in a Docker container.
                Defaults to False.
                * **filename**: The name of the output PDF file.
        """
        self.yards: float = kwargs.get("yards", 100)
        self.MOA: float = kwargs.get("MOA", 0.25)
        self.diagonal_thickness: float = kwargs.get(
            "diagonal_thickness",
            0.125
        )
        self.scope_adjustment_text: bool = kwargs.get(
            "scope_adjustment_text",
            True
        )
        self.page_size: tuple[float, float] = kwargs.get(
            "page_size",
            (8.5 * inch, 11 * inch)
        )
        self.margin: float = kwargs.get(
            "margin",
            0.5 * inch
        )
        self.flask: bool = kwargs.get("flask", False)
        self.filename = kwargs.get(
            "filename",
            self._flask_filename() if self.flask else self._filename()
        )
        self.pdf: canvas = canvas.Canvas(self.filename, pagesize=self.page_size)

    def _filename(self) -> str:
        """Generate the filename used for the PDF.

        Returns:
            str: The filename for the PDF
        """
        filename: str = str(self.yards).replace(".", "-") + "yards_"
        filename += str(self.MOA).replace(".", "-") + "moa.pdf"
        return filename

    def _flask_filename(self) -> str:
        """Generate the filename used in the Flask app.

        Returns:
            filename (str): The Docker-compatible filename
        """
        filename: str = "static/"
        filename += str(self.yards).replace(".", "-") + "yards_"
        filename += str(self.MOA).replace(".", "-") + "moa.pdf"
        return filename

    def _minute_of_angle(self) -> float:
        """Calculate the size of a MOA in inches at a given yardage.

        Returns:
            moa_inches (float): The size of the MOA in inches at the specified
                yardage.
        """
        moa_per_degree = self.MOA / 60.0
        inches = self.yards * 3 * 12
        moa_inches = inches * radians(moa_per_degree / 2) * 2
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
        """Draw text centered around a given point.

        Args:
            c (canvas.Canvas): The canvas to draw on.
            text (str): The text to draw.
            x (float): The x-coordinate of the center point.
            y (float): The y-coordinate of the center point.
            font (str, optional): The font to use. Defaults to "Helvetica".
            font_size (int, optional): The font size to use. Defaults to 12.
            font_color (str, optional): The font color to use.
                Defaults to "black".
        """
        c.setFont(font, font_size)
        c.setFillColor(font_color)
        text_width = c.stringWidth(text, font, font_size)
        # Assuming the height of a single line of text is roughly the font size
        text_height = font_size
        # Adjust x and y to center the text
        c.drawString(x - (text_width / 2), y - (text_height / 3), text)

    def create_target(self) -> None:
        """Create a target PDF with the class parameters."""
        # Set the title of the PDF
        self.pdf.setTitle(
            f"Target - {int(self.yards)} yards - {self.MOA} MOA per click"
        )

        self.pdf.setStrokeColor("black")
        self.pdf.setLineWidth(1)
        self.pdf.setLineCap(2)

        grid_size = self._minute_of_angle()

        text = f"{self.MOA} MOA grid ({grid_size:.3f} in) at {self.yards} yards"
        self.pdf.setFillColor("black")
        self.pdf.setFont("Helvetica", 12)
        self._draw_centered_text(
            self.pdf, text, self.page_size[0] / 2, 0.5 * inch)

        available_width = (self.page_size[0] - 2 * self.margin) / inch
        available_height = (self.page_size[1] - 2 * self.margin) / inch
        num_rows = floor(((available_width / grid_size) // 2) * 2)
        num_cols = num_rows
        grid_width = num_cols * grid_size
        grid_height = num_rows * grid_size

        # Center the grid on the page
        x_start = self.margin + (
            available_width * inch - grid_width * inch) / 2
        y_start = self.margin + (
            available_height * inch - grid_height * inch) / 2

        x_center = self.margin + available_width / 2 * inch
        y_center = self.margin + available_height / 2 * inch

        if self.scope_adjustment_text:
            # Quadrant lines
            self.pdf.setStrokeColor("gray")
            self.pdf.setLineWidth(5)
            self.pdf.line(x_center,
                          y_start,
                          x_center,
                          y_start + grid_height * inch)
            self.pdf.line(x_start,
                          y_center,
                          x_start + grid_width * inch, y_center)
            self.pdf.setStrokeColor("black")
            self.pdf.setLineWidth(1)

        # Draw horizontal lines
        for i in range(num_rows + 1):
            y = y_start + i * grid_size * inch
            self.pdf.line(x_start, y, x_start + grid_width * inch, y)

        # Draw vertical lines
        for i in range(num_cols + 1):
            x = x_start + i * grid_size * inch
            self.pdf.line(x, y_start, x, y_start + grid_height * inch)

        # Draw diagonal lines
        self.pdf.setLineWidth(
            self.diagonal_thickness * 72
        )  # Convert from inches to points
        self.pdf.line(
            x_start,
            y_start,
            x_start + grid_width * inch,
            y_start + grid_height * inch
        )
        self.pdf.line(
            x_start + grid_width * inch,
            y_start,
            x_start,
            y_start + grid_height * inch
        )

        # Scope Adjustment Text
        if self.scope_adjustment_text:
            scope_adjustment_text_size = 72
            self._draw_centered_text(
                self.pdf,
                "R/U",
                x_center - (x_center - x_start) / 2,
                y_center - (y_center - y_start) / 2,
                font_size=scope_adjustment_text_size,
                font_color="gray",
            )
            self._draw_centered_text(
                self.pdf,
                "R/D",
                x_center - (x_center - x_start) / 2,
                y_center + (y_center - y_start) / 2,
                font_size=scope_adjustment_text_size,
                font_color="gray",
            )
            self._draw_centered_text(
                self.pdf,
                "L/U",
                x_center + (x_center - x_start) / 2,
                y_center - (y_center - y_start) / 2,
                font_size=scope_adjustment_text_size,
                font_color="gray",
            )
            self._draw_centered_text(
                self.pdf,
                "L/D",
                x_center + (x_center - x_start) / 2,
                y_center + (y_center - y_start) / 2,
                font_size=scope_adjustment_text_size,
                font_color="gray",
            )

        self.pdf.save()


if __name__ == "__main__":
    target = Target(yardage=100,
                    MOA=0.25,
                    diagonal_thickness=0.125,
                    scope_adjustment_text=True,
                    filename="test.pdf")
    target.create_target()

