import hashlib
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import tkinter.filedialog as filedialog
import os
import xlsxwriter
import datetime
import threading
import exifread
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import win32security
import win32con

global path
method_buttons_created = False
threads = []
global owner_history
baseline_hashes = {}
flag = True


def monitor_gui():
    def stop_all_threads():
        global flag
        flag = False
        for t in threads:
            t.join()
        terminal.insert(tk.END, f"Monitoring Halted\n")
        flag = True

    def select_file_folder():
        global path
        path = filedialog.askopenfilename()
        terminal.config(state='normal')
        terminal.insert(tk.END, f"Selected path: {path}\n")
        terminal.config(state='disabled')

    def select_folder():
        global path
        path = filedialog.askdirectory()
        terminal.config(state='normal')
        terminal.insert(tk.END, f"Selected path: {path}\n")
        terminal.config(state='disabled')

    def hash_monitoring():
        global path
        terminal.config(state='normal')
        terminal.insert(tk.END, "Hash Monitoring Selected\n")
        terminal.insert(tk.END, f"{path} is the path\n")
        thread = threading.Thread(target=hash_loop)
        threads.append(thread)
        thread.start()


    def hash_loop():
        # Calculate the initial hash of the file
        with open(path, 'rb') as f:
            initial_hash = hashlib.sha256(f.read()).hexdigest()
        while flag:
            with open(path, 'rb') as f:
                current_hash = hashlib.sha256(f.read()).hexdigest()
            if current_hash != initial_hash:
                terminal.insert(tk.END, f"{path} has been modified!\n")
            else:
                terminal.insert(tk.END, f"File Unchanged\n")
            initial_hash = current_hash
            time.sleep(3)  # Wait n seconds before checking again

    def directory_monitoring():
        global path
        terminal.config(state='normal')
        terminal.insert(tk.END, "Directory Monitoring Selected\n")
        terminal.insert(tk.END, f"{path} is the path\n")
        thread = threading.Thread(target=directory_loop, args=(path,))  # Using a thread
        threads.append(thread)
        thread.start()

    class TkinterHandler(logging.Handler):  # custom class to handle tkinter integration for logging+watchdog lib
        def __init__(self, terminal):
            super().__init__()
            self.terminal = terminal

        def emit(self, record):
            msg = self.format(record)
            self.terminal.config(state='normal')
            self.terminal.insert(tk.END, msg + "\n")
            self.terminal.config(state='disabled')

    def directory_loop(path):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        logging.getLogger().addHandler(TkinterHandler(terminal))

        pathi = path
        event_handler = LoggingEventHandler()
        observer = Observer()
        observer.schedule(event_handler, pathi, recursive=True)
        observer.start()
        try:
            while flag:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()

    def metadata_monitoring():
        global path
        terminal.config(state='normal')
        terminal.insert(tk.END, "Metadata Monitoring Selected\n")
        terminal.insert(tk.END, f"{path} is the path\n")
        thread = threading.Thread(target=meta_loop)  # Using a thread
        threads.append(thread)
        thread.start()

    def get_file_owner(file_path):
        try:
            sd = win32security.GetFileSecurity(file_path, win32security.OWNER_SECURITY_INFORMATION)
            owner_sid = sd.GetSecurityDescriptorOwner()
            owner, domain, _ = win32security.LookupAccountSid(None, owner_sid)
            return f"{domain}\\{owner}"
        except Exception as e:
            return f"Error: Unable to retrieve owner - {str(e)}"

    def meta_loop():
        global owner_history
        previous_size = 0
        previous_timestamp = 0
        previous_metadata = {}
        previous_owner = None
        owner_history = []

        while flag:
            current_size = os.path.getsize(path)
            current_timestamp = os.path.getmtime(path)
            current_owner = get_file_owner(path)

            if current_size != previous_size:
                terminal.insert(tk.END, f"Changes detected at {time.ctime(current_timestamp)}\n")
                terminal.insert(tk.END, f"Verified File Size was  {previous_size}, current File size is "
                                        f"{current_size}\n")
                previous_size = current_size
            if current_timestamp != previous_timestamp:
                terminal.insert(tk.END, f"Changes detected at {time.ctime(current_timestamp)}\n")
                terminal.insert(tk.END, f"previously last modified at {previous_timestamp}, current modification at "
                                        f"{current_timestamp}\n")
                previous_timestamp = current_timestamp

            if current_owner != previous_owner:
                terminal.insert(tk.END, f"File owner changed from {previous_owner} to {current_owner}\n")
                previous_owner = current_owner

            owner_history.append(current_owner)

            if path.endswith('.jpg') or path.endswith('.jpeg') or path.endswith('.png') or path.endswith('.gif') \
                    or path.endswith('.jfif'):
                with open(path, 'rb') as f:
                    tags = exifread.process_file(f)
                    for tag in tags.keys():
                        if tag not in previous_metadata.keys() or tags[tag].values != previous_metadata[tag]:
                            terminal.insert(tk.END, f"Metadata {tag} has been changed\n")
                            previous_metadata[tag] = tags[tag].values

            elif path.endswith('.mp4') or path.endswith('.avi') or path.endswith('.mkv') or path.endswith('.webm') \
                    or path.endswith('.mp3'):
                video = mp.VideoFileClip(path)
                video_duration = video.duration
                video_fps = video.fps
                video_size = video.size

                with open(path, 'rb') as f:
                    tags = exifread.process_file(f)
                    for tag in tags.keys():
                        if tag not in previous_metadata.keys() or tags[tag].values != previous_metadata[tag]:
                            terminal.insert(tk.END, f"Metadata {tag} has been changed\n")
                            previous_metadata[tag] = tags[tag].values
                
            time.sleep(3)

    def save_logs():
        terminal.config(state='normal')
        terminal.insert(tk.END, "save logs\n")
        terminal.config(state='disabled')
        log_text = terminal.get("1.0", tk.END)
        log_list = log_text.split("\n")
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Workbook", "*.xlsx")])
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, "Serial No.")
        worksheet.write(0, 1, "Time")
        worksheet.write(0, 2, "Date")
        worksheet.write(0, 3, "Owner")
        worksheet.write(0, 4, "Output")
        
        owner_index = 0;
        for i, log in enumerate(log_list):
            if log != "":
                current_time = str(datetime.datetime.now().time())[:8]
                current_date = str(datetime.datetime.now().date())
                owner_name = owner_history[owner_index] if owner_index < len(owner_history) else "Unknown"
                worksheet.write(i + 1, 0, i + 1)
                worksheet.write(i + 1, 1, current_time)
                worksheet.write(i + 1, 2, current_date)
                worksheet.write(i + 1, 3, owner_name)
                worksheet.write(i + 1, 4, log)
                owner_index += 1
        workbook.close()
        terminal.config(state='normal')
        terminal.insert(tk.END, "Logs saved to " + filename + "\n")
        terminal.config(state='disabled')

    # Function to create clickable frames with image and text
    def create_clickable_frame(parent, image_file, text, command):
        # Load and resize the image
        img = Image.open(image_file)
        img = img.resize((60, 60), Image.LANCZOS)  # Resize image as needed
        img = ImageTk.PhotoImage(img)

        # Frame for the clickable box
        clickable_frame = tk.Frame(parent, width=260, height=120, bg="white", bd=2, relief="raised")
        clickable_frame.pack_propagate(False)  # Prevent the frame from resizing to its contents

        # Image label (centered)
        image_label = tk.Label(clickable_frame, image=img, bg="white")
        image_label.image = img  # Keep a reference to avoid garbage collection
        image_label.pack(pady=(15, 5))  # Adjust padding to center image vertically

        # Text label below image
        text_label = tk.Label(clickable_frame, text=text, font=("Arial", 12, "bold"), bg="white")
        text_label.pack()

        # Bind the frame to perform the action on click
        clickable_frame.bind("<Button-1>", lambda e: command())
        image_label.bind("<Button-1>", lambda e: command())  # Also bind click on image
        text_label.bind("<Button-1>", lambda e: command())   # Also bind click on text

        return clickable_frame

    root = tk.Tk()
    root.geometry("1000x1000")
    root.title("HashBox")

    top_title = tk.Label(root, text="HashBox", font=("Arial", 25, "bold"))
    top_title.pack(pady=(2,2))

    top_label = tk.Label(root, text="File Integrity Monitoring System", font=("Arial", 15, "bold"))
    top_label.pack(pady=(2,2))  # Adjust padding as needed to position it at the top

    middle_label = tk.Label(root, text="Secure Your Files, Track Every Change — With SHA-256 Precision and Real-Time Monitoring", font=("Arial", 14, "italic"))
    middle_label.pack(pady=(3,5))  # Adjust padding to place it in the middle

    command_label = tk.Label(root, text="Select the file or directory for integrity check", font=("Arial", 13, "italic"))
    command_label.pack(pady=(12,5)) 

    button_frame = tk.Frame(root)
    button_frame.pack(pady=5)

    # Create clickable frames for "Browse File" and "Browse Directory"
    file_frame = create_clickable_frame(button_frame, "images/fileIcon.PNG", "Browse File", select_file_folder)
    file_frame.grid(row=0, column=0, padx=15)

    dir_frame = create_clickable_frame(button_frame, "images/folderIcon.PNG", "Browse Directory", select_folder)
    dir_frame.grid(row=0, column=1, padx=15)

    # Create a frame to hold the method buttons in a row
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    # Common style for all method buttons
    button_style = {"height": 2, "width": 20, "bg": "white", "font": ("Arial", 12, "bold")}

    # Button for "Hash Comparison"
    method1_button = tk.Button(button_frame, text="Hash Comparison", command=hash_monitoring, **button_style)
    method1_button.pack(side="left", padx=10)

    # Button for "Directory Monitoring"
    method2_button = tk.Button(button_frame, text="Directory Monitoring", command=directory_monitoring, **button_style)
    method2_button.pack(side="left", padx=10)

    # Button for "Metadata Monitoring"
    method4_button = tk.Button(button_frame, text="Metadata Monitoring", command=metadata_monitoring, **button_style)
    method4_button.pack(side="left", padx=10)
    
    # Create terminal to display the changes in the file
    terminal = tk.Text(root)
    terminal.pack(side="top", padx=15, pady=5)
    terminal.config(state='disabled', height=20, width=100, padx=50)
 
    # Create a frame to hold the "Save Logs" and "Stop Monitoring" buttons
    bottom_button_frame = tk.Frame(root)
    bottom_button_frame.pack(pady=(10, 1))

    # "Save Logs" button
    save_logs_button = tk.Button(bottom_button_frame, text="Save Logs", command=save_logs, height=2, width=18, bg="white", font=("Arial", 12, "bold"))
    save_logs_button.pack(side="left", padx=15)

    # "Stop Monitoring" button
    kill_thread_button = tk.Button(bottom_button_frame, text="Stop Monitoring", command=stop_all_threads,  height=2, width=18, bg="white", font=("Arial", 12, "bold"))
    kill_thread_button.pack(side="left", padx=15)


    root.mainloop()

monitor_gui()