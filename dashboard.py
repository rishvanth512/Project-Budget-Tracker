import tkinter as tk
from database import Database
import logging

db = Database("static/data/projects.db")

def setup_dashboard_tab(dashboard_frame):
    """
    Set up the Dashboard Tab.
    """
    def update_dashboard():
        """
        Update the dashboard with project summaries.
        """
        try:
            project_summaries = db.get_projects()
            dashboard_list.delete(0, tk.END)

            for project in project_summaries:
                project_status = (
                    f"Project: {project['name']}, "
                    f"Total Budget: ${project['cost']:.2f}, "
                    f"Remaining: ${db.get_remaining_budget(project['name']):.2f}"
                )
                dashboard_list.insert(tk.END, project_status)
            logging.info("Dashboard updated successfully.")
        except Exception as e:
            logging.error(f"Error updating dashboard: {e}")

    # Dashboard Widgets
    tk.Label(dashboard_frame, text="Project Overview:").pack(pady=10)
    dashboard_list = tk.Listbox(dashboard_frame, width=80, height=15)
    dashboard_list.pack(pady=10)

    update_dashboard_button = tk.Button(dashboard_frame, text="Refresh Dashboard", command=update_dashboard)
    update_dashboard_button.pack(pady=10)