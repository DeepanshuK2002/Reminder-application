import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
import threading
import time
from plyer import notification
from playsound import playsound
from PIL import Image, ImageTk

class ReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Day Reminder")
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        self.set_taskbar_icon()

        self.tasks = []

        self.current_time_label = tk.Label(root, text="", font=("Helvetica", 14))
        self.current_time_label.pack(pady=10)
        self.update_current_time()

        self.label_task = tk.Label(root, text="Task:")
        self.label_task.pack(pady=5)
        self.entry_task = tk.Entry(root, width=40)
        self.entry_task.pack(pady=5)

        time_frame = tk.Frame(root)
        time_frame.pack(pady=5)

        self.label_time = tk.Label(time_frame, text="Reminder Time (HH:MM):")
        self.label_time.pack(side=tk.LEFT, padx=5)
        self.entry_time = tk.Entry(time_frame, width=20)
        self.entry_time.pack(side=tk.LEFT, padx=(0, 20))

        self.am_pm_var = tk.StringVar(value="AM")
        self.am_pm_combobox = ttk.Combobox(time_frame, textvariable=self.am_pm_var, values=["AM", "PM"], state="readonly", width=5)
        self.am_pm_combobox.pack(side=tk.LEFT)

        self.task_list = ttk.Treeview(root, columns=('Task', 'Time Left'), show='headings')
        self.task_list.heading('Task', text='Task')
        self.task_list.heading('Time Left', text='Time Left')
        self.task_list.pack(pady=10)

        self.add_btn = tk.Button(root, text="Add Reminder", command=self.add_reminder)
        self.add_btn.pack(pady=5)
        self.delete_btn = tk.Button(root, text="Delete Reminder", command=self.delete_reminder)
        self.delete_btn.pack(pady=5)

        self.update_countdowns_thread = threading.Thread(target=self.update_countdowns)
        self.update_countdowns_thread.daemon = True
        self.update_countdowns_thread.start()

    def set_taskbar_icon(self):
        try:
            self.root.iconbitmap("C:\\Users\\Deepu Kashyap\\Desktop\\Reminder\\notification.ico")  # Ensure the logo path is correct
        except Exception as e:
            messagebox.showerror("Error", f"Could not set taskbar logo: {e}")

    def update_current_time(self):
        current_time = datetime.now().strftime("%I:%M:%S %p")
        self.current_time_label.config(text=f"Current Time: {current_time}")
        self.root.after(1000, self.update_current_time)

    def add_reminder(self):
        task = self.entry_task.get()
        reminder_time_str = self.entry_time.get()
        am_pm = self.am_pm_var.get()

        try:
            reminder_time = datetime.strptime(reminder_time_str, "%I:%M")
        except ValueError:
            messagebox.showerror("Invalid Time", "Please enter time in HH:MM format")
            return

        if am_pm == "PM" and reminder_time.hour != 12:
            reminder_time = reminder_time.replace(hour=reminder_time.hour + 12)
        elif am_pm == "AM" and reminder_time.hour == 12:
            reminder_time = reminder_time.replace(hour=0)

        current_time = datetime.now()
        reminder_datetime = current_time.replace(hour=reminder_time.hour, minute=reminder_time.minute, second=0, microsecond=0)

        if reminder_datetime <= current_time:
            reminder_datetime += timedelta(days=1)

        self.tasks.append((task, reminder_datetime))
        self.task_list.insert('', 'end', values=(task, self.get_time_left(reminder_datetime)))

        self.entry_task.delete(0, tk.END)
        self.entry_time.delete(0, tk.END)

        threading.Thread(target=self.reminder_thread, args=(task, reminder_datetime)).start()

    def delete_reminder(self):
        selected_item = self.task_list.selection()
        if selected_item:
            task_text = self.task_list.item(selected_item[0], 'values')[0]
            self.task_list.delete(selected_item)
            self.tasks = [task for task in self.tasks if task[0] != task_text]

    def reminder_thread(self, task, reminder_time):
        while True:
            current_time = datetime.now()
            if current_time >= reminder_time:
                self.show_notification(task)
                playsound("notification_sound.mp3")
                break
            time.sleep(1)

    def show_notification(self, task):
        notification.notify(
            title="Reminder",
            message=f"Time to: {task}",
            timeout=10
        )

    def get_time_left(self, reminder_datetime):
        time_left = reminder_datetime - datetime.now()
        return str(time_left).split('.')[0]

    def update_countdowns(self):
        while True:
            for i, (task, reminder_datetime) in enumerate(self.tasks):
                time_left = self.get_time_left(reminder_datetime)
                self.task_list.set(self.task_list.get_children()[i], 'Time Left', time_left)
            time.sleep(1)

root = tk.Tk()
app = ReminderApp(root)
root.mainloop()
