import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Define the constant for the JSON file path
TASKS_JSON = "tasks.json"

# ================================================Stage 1:CRUD Ops================================================

# Global task list
tasks = []

# Get input from user with validation
def get_input(prompt, allow_empty=False):
    while True:
        value = input(prompt).strip()
        if allow_empty or value:
            return value
        print("Input cannot be empty. Try again.")

# Ask for task priority and validate
def get_priority():
    while True:
        priority = input("Priority (Low/Medium/High): ").strip().lower()
        if priority in ["low", "medium", "high"]:
            return priority.capitalize()
        print("Invalid priority! Please enter Low, Medium, or High.")

# Ask for date input and validate format
def get_valid_date():
    while True:
        date_input = input("Due Date (YYYY-MM-DD): ").strip()
        if validate_date_format(date_input):
            return date_input
        else:
            print("Invalid date format! Please use YYYY-MM-DD.")

# Check if date format is valid
def validate_date_format(date_str):
    parts = date_str.split("-")
    if len(parts) != 3:
        return False
    year, month, day = parts
    if not (year.isdigit() and month.isdigit() and day.isdigit()):
        return False
    year, month, day = int(year), int(month), int(day)
    if not (1 <= month <= 12):
        return False
    days_in_month = [31, 29 if is_leap_year(year) else 28, 31, 30, 31, 30,
                     31, 31, 30, 31, 30, 31]
    return 1 <= day <= days_in_month[month - 1]

# Check if a year is a leap year
def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

# Convert any task to dictionary format
def ensure_task_dict(task):
    # If it's a list, convert to dictionary
    if type(task) == list and len(task) >= 4:
        return {
            "name": task[0],
            "description": task[1],
            "priority": task[2],
            "due_date": task[3]
        }
    # Already a dictionary
    return task

# CRUD Operations using list
def add_task():
    name = get_input("Task Name: ")
    desc = get_input("Description: ")
    priority = get_priority()
    date = get_valid_date()
    
    # Create task directly as dictionary
    task = {
        "name": name,
        "description": desc,
        "priority": priority,
        "due_date": date
    }
    tasks.append(task)
    save_tasks_to_file()
    save_tasks_to_json()
    print("Task Added Successfully!\n")

def show_tasks():
    if not tasks:
        print("No tasks found.\n")
        return
    
    for index, task in enumerate(tasks, start=1):
        # Convert task to dictionary if needed
        task_dict = ensure_task_dict(task)
        print(f"{index}. {task_dict['name']} - {task_dict['description']} (Priority: {task_dict['priority']}, Due: {task_dict['due_date']})")
    print()

def update_task():
    show_tasks()
    if not tasks:
        return
    task_number = get_input("Enter task number to update: ")
    if not task_number.isdigit() or not (1 <= int(task_number) <= len(tasks)):
        print("Invalid Task Number!\n")
        return
    
    index = int(task_number) - 1
    task = ensure_task_dict(tasks[index])
    
    new_name = get_input("New Name (Enter to skip): ", allow_empty=True)
    if new_name:
        task['name'] = new_name
    new_desc = get_input("New Description (Enter to skip): ", allow_empty=True)
    if new_desc:
        task['description'] = new_desc
    priority_input = get_input("New Priority (Low/Medium/High) (Enter to skip): ", allow_empty=True).lower()
    if priority_input in ["low", "medium", "high"]:
        task['priority'] = priority_input.capitalize()
    elif priority_input != "":
        print("Invalid priority! Keeping previous value.")
    date_input = get_input("New Due Date (YYYY-MM-DD) (Enter to skip): ", allow_empty=True)
    if date_input and validate_date_format(date_input):
        task['due_date'] = date_input
    elif date_input:
        print("Invalid date format! Keeping previous value.")
    
    # Ensure the task is saved back in dictionary format
    tasks[index] = task
    save_tasks_to_file()
    save_tasks_to_json()
    print("Task Updated Successfully!\n")

