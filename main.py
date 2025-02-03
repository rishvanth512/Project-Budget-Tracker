import tkinter as tk
from tkinter import ttk
from budget import setup_budget_tab
from expense import setup_expense_tab
from dashboard import setup_dashboard_tab
from utils import setup_logging
import logging

# Set up logging
setup_logging()

# Initialize the main application
app = tk.Tk()
app.title("Modular Project Budget Estimator and Tracker")
notebook = ttk.Notebook(app)
notebook.pack(expand=True, fill="both")

# Add tabs
budget_frame = ttk.Frame(notebook)
expense_frame = ttk.Frame(notebook)
dashboard_frame = ttk.Frame(notebook)

notebook.add(budget_frame, text="Budget Estimation")
notebook.add(expense_frame, text="Expense Tracking")
notebook.add(dashboard_frame, text="Dashboard")

# Set up individual tabs
try:
    setup_budget_tab(budget_frame)
    logging.info("Budget tab initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize Budget tab: {e}")

try:
    setup_expense_tab(expense_frame)
    logging.info("Expense tab initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize Expense tab: {e}")

try:
    setup_dashboard_tab(dashboard_frame)
    logging.info("Dashboard tab initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize Dashboard tab: {e}")

# Run the application
if __name__ == "__main__":
    try:
        app.mainloop()
        logging.info("Application closed successfully.")
    except Exception as e:
        logging.error(f"Application crashed: {e}")
