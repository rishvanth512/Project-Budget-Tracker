import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib import pyplot as plt
from database import Database
from datetime import datetime, timedelta
import logging
import numpy as np
from sklearn.linear_model import LinearRegression
from fpdf import FPDF

db = Database("static/data/projects.db")


def setup_expense_tab(expense_frame):
    """
    Set up the Expense Tracking Tab with all features, including:
    - AI-based recommendations
    - Spending trends
    - PDF report generation
    - Category management
    """

    def update_expense_project_list():
        try:
            project_list = db.get_projects()
            project_combo['values'] = [project["name"] for project in project_list]
        except Exception as e:
            logging.error(f"Error updating project list: {e}")

    def update_category_list():
        try:
            categories = db.get_categories()
            expense_category_combo['values'] = categories
        except Exception as e:
            logging.error(f"Error updating category list: {e}")

    def add_expense():
        try:
            selected_project = project_combo.get()
            if not selected_project:
                messagebox.showerror("Input Error", "Please select a project.")
                return

            description = expense_description_entry.get()
            amount = float(expense_amount_entry.get())
            category = expense_category_combo.get()
            date = expense_date_entry.get()

            if not date:
                messagebox.showerror("Input Error", "Please enter a valid date.")
                return

            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Input Error", "Invalid date format. Use YYYY-MM-DD.")
                return

            project_id = db.get_project_id(selected_project)
            db.add_expense(project_id, description, amount, category, date)

            messagebox.showinfo("Success", "Expense added successfully!")
            update_expense_history()
            update_remaining_budget()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid expense amount.")
        except Exception as e:
            logging.error(f"Error adding expense: {e}")
            messagebox.showerror("Error", "An error occurred while adding the expense.")

    def update_expense_history():
        selected_project = project_combo.get()
        if not selected_project:
            return

        try:
            project_id = db.get_project_id(selected_project)
            expenses = db.get_expenses(project_id)

            expense_history_list.delete(0, tk.END)
            for expense in expenses:
                expense_history_list.insert(
                    tk.END, f"{expense['description']} - ${expense['amount']} ({expense['category']}) on {expense['date']}"
                )
        except Exception as e:
            logging.error(f"Error updating expense history: {e}")

    def update_remaining_budget():
        try:
            selected_project = project_combo.get()
            if not selected_project:
                return

            remaining_budget = db.get_remaining_budget(selected_project)
            remaining_budget_label.config(text=f"Remaining Budget: $ {remaining_budget:.2f}")
        except Exception as e:
            logging.error(f"Error updating remaining budget: {e}")

    def show_expense_pie_chart():
        try:
            selected_project = project_combo.get()
            if not selected_project:
                messagebox.showerror("Input Error", "Please select a project.")
                return

            project_id = db.get_project_id(selected_project)
            total_budget = db.get_projects()[0]["cost"]
            remaining_budget = db.get_remaining_budget(selected_project)

            expenses = db.get_expenses(project_id)
            category_totals = {}
            for expense in expenses:
                category = expense["category"]
                amount = expense["amount"]
                category_totals[category] = category_totals.get(category, 0) + amount

            labels = list(category_totals.keys()) + ["Remaining"]
            values = list(category_totals.values()) + [remaining_budget]
            colors = ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#c2c2f0"][: len(labels)]

            plt.figure(figsize=(6, 6))
            plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors)
            plt.title(f"Expense Report for {selected_project}")
            plt.axis("equal")
            plt.show()
        except Exception as e:
            logging.error(f"Error generating expense report: {e}")

    def show_spending_trends():
        """
        Generate and display a bar chart showing monthly spending trends.
        """
        try:
            selected_project = project_combo.get()
            if not selected_project:
                messagebox.showerror("Input Error", "Please select a project.")
                return

            project_id = db.get_project_id(selected_project)
            expenses = db.get_expenses(project_id)

            if not expenses:
                messagebox.showerror("Data Error", "No expenses recorded for this project.")
                return

            monthly_totals = {}
            for expense in expenses:
                expense_date = datetime.strptime(expense["date"], "%Y-%m-%d")
                month_year = expense_date.strftime("%B %Y")
                monthly_totals[month_year] = monthly_totals.get(month_year, 0) + expense["amount"]

            months = list(monthly_totals.keys())
            spending = list(monthly_totals.values())

            plt.figure(figsize=(8, 5))
            plt.bar(months, spending, color="skyblue")
            plt.title(f"Monthly Spending Trends for {selected_project}")
            plt.xlabel("Month")
            plt.ylabel("Amount Spent ($)")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            logging.error(f"Error generating spending trends: {e}")
            messagebox.showerror("Error", "Could not generate spending trends.")

    def generate_ai_recommendations():
        """
        Generate AI-based budget recommendations with detailed suggestions.
        """
        try:
            selected_project = project_combo.get()
            if not selected_project:
                messagebox.showerror("Input Error", "Please select a project.")
                return

            project_id = db.get_project_id(selected_project)
            expenses = db.get_expenses(project_id)

            if not expenses:
                messagebox.showerror("Data Error", "No expenses recorded for this project.")
                return

            # Prepare data for Linear Regression
            dates = []
            amounts = []
            for expense in expenses:
                if expense["date"]:
                    date_obj = datetime.strptime(expense["date"], "%Y-%m-%d")
                    dates.append(date_obj.toordinal())  # Convert date to ordinal for regression
                    amounts.append(expense["amount"])

            if len(dates) < 2:
                messagebox.showerror("Data Error", "Not enough data points for prediction.")
                return

            X = np.array(dates).reshape(-1, 1)
            y = np.array(amounts)

            # Train Linear Regression model
            model = LinearRegression()
            model.fit(X, y)

            # Predict future expenses
            future_dates = [(datetime.now() + timedelta(days=i * 30)).toordinal() for i in range(1, 7)]
            future_expenses = model.predict(np.array(future_dates).reshape(-1, 1))

            # Fetch total budget and remaining budget
            total_budget = db.get_projects()[0]["cost"]
            remaining_budget = db.get_remaining_budget(selected_project)

            # Generate category-based recommendations
            category_totals = {}
            for expense in expenses:
                category = expense["category"]
                amount = expense["amount"]
                category_totals[category] = category_totals.get(category, 0) + amount

            # Calculate category allocation suggestions
            total_spent = sum(category_totals.values())
            suggestions = []
            for category, spent in category_totals.items():
                recommended = (spent / total_spent) * remaining_budget
                suggestions.append(f"Allocate ${recommended:.2f} to {category}.")

            # Cost efficiency suggestions based on project parameters
            recommendations = []
            if total_budget > 1000000:  # Example threshold
                recommendations.append("Consider reducing hourly rates or optimizing resource allocation.")
            if category_totals.get("Tools", 0) > (0.3 * total_budget):
                recommendations.append("Re-evaluate tool costs; consider cheaper alternatives.")
            if remaining_budget < 0:
                recommendations.append("Adjust budget or cut unnecessary expenditures to avoid a deficit.")
            if future_expenses[-1] > remaining_budget:
                recommendations.append("Plan for potential budget overrun in future months.")

            # Generate output
            prediction_text = "\n".join(
                [f"Month {i+1}: ${future_expenses[i]:.2f}" for i in range(len(future_expenses))]
            )
            category_suggestions_text = "\n".join(suggestions)
            cost_efficiency_text = "\n".join(recommendations) if recommendations else "Your budget is sufficient."

            messagebox.showinfo(
                "AI Recommendations",
                f"Predicted Future Spending:\n{prediction_text}\n\n"
                f"Category Allocation Suggestions:\n{category_suggestions_text}\n\n"
                f"Cost Efficiency Recommendations:\n{cost_efficiency_text}"
            )
        except Exception as e:
            logging.error(f"Error generating recommendations: {e}")
            messagebox.showerror("Error", "Could not generate recommendations.")

    def generate_expense_report():
        """
        Generate a comprehensive PDF report for the selected project.
        """
        try:
            selected_project = project_combo.get()
            if not selected_project:
                messagebox.showerror("Input Error", "Please select a project.")
                return

            project_id = db.get_project_id(selected_project)
            project_details = db.get_project_details(project_id)
            expenses = db.get_expenses(project_id)
            remaining_budget = db.get_remaining_budget(selected_project)

            # Initialize PDF
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Title
            pdf.set_font("Arial", style="B", size=16)
            pdf.cell(200, 10, txt=f"Expense Report for Project: {selected_project}", ln=True, align="C")
            pdf.ln(10)

            # Project Details
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(200, 10, txt="Project Details:", ln=True, align="L")
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Name: {project_details['name']}", ln=True, align="L")
            pdf.cell(200, 10, txt=f"Start Date: {project_details['start_date']}", ln=True, align="L")
            pdf.cell(200, 10, txt=f"Total Budget: ${project_details['cost']:.2f}", ln=True, align="L")
            pdf.cell(200, 10, txt=f"Remaining Budget: ${remaining_budget:.2f}", ln=True, align="L")
            pdf.ln(10)

            # Expense History
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(200, 10, txt="Expense History:", ln=True, align="L")
            pdf.set_font("Arial", size=12)
            if expenses:
                for expense in expenses:
                    pdf.cell(200, 10, txt=f"{expense['description']} - ${expense['amount']} ({expense['category']}) on {expense['date']}", ln=True, align="L")
            else:
                pdf.cell(200, 10, txt="No expenses recorded.", ln=True, align="L")
            pdf.ln(10)

            # Save PDF
            report_path = f"{selected_project}_Expense_Report.pdf"
            pdf.output(report_path)
            messagebox.showinfo("Success", f"Report generated successfully: {report_path}")
        except Exception as e:
            logging.error(f"Error generating report: {e}")
            messagebox.showerror("Error", "Could not generate report.")

    # Widgets for Expense Tab
    tk.Label(expense_frame, text="Select Project:").grid(row=0, column=0, padx=10, pady=5)
    project_combo = ttk.Combobox(expense_frame, postcommand=update_expense_project_list)
    project_combo.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(expense_frame, text="Expense Description:").grid(row=1, column=0, padx=10, pady=5)
    expense_description_entry = tk.Entry(expense_frame)
    expense_description_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(expense_frame, text="Expense Amount ($):").grid(row=2, column=0, padx=10, pady=5)
    expense_amount_entry = tk.Entry(expense_frame)
    expense_amount_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(expense_frame, text="Category:").grid(row=3, column=0, padx=10, pady=5)
    expense_category_combo = ttk.Combobox(expense_frame, postcommand=update_category_list)
    expense_category_combo.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(expense_frame, text="Expense Date (YYYY-MM-DD):").grid(row=4, column=0, padx=10, pady=5)
    expense_date_entry = tk.Entry(expense_frame)
    expense_date_entry.grid(row=4, column=1, padx=10, pady=5)
    expense_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    add_expense_button = tk.Button(expense_frame, text="Add Expense", command=add_expense)
    add_expense_button.grid(row=5, column=0, columnspan=2, pady=10)

    tk.Label(expense_frame, text="Expense History:").grid(row=6, column=0, padx=10, pady=5)
    expense_history_list = tk.Listbox(expense_frame, height=10, width=50)
    expense_history_list.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

    remaining_budget_label = tk.Label(expense_frame, text="Remaining Budget: $0.00")
    remaining_budget_label.grid(row=8, column=0, columnspan=2, pady=10)

    show_pie_button = tk.Button(expense_frame, text="Show Expense Pie Chart", command=show_expense_pie_chart)
    show_pie_button.grid(row=9, column=0, columnspan=2, pady=10)

    show_trends_button = tk.Button(expense_frame, text="Show Spending Trends", command=show_spending_trends)
    show_trends_button.grid(row=10, column=0, columnspan=2, pady=10)

    ai_recommendation_button = tk.Button(expense_frame, text="Generate AI Recommendations", command=generate_ai_recommendations)
    ai_recommendation_button.grid(row=11, column=0, columnspan=2, pady=10)

    generate_report_button = tk.Button(expense_frame, text="Generate Expense Report", command=generate_expense_report)
    generate_report_button.grid(row=12, column=0, columnspan=2, pady=10)