def delete_task():
    show_tasks()
    if not tasks:
        return
    task_number = get_input("Enter task number to delete: ")
    if not task_number.isdigit() or not (1 <= int(task_number) <= len(tasks)):
        print("Invalid Task Number!\n")
        return
    tasks.pop(int(task_number) - 1)
    save_tasks_to_file()
    save_tasks_to_json()
    print("Task Deleted Successfully!\n")

# ==============================================Stage 2: Text File Handling ==============================================

def load_tasks_from_file():
    try:
        with open("task_save.txt", "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 4:
                    tasks.append({
                        "name": parts[0],
                        "description": parts[1],
                        "priority": parts[2],
                        "due_date": parts[3]
                    })
    except FileNotFoundError:
        pass

def save_tasks_to_file():
    with open("task_save.txt", "w") as f:
        for task in tasks:
            task_dict = ensure_task_dict(task)
            f.write(f"{task_dict['name']},{task_dict['description']},{task_dict['priority']},{task_dict['due_date']}\n")
# ==============================================Stage 3: json ============================================================

def load_tasks_from_json():
    # Loads tasks with more structured format
    global tasks
    try:
        if os.path.exists(TASKS_JSON):
            with open(TASKS_JSON, "r") as file:
                file_content = file.read().strip()
                if file_content:  # Check if file is not empty
                    try:
                        loaded_tasks = json.loads(file_content)
                        # Convert all tasks to a standard format (dictionary)
                        for i, item in enumerate(loaded_tasks):
                            loaded_tasks[i] = ensure_task_dict(item)
                        tasks = loaded_tasks
                        # Removed the "Task list loaded from JSON file" message
                    except json.JSONDecodeError:
                        print("Invalid JSON format in file, starting with an empty list...")
                        tasks = []
                else:
                    print("JSON file is empty, starting with an empty list...")
                    tasks = []
        else:
            print("JSON file doesn't exist, starting with an empty list...")
            tasks = []
    except Exception as e:
        print(f"Error loading JSON file: {str(e)}")
        tasks = []

def save_tasks_to_json():
    try:
        # Convert all tasks to dictionary format for consistency
        tasks_to_save = []
        for task in tasks:
            tasks_to_save.append(ensure_task_dict(task))
        
        with open(TASKS_JSON, "w") as file:
            json.dump(tasks_to_save, file, indent=4)
        print("Tasks saved to JSON file successfully")
    except Exception as e:
        print(f"Error saving to JSON file: {str(e)}")


# Define the Task class to represent each task
class Task:
    # Constructor to initialize all task properties.
    def __init__(self, name, description, priority, due_date):
        self.name = name
        self.description = description
        self.priority = priority
        self.due_date = due_date

    def to_dict(self):
        # Converts Task object to dictionary format for serialization.
        return {
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date
        }


# Define the TaskManager class to handle task operations
class TaskManager:
    def __init__(self, json_file=TASKS_JSON):
        self.tasks = []
        self.json_file = json_file
        self.load_tasks_from_json()
    
    def load_tasks_from_json(self):
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, "r") as file:
                    file_content = file.read().strip()
                    if file_content:  # Check if file is not empty
                        try:
                            task_dicts = json.loads(file_content)
                            self.tasks = []
                            for task_data in task_dicts:
                                # Handle both list and dictionary formats uniformly
                                if type(task_data) == list and len(task_data) >= 4:
                                    new_task = Task(task_data[0], task_data[1], task_data[2], task_data[3])
                                else:
                                    task_dict = ensure_task_dict(task_data)
                                    new_task = Task(
                                        task_dict.get("name", "Untitled"),
                                        task_dict.get("description", ""),
                                        task_dict.get("priority", "Medium"),
                                        task_dict.get("due_date", "2025-01-01")
                                    )
                                self.tasks.append(new_task)
                            # Removed the success message here
                        except json.JSONDecodeError:
                            print("Invalid JSON format in file, starting with empty tasks")
                            self.tasks = []
                    else:
                        print("JSON file is empty, starting with empty tasks")
                        self.tasks = []
            else:
                print("TaskManager: JSON file doesn't exist, starting with empty tasks")
                self.tasks = []
        except Exception as e:
            print(f"Error loading JSON file: {str(e)}")
            self.tasks = []
    
    def get_filtered_tasks(self, name_filter=None, priority_filter=None, due_date_filter=None):
        filtered_tasks = self.tasks
        
        if name_filter:
            name_filter = name_filter.lower()
            result = []
            for task in filtered_tasks:
                if name_filter in task.name.lower():
                    result.append(task)
            filtered_tasks = result
        
        if priority_filter and priority_filter != "All":
            result = []
            for task in filtered_tasks:
                if task.priority.lower() == priority_filter.lower():
                    result.append(task)
            filtered_tasks = result
        
        if due_date_filter:
            result = []
            for task in filtered_tasks:
                if task.due_date == due_date_filter:
                    result.append(task)
            filtered_tasks = result
        
        return filtered_tasks
    
    def sort_tasks(self, sort_key='name', reverse=False):
        if sort_key == 'name':
            # Sort by name
            for i in range(len(self.tasks)):
                for j in range(i + 1, len(self.tasks)):
                    if (self.tasks[i].name.lower() > self.tasks[j].name.lower() and not reverse) or (self.tasks[i].name.lower() < self.tasks[j].name.lower() and reverse):
                        self.tasks[i], self.tasks[j] = self.tasks[j], self.tasks[i]
        
        elif sort_key == 'priority':
            # Define priority order
            priority_order = {"high": 0, "medium": 1, "low": 2}
            
            # Sort by priority
            for i in range(len(self.tasks)):
                for j in range(i + 1, len(self.tasks)):
                    task_i_priority = priority_order.get(self.tasks[i].priority.lower(), 3)
                    task_j_priority = priority_order.get(self.tasks[j].priority.lower(), 3)
                    
                    if (task_i_priority > task_j_priority and not reverse) or (task_i_priority < task_j_priority and reverse):
                        self.tasks[i], self.tasks[j] = self.tasks[j], self.tasks[i]
        
        elif sort_key == 'due_date':
            # Sort by due date
            for i in range(len(self.tasks)):
                for j in range(i + 1, len(self.tasks)):
                    date_i = datetime.strptime(self.tasks[i].due_date, "%Y-%m-%d")
                    date_j = datetime.strptime(self.tasks[j].due_date, "%Y-%m-%d")
                    
                    if (date_i > date_j and not reverse) or (date_i < date_j and reverse):
                        self.tasks[i], self.tasks[j] = self.tasks[j], self.tasks[i]
        
        return self.tasks
    
