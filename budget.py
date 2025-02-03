import tkinter as tk
from tkinter import ttk, messagebox
from cocomo_calculator import COCOMOCalculator
from database import Database
import logging

cocomo = COCOMOCalculator()
db = Database("static/data/projects.db")

def setup_budget_tab(budget_frame):
    """
    Set up the Budget Estimation Tab.
    """
    project_details = {}

    def calculate_budget():
        """
        Calculate the budget based on COCOMO II model.
        """
        try:
            logging.info("Starting budget calculation.")
            sloc = float(sloc_entry.get())
            reused = float(reused_entry.get())
            modified = float(modified_entry.get())
            hourly_rate = float(hourly_rate_entry.get())

            scale_factors = {
                "Precedentedness": cocomo.scale_factors[precedence_combo.get()],
                "Development Flexibility": cocomo.scale_factors[flexibility_combo.get()],
                "Process Maturity": cocomo.scale_factors[maturity_combo.get()]
            }
            effort_multipliers = {
                "Required Reliability": cocomo.effort_multipliers[reliability_combo.get()],
                "Database Size": cocomo.effort_multipliers[database_combo.get()],
                "Product Complexity": cocomo.effort_multipliers[complexity_combo.get()]
            }

            effort = cocomo.calculate_effort(sloc, reused, modified, scale_factors, effort_multipliers)
            schedule = cocomo.calculate_schedule(effort)
            total_cost = effort * hourly_rate * 160

            project_details.clear()
            project_details.update({
                "sloc": sloc,
                "reused": reused,
                "modified": modified,
                "effort": effort,
                "schedule": schedule,
                "cost": total_cost,
                "hourly_rate": hourly_rate
            })

            effort_label.config(text=f"Effort: {effort:.2f} Person-Months")
            schedule_label.config(text=f"Schedule: {schedule:.2f} Months")
            cost_label.config(text=f"Total Cost: ${total_cost:.2f}")

            logging.info("Budget calculation successful.")
        except Exception as e:
            logging.error(f"Error in budget calculation: {e}")
            messagebox.showerror("Error", "Invalid inputs for budget calculation.")

    def start_project():
        """
        Add a new project to the database after calculating the budget.
        """
        project_name = project_name_entry.get()
        start_date = start_date_entry.get()

        if not project_name:
            messagebox.showerror("Input Error", "Please provide a project name.")
            return

        if not start_date:
            messagebox.showerror("Input Error", "Please provide a start date.")
            return

        if "cost" not in project_details:
            messagebox.showerror("Calculation Error", "Please estimate the budget first.")
            return

        try:
            db.add_project(
                project_name,
                project_details["sloc"],
                project_details["reused"],
                project_details["modified"],
                project_details["effort"],
                project_details["schedule"],
                project_details["cost"],
                project_details["hourly_rate"],
                start_date
            )
            messagebox.showinfo("Project Created", f"Project '{project_name}' has been created.")
            logging.info(f"Project '{project_name}' added successfully.")
        except Exception as e:
            logging.error(f"Error adding project: {e}")
            messagebox.showerror("Error", "Failed to add the project to the database.")

    # Widgets for the Budget Tab
    tk.Label(budget_frame, text="Software Size (SLOC):").grid(row=0, column=0, padx=10, pady=5)
    sloc_entry = tk.Entry(budget_frame)
    sloc_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(budget_frame, text="Reused Code (%):").grid(row=1, column=0, padx=10, pady=5)
    reused_entry = tk.Entry(budget_frame)
    reused_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(budget_frame, text="Modified Code (%):").grid(row=2, column=0, padx=10, pady=5)
    modified_entry = tk.Entry(budget_frame)
    modified_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(budget_frame, text="Hourly Rate ($):").grid(row=3, column=0, padx=10, pady=5)
    hourly_rate_entry = tk.Entry(budget_frame)
    hourly_rate_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(budget_frame, text="Precedentedness:").grid(row=4, column=0, padx=10, pady=5)
    precedence_combo = ttk.Combobox(budget_frame, values=["Nominal", "Low", "High"])
    precedence_combo.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(budget_frame, text="Development Flexibility:").grid(row=5, column=0, padx=10, pady=5)
    flexibility_combo = ttk.Combobox(budget_frame, values=["Nominal", "Low", "High"])
    flexibility_combo.grid(row=5, column=1, padx=10, pady=5)

    tk.Label(budget_frame, text="Process Maturity:").grid(row=6, column=0, padx=10, pady=5)
    maturity_combo = ttk.Combobox(budget_frame, values=["Nominal", "Low", "High"])
    maturity_combo.grid(row=6, column=1, padx=10, pady=5)

    tk.Label(budget_frame, text="Required Reliability:").grid(row=7, column=0, padx=10, pady=5)
    reliability_combo = ttk.Combobox(budget_frame, values=["Nominal", "Low", "High"])
    reliability_combo.grid(row=7, column=1, padx=10, pady=5)

    tk.Label(budget_frame, text="Database Size:").grid(row=8, column=0, padx=10, pady=5)
    database_combo = ttk.Combobox(budget_frame, values=["Nominal", "Low", "High"])
    database_combo.grid(row=8, column=1, padx=10, pady=5)

    tk.Label(budget_frame, text="Product Complexity:").grid(row=9, column=0, padx=10, pady=5)
    complexity_combo = ttk.Combobox(budget_frame, values=["Nominal", "Low", "High"])
    complexity_combo.grid(row=9, column=1, padx=10, pady=5)

    tk.Label(budget_frame, text="Project Name:").grid(row=10, column=0, padx=10, pady=5)
    project_name_entry = tk.Entry(budget_frame)
    project_name_entry.grid(row=10, column=1, padx=10, pady=5)

    tk.Label(budget_frame, text="Start Date (YYYY-MM-DD):").grid(row=11, column=0, padx=10, pady=5)
    start_date_entry = tk.Entry(budget_frame)
    start_date_entry.grid(row=11, column=1, padx=10, pady=5)

    calculate_button = tk.Button(budget_frame, text="Calculate", command=calculate_budget)
    calculate_button.grid(row=12, column=0, columnspan=2, pady=10)

    start_project_button = tk.Button(budget_frame, text="Start Project", command=start_project)
    start_project_button.grid(row=13, column=0, columnspan=2, pady=10)

    effort_label = tk.Label(budget_frame, text="Effort: 0.00 Person-Months")
    effort_label.grid(row=14, column=0, columnspan=2, pady=5)

    schedule_label = tk.Label(budget_frame, text="Schedule: 0.00 Months")
    schedule_label.grid(row=15, column=0, columnspan=2, pady=5)

    cost_label = tk.Label(budget_frame, text="Total Cost: $0.00")
    cost_label.grid(row=16, column=0, columnspan=2, pady=5)
