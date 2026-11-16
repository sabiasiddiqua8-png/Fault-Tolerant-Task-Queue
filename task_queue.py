import sqlite3
class TaskQueue:


    def __init__(self):

        self.tasks = []

        self.connection = sqlite3.connect("tasks.db")

        self.cursor = self.connection.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                status TEXT NOT NULL,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3
            )
        """)


        self.connection.commit()

        self.load_tasks()

    
    def add_task(self, task_name):

        task_name = task_name.strip()

        if not task_name:
            print("Task name cannot be empty.")
            return

        self.cursor.execute("""
            INSERT INTO tasks (task_name, status, retry_count, max_retries)
            VALUES (?, ?, ?, ?)
            """, (task_name, "Pending", 0, 3))

        self.connection.commit()

        task_id = self.cursor.lastrowid

        task = {
            "id": task_id,
            "name": task_name,
            "status": "Pending",
            "retry_count": 0,
            "max_retries": 3
        }

        self.tasks.append(task)

        print("Task added successfully!")


    def load_tasks(self):

        self.cursor.execute("SELECT * FROM tasks")

        records = self.cursor.fetchall()

        self.tasks = []

        for record in records:

            task = {
                "id": record[0],
                "name": record[1],
                "status": record[2],
                "retry_count": record[3],
                "max_retries": record[4]
            }

            self.tasks.append(task)

        print("Tasks loaded successfully!")    
    
    def execute_task(self, task_id, simulate_failure=False):

        for task in self.tasks:

            if task["id"] == task_id:

                if task["status"] != "Pending":
                    print("Task is not ready for execution.")
                    return

                while True:

                    task["status"] = "Processing"

                    self.cursor.execute(
                        "UPDATE tasks SET status = ? WHERE task_id = ?",
                        ("Processing", task_id)
                    )
                    self.connection.commit()

                    print("\nExecuting:", task["name"])

                    if simulate_failure:

                        print("Task execution failed!")

                        if task["retry_count"] < task["max_retries"]:

                            task["retry_count"] += 1

                            self.cursor.execute(
                                "UPDATE tasks SET retry_count = ? WHERE task_id = ?",
                                (task["retry_count"], task_id)
                            )

                            self.connection.commit()

                            print("Retrying...")

                        else:

                            task["status"] = "Failed"

                            self.cursor.execute("""
                                UPDATE tasks
                                SET status = ?, retry_count = ?
                                WHERE task_id = ?
                                """, ("Failed", task["retry_count"], task_id))

                            self.connection.commit()

                            print("Maximum retries reached.")
                            return

                    else:

                        task["status"] = "Completed"

                        self.cursor.execute(
                            "UPDATE tasks SET status = ? WHERE task_id = ?",
                            ("Completed", task_id)
                        )

                        self.connection.commit()

                        print("Task completed successfully!")
                        return

        print("Task ID not found.")

    
    def retry_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:

                if task["status"] != "Failed":
                    print("Only failed tasks can be retried.")
                    return

                # Start a fresh retry cycle
                task["retry_count"] = 0
                task["status"] = "Pending"

                self.cursor.execute("""
                    UPDATE tasks
                    SET status = ?, retry_count = ?
                    WHERE task_id = ?
                    """, ("Pending", 0, task_id))

                self.connection.commit()

                print("Task moved to Pending successfully!")
                print("Retry count reset to 0.")
                return

        print("Task ID not found.")

    
    def delete_task(self, task_id):

        for task in self.tasks:

            if task["id"] == task_id:

                self.cursor.execute(
                    "DELETE FROM tasks WHERE task_id = ?",
                    (task_id,)
                ) 

                self.connection.commit()

                self.tasks.remove(task)

                print("Task deleted successfully!")

                return

        print("Task ID not found.")  
    
    def search_task(self, task_id):

        for task in self.tasks:

            if task["id"] == task_id:

                print("\n===== TASK FOUND =====")
                print("Task ID:", task["id"])
                print("Task Name:", task["name"])
                print("Status:", task["status"])
                print("Retry Count:", task["retry_count"])
                print("Maximum Retries:", task["max_retries"])
                print("----------------------")

                return

        print("Task ID not found.") 
    
    def filter_tasks_by_status(self, status):

        found = False

        print("\n===== " + status.upper() + " TASKS =====")

        for task in self.tasks:

            if task["status"].lower() == status.lower():

                print("Task ID:", task["id"])
                print("Task Name:", task["name"])
                print("Status:", task["status"])
                print("Retry Count:", task["retry_count"])
                print("----------------------")

                found = True

        if not found:
            print("No tasks found with this status.")
 
    def display_statistics(self):

        total = len(self.tasks)

        pending = 0
        completed = 0
        failed = 0
        processing = 0

        for task in self.tasks:

            if task["status"] == "Pending":
                pending += 1

            elif task["status"] == "Completed":
                completed += 1

            elif task["status"] == "Failed":
                failed += 1

            elif task["status"] == "Processing":
                processing += 1

        print("\n===== TASK QUEUE STATISTICS =====")
        print("Total Tasks:", total)
        print("Pending Tasks:", pending)
        print("Completed Tasks:", completed)
        print("Failed Tasks:", failed)
        print("Processing Tasks:", processing)

        if total > 0:
            completion_rate = (completed / total) * 100
            print("Completion Rate:", round(completion_rate, 2), "%")
        else:
            print("Completion Rate: 0%")
    
    def fail_task(self, task_id):

        for task in self.tasks:

            if task["id"] == task_id:

                if task["status"] != "Pending":
                    print("Only pending tasks can be marked as failed.")
                    return

                task["status"] = "Failed"

                self.cursor.execute(
                    "UPDATE tasks SET status = ? WHERE task_id = ?",
                    ("Failed", task_id)
                )

                self.connection.commit()

                print("Task failed!")
                return

        print("Task ID not found.")

    def display_tasks(self):

        if not self.tasks:
            print("No tasks available.")
            return

        print("\n===== TASK QUEUE =====")

        for task in self.tasks:
            print("Task ID:", task["id"])
            print("Task Name:", task["name"])
            print("Status:", task["status"])
            print("Retry Count:", task["retry_count"])
            print("Maximum Retries:", task["max_retries"])
            print("----------------------")

    def execute_all_pending_tasks(self):

        print("\n===== EXECUTING PENDING TASKS =====")

        found = False

        for task in self.tasks:

            if task["status"] == "Pending":

                found = True

                print("\nProcessing Task ID:", task["id"])

                self.execute_task(task["id"])

        if not found:
            print("No pending tasks available.")

    def run_menu(self):

        while True:

            print("\n===== FAULT-TOLERANT TASK QUEUE =====")
            print("1. Add Task")
            print("2. Display All Tasks")
            print("3. Execute a Task")
            print("4. Execute All Pending Tasks")
            print("5. Retry a Failed Task")
            print("6. Delete a Task")
            print("7. Search a Task")
            print("8. Filter Tasks by Status")
            print("9. Display Statistics")
            print("10. Exit")

            try:
                choice = int(input("\nEnter your choice: "))

            except ValueError:
                print("Please enter a valid number.")
                continue

            if choice == 1:

                task_name = input("Enter task name: ")
                self.add_task(task_name)

            elif choice == 2:

                self.display_tasks()

            elif choice == 3:

                try:
                    task_id = int(input("Enter Task ID: "))

                    simulate = input(
                        "Simulate task failure? (yes/no): "
                    ).strip().lower()

                    if simulate == "yes":
                        self.execute_task(task_id, simulate_failure=True)

                    elif simulate == "no":
                        self.execute_task(task_id)

                    else:
                        print("Please enter yes or no.")

                except ValueError:
                    print("Please enter a valid Task ID.")

            elif choice == 4:

                self.execute_all_pending_tasks()

            elif choice == 5:

                try:
                    task_id = int(input("Enter Task ID: "))
                    self.retry_task(task_id)
                except ValueError:
                    print("Please enter a valid Task ID.")

            elif choice == 6:

                try:
                    task_id = int(input("Enter Task ID: "))
                    self.delete_task(task_id)
                except ValueError:
                    print("Please enter a valid Task ID.")

            elif choice == 7:

                try:
                    task_id = int(input("Enter Task ID: "))
                    self.search_task(task_id)
                except ValueError:
                    print("Please enter a valid Task ID.")

            elif choice == 8:

                status = input(
                    "Enter status (Pending/Completed/Failed/Processing): "
                ).strip().capitalize()

                if status in ["Pending", "Completed", "Failed", "Processing"]:
                    self.filter_tasks_by_status(status)
                else:
                    print("Invalid status. Please enter a valid task status.")

            elif choice == 9:

                self.display_statistics()

            elif choice == 10:

                print("Exiting Task Queue System...")
                self.close()
                break

            else:

                print("Invalid choice. Please try again.")


    def close(self):
        self.connection.close()
        print("Database connection closed.")


if __name__ == "__main__":

    queue = TaskQueue()
    queue.run_menu()
