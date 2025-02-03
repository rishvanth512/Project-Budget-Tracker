import sqlite3
import logging

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self._connect()

    def _connect(self):
        """
        Connect to the SQLite database.
        """
        try:
            self.conn = sqlite3.connect(self.db_path, timeout=10)
            self.conn.row_factory = sqlite3.Row  # Enable dictionary-like row access
            self._initialize_tables()
            logging.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")

    def _initialize_tables(self):
        """
        Initialize the projects, expenses, and categories tables if they don't already exist.
        """
        try:
            # Projects table
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                sloc REAL NOT NULL,
                reused REAL NOT NULL,
                modified REAL NOT NULL,
                effort REAL NOT NULL,
                schedule REAL NOT NULL,
                cost REAL NOT NULL,
                hourly_rate REAL NOT NULL,
                start_date TEXT NOT NULL
            );
            """)

            # Expenses table
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            );
            """)

            # Categories table
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
            """)

            # Prepopulate categories if empty
            self._prepopulate_categories()

            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error initializing database tables: {e}")

    def _prepopulate_categories(self):
        """
        Prepopulate the categories table with default categories.
        """
        default_categories = ["Development", "Tools", "Travel", "Miscellaneous"]
        try:
            for category in default_categories:
                self.conn.execute(
                    "INSERT OR IGNORE INTO categories (name) VALUES (?)",
                    (category,)
                )
        except sqlite3.Error as e:
            logging.error(f"Error prepopulating categories: {e}")

    def add_project(self, name, sloc, reused, modified, effort, schedule, cost, hourly_rate, start_date):
        """
        Add a new project to the database.
        """
        try:
            self.conn.execute(
                """
                INSERT INTO projects (name, sloc, reused, modified, effort, schedule, cost, hourly_rate, start_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (name, sloc, reused, modified, effort, schedule, cost, hourly_rate, start_date),
            )
            self.conn.commit()
            logging.info(f"Project '{name}' added successfully.")
        except sqlite3.Error as e:
            logging.error(f"Error adding project: {e}")
            raise

    def add_expense(self, project_id, description, amount, category, date):
        """
        Add an expense to the database.
        """
        try:
            self.conn.execute(
                """
                INSERT INTO expenses (project_id, description, amount, category, date)
                VALUES (?, ?, ?, ?, ?)
                """,
                (project_id, description, amount, category, date),
            )
            self.conn.commit()
            logging.info(f"Expense added to project ID {project_id}.")
        except sqlite3.Error as e:
            logging.error(f"Error adding expense: {e}")
            raise

    def get_projects(self):
        """
        Fetch all projects from the database.
        """
        try:
            cursor = self.conn.execute("SELECT * FROM projects")
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Error fetching projects: {e}")
            return []
            
    def get_project_details(self, project_id):
        """
        Fetch detailed information about a project by its ID.
        """
        try:
            cursor = self.conn.execute(
                "SELECT * FROM projects WHERE id = ?",
                (project_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logging.error(f"Error fetching project details: {e}")
            return None

    def get_project_id(self, project_name):
        """
        Get the project ID for the given project name.
        """
        try:
            cursor = self.conn.execute("SELECT id FROM projects WHERE name = ?", (project_name,))
            row = cursor.fetchone()
            return row["id"] if row else None
        except sqlite3.Error as e:
            logging.error(f"Error fetching project ID: {e}")
            return None

    def get_remaining_budget(self, project_name):
        """
        Calculate the remaining budget for a given project.
        """
        try:
            project_id = self.get_project_id(project_name)
            if not project_id:
                return 0.0

            # Get total budget
            cursor = self.conn.execute("SELECT cost FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            total_budget = row["cost"] if row else 0.0

            # Calculate total expenses
            cursor = self.conn.execute("SELECT SUM(amount) as total_expenses FROM expenses WHERE project_id = ?", (project_id,))
            row = cursor.fetchone()
            total_expenses = row["total_expenses"] if row["total_expenses"] else 0.0

            return total_budget - total_expenses
        except sqlite3.Error as e:
            logging.error(f"Error calculating remaining budget: {e}")
            return 0.0

    def get_expenses(self, project_id):
        """
        Fetch all expenses for a given project ID.
        """
        try:
            cursor = self.conn.execute("SELECT * FROM expenses WHERE project_id = ?", (project_id,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Error fetching expenses: {e}")
            return []

    def get_categories(self):
        """
        Fetch all categories from the database.
        """
        try:
            cursor = self.conn.execute("SELECT name FROM categories")
            return [row["name"] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Error fetching categories: {e}")
            return []

    def close(self):
        """
        Close the database connection.
        """
        try:
            if self.conn:
                self.conn.close()
                logging.info("Database connection closed.")
        except sqlite3.Error as e:
            logging.error(f"Error closing database connection: {e}")
