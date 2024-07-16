import math

from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


class target:
    def __init__(
        self,
        yards: float = 100,
        MOA: float = 0.25,
        diagonal_thickness: float = 0.125,
        scope_adjustment_text: bool = True,
    ) -> None:
        """Initialize the target object with the given parameters."""
        self.filename: str = (
            f"static/{int(yards)}yards_{str(MOA).replace('.','-')}moa.pdf"
        )
        self.yards: float = yards
        self.MOA: float = MOA
        self.diagonal_thickness: float = diagonal_thickness
        self.scope_adjustment_text: bool = scope_adjustment_text
        self.page_size: tuple[float, float] = (8.5 * inch, 11 * inch)
        self.pdf: canvas = canvas.Canvas(self.filename, pagesize=self.page_size)
        self.margin: float = 0.5 * inch

    def minute_of_angle(self) -> float:
        """Calculate the size of a minute of angle (MOA) in inches at a given yardage."""

        moa_per_degree = self.MOA / 60.0
        inches = self.yards * 3 * 12
        moa_inches = inches * math.radians(moa_per_degree / 2) * 2
        return moa_inches

    def draw_centered_text(
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

    def create_target(self) -> None:
        """Create a target PDF with a grid spacing of a specified MOA click at a given yardage."""

        # Set the title of the PDF
        self.pdf.setTitle(
            f"Target - {int(self.yards)} yards - {self.MOA} MOA per click"
        )

        self.pdf.setStrokeColor("black")
        self.pdf.setLineWidth(1)
        self.pdf.setLineCap(2)

        grid_size = self.minute_of_angle()

        text = f"{self.MOA} MOA grid ({grid_size:.3f} in) at {self.yards} yards"
        self.pdf.setFillColor("black")
        self.pdf.setFont("Helvetica", 12)
        self.draw_centered_text(self.pdf, text, self.page_size[0] / 2, 0.5 * inch)

        available_width = (self.page_size[0] - 2 * self.margin) / inch  # inches
        available_height = (self.page_size[1] - 2 * self.margin) / inch  # inches
        num_rows = math.floor(((available_width / grid_size) // 2) * 2)
        num_cols = num_rows
        grid_width = num_cols * grid_size
        grid_height = num_rows * grid_size

        # Center the grid on the page
        x_start = self.margin + (available_width * inch - grid_width * inch) / 2
        y_start = self.margin + (available_height * inch - grid_height * inch) / 2

        x_center = self.margin + available_width / 2 * inch
        y_center = self.margin + available_height / 2 * inch

        if self.scope_adjustment_text:
            # Quadrant lines
            self.pdf.setStrokeColor("gray")
            self.pdf.setLineWidth(5)
            self.pdf.line(x_center, y_start, x_center, y_start + grid_height * inch)
            self.pdf.line(x_start, y_center, x_start + grid_width * inch, y_center)
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
            x_start, y_start, x_start + grid_width * inch, y_start + grid_height * inch
        )
        self.pdf.line(
            x_start + grid_width * inch, y_start, x_start, y_start + grid_height * inch
        )

        # Scope Adjustment Text
        if self.scope_adjustment_text:
            scope_adjustment_text_size = 72
            self.draw_centered_text(
                self.pdf,
                "R/U",
                x_center - (x_center - x_start) / 2,
                y_center - (y_center - y_start) / 2,
                font_size=scope_adjustment_text_size,
                font_color="gray",
            )
            self.draw_centered_text(
                self.pdf,
                "R/D",
                x_center - (x_center - x_start) / 2,
                y_center + (y_center - y_start) / 2,
                font_size=scope_adjustment_text_size,
                font_color="gray",
            )
            self.draw_centered_text(
                self.pdf,
                "L/U",
                x_center + (x_center - x_start) / 2,
                y_center - (y_center - y_start) / 2,
                font_size=scope_adjustment_text_size,
                font_color="gray",
            )
            self.draw_centered_text(
                self.pdf,
                "L/D",
                x_center + (x_center - x_start) / 2,
                y_center + (y_center - y_start) / 2,
                font_size=scope_adjustment_text_size,
                font_color="gray",
            )

        self.pdf.save()
