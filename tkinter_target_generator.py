"""Provides a GUI for generating shooting targets."""

import logging
import os
import sys
import tkinter as tk
from tkinter import messagebox

from pdf_gen import Target

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class TargetGeneratorApp(tk.Tk):
    """Main application class for the target generator GUI."""

    def __init__(self) -> None:
        """Initialize the application."""
        super().__init__()
        icon_path = resource_path("static/favicon.ico")
        self.iconbitmap(icon_path)
        self.title("Target Generator")
        self.geometry("400x300")
        self.create_widgets()

    def create_widgets(self) -> None:
        """Create and place widgets in the main window."""
        tk.Label(self, text="Yards:").pack(pady=5)
        self.yards_entry = tk.Entry(self)
        self.yards_entry.pack(pady=5)

        tk.Label(self, text="MOA:").pack(pady=5)
        self.moa_entry = tk.Entry(self)
        self.moa_entry.pack(pady=5)

        tk.Label(self, text="Diagonal Thickness:").pack(pady=5)
        self.diagonal_thickness_entry = tk.Entry(self)
        self.diagonal_thickness_entry.pack(pady=5)

        self.scope_adjustment_var = tk.BooleanVar(value=True)
        self.scope_adjustment_check = tk.Checkbutton(
            self,
            text="Add Scope Adjustment Text",
            variable=self.scope_adjustment_var,
        )
        self.scope_adjustment_check.pack(pady=5)

        self.generate_button = tk.Button(
            self, text="Generate Target", command=self.generate_target
        )
        self.generate_button.pack(pady=20)

    def generate_target(self) -> None:
        """Handle target generation logic."""
        yards = self.yards_entry.get()
        moa = self.moa_entry.get()
        diagonal_thickness = self.diagonal_thickness_entry.get()
        scope_adjustment = self.scope_adjustment_var.get()

        # Here you would call the target generation logic
        log.info(
            f"Generating target with yards={yards}, moa={moa}, "
            f"diagonal_thickness={diagonal_thickness}, "
            f"scope_adjustment={scope_adjustment}"
        )

        try:
            target = Target(
                yards=float(yards),
                moa=float(moa),
                diagonal_thickness=float(diagonal_thickness),
                scope_adjustment_text=scope_adjustment,
                flask=False,  # Set to False for GUI
            )
            filename = target.create_target()
            log.info(f"Target generated: {filename}")
            messagebox.showinfo("Success", f"Target saved as {filename}")
        except Exception as e:
            log.error(f"Error generating target: {e}")
            messagebox.showerror("Error", f"Failed to generate target: {e}")


if __name__ == "__main__":
    """Run the target generator application."""
    if not log.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
        handler.setFormatter(formatter)
        log.addHandler(handler)
    app = TargetGeneratorApp()
    app.mainloop()