# ==============================================Stage 4:Gui  ===============================================


# Define the TaskManagerGUI class to create the Tkinter interface with only viewing functionality
class TaskManagerGUI:
    def __init__(self, root):
        self.root = root
        self.task_manager = TaskManager()
        self.current_sort_key = 'name'
        self.sort_reverse = False
        self.setup_gui()

    def setup_gui(self):
        self.root.title("Personal Task Manager - View Only")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)

        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)

        # Title Label
        title_label = ttk.Label(title_frame, text="Personal Task Manager", font=("Arial", 16, "bold"))
        title_label.pack()

        # Message Label
        message_label = ttk.Label(title_frame, text="",
                                 font=("Arial", 10, "italic"))
        message_label.pack(pady=5)

        # Frame for Search and Filter
        filter_frame = ttk.LabelFrame(self.root, text="Search and Filter", padding="10")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        # Filters in same row
        filter_row = ttk.Frame(filter_frame)
        filter_row.pack(fill=tk.X, pady=5)

        # Task Name filter
        name_label = ttk.Label(filter_row, text="Task Name:")
        name_label.pack(side=tk.LEFT, padx=5)

        self.name_entry = ttk.Entry(filter_row, width=20)
        self.name_entry.pack(side=tk.LEFT, padx=5)

        # Priority filter dropdown
        priority_label = ttk.Label(filter_row, text="Priority:")
        priority_label.pack(side=tk.LEFT, padx=5)

        self.priority_var = tk.StringVar(value="All")
        priority_options = ["All", "High", "Medium", "Low"]
        priority_dropdown = ttk.Combobox(filter_row, textvariable=self.priority_var, values=priority_options,
                                         state="readonly", width=8)
        priority_dropdown.pack(side=tk.LEFT, padx=5)

        # Due date filter field
        date_label = ttk.Label(filter_row, text="Due Date (YYYY-MM-DD):")
        date_label.pack(side=tk.LEFT, padx=5)

        self.date_entry = ttk.Entry(filter_row, width=12)
        self.date_entry.pack(side=tk.LEFT, padx=5)

        # Filter button on the same row
        filter_button = ttk.Button(filter_row, text="Filter", command=self.apply_filter)
        filter_button.pack(side=tk.LEFT, padx=5)
        
        # Separator between filter and sort
        ttk.Label(filter_row, text="|").pack(side=tk.LEFT, padx=5)
        
        # Sort label
        sort_label = ttk.Label(filter_row, text="Sort by:")
        sort_label.pack(side=tk.LEFT, padx=5)
        
        # Three separate sort buttons instead of dropdown
        sort_name_button = ttk.Button(filter_row, text="Name", command=lambda: self.sort_tasks("name"))
        sort_name_button.pack(side=tk.LEFT, padx=2)
        
        sort_priority_button = ttk.Button(filter_row, text="Priority", command=lambda: self.sort_tasks("priority"))
        sort_priority_button.pack(side=tk.LEFT, padx=2)
        
        sort_date_button = ttk.Button(filter_row, text="Due Date", command=lambda: self.sort_tasks("due_date"))
        sort_date_button.pack(side=tk.LEFT, padx=2)

        # Create a frame for the task table
        table_frame = ttk.LabelFrame(self.root, text="Tasks", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create the task table with ScrollBar
        columns = ("name", "description", "priority", "due_date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Configure the columns
        self.tree.heading("name", text="Name", command=lambda: self.sort_column("name"))
        self.tree.heading("description", text="Description", command=lambda: self.sort_column("description"))
        self.tree.heading("priority", text="Priority", command=lambda: self.sort_column("priority"))
        self.tree.heading("due_date", text="Due Date", command=lambda: self.sort_column("due_date"))

        self.tree.column("name", width=150)
        self.tree.column("description", width=300)
        self.tree.column("priority", width=100)
        self.tree.column("due_date", width=100)

        # Add scrollbar to the table view
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Frame for buttons at bottom
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)

        # Populate the tree with tasks
        self.populate_tree()

    def populate_tree(self, tasks=None):
        # Clear the existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # If no tasks are provided, use all tasks
        if tasks is None:
            tasks = self.task_manager.tasks

        # Add tasks to the tree
        for task in tasks:
            self.tree.insert("", tk.END, values=(task.name, task.description, task.priority, task.due_date))

    def apply_filter(self):
        name_filter = self.name_entry.get()
        priority_filter = self.priority_var.get()
        due_date_filter = self.date_entry.get()

        filtered_tasks = self.task_manager.get_filtered_tasks(
            name_filter=name_filter,
            priority_filter=priority_filter,
            due_date_filter=due_date_filter
        )

        self.populate_tree(filtered_tasks)

    def sort_column(self, column):
        if self.current_sort_key == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.current_sort_key = column
            self.sort_reverse = False

        self.sort_tasks(column)

    def sort_tasks(self, sort_key):
        if self.current_sort_key == sort_key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.current_sort_key = sort_key
            self.sort_reverse = False
            
        sorted_tasks = self.task_manager.sort_tasks(sort_key, self.sort_reverse)
        self.populate_tree(sorted_tasks)

def main():
    load_tasks_from_file()
    load_tasks_from_json()
    while True:
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Open GUI")
        print("6. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            add_task()
        elif choice == "2":
            show_tasks()
        elif choice == "3":
            update_task()
        elif choice == "4":
            delete_task()
        elif choice == "5":
            try:
                root = tk.Tk()
                root.geometry("850x450")
                app = TaskManagerGUI(root)
                root.mainloop()
            except Exception as e:
                print(f"Error opening GUI: {e}")
        elif choice == "6":
            print("Goodbye 👋")
            break
        else:
            print("Invalid choice! Try again.\n")

if __name__ == "__main__":
    main()