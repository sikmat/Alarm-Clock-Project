import customtkinter
import tkinter as tk
from tkinter import messagebox
import datetime
import json
import pygame
import os

class Alarm:
    def __init__(self, date, time, message, tone):
        self.datetime = datetime.datetime.combine(date, time)
        self.message = message
        self.tone = tone

# Initialize an empty list to store alarms
alarms = []

# Initialize snooze duration (default: 5 minutes)
snooze_duration = datetime.timedelta(minutes=1)

def save_alarms():
    with open("alarms.json", "w") as file:
        json.dump([(alarm.datetime.strftime('%Y-%m-%d %H:%M'), alarm.message, alarm.tone) for alarm in alarms], file)

def load_alarms():
    try:
        with open("alarms.json", "r") as file:
            alarms_data = json.load(file)
            for alarm_data in alarms_data:
                date_time_str, message, tone = alarm_data
                date_time = datetime.datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
                alarms.append(Alarm(date_time.date(), date_time.time(), message, tone))
    except FileNotFoundError:
        print("Sorry the file is not found.")
    except json.JSONDecodeError:
        print("Error decoding JSON. No alarm loaded.")

def add_alarm():
    date_str = date_entry.get()
    time_str = time_entry.get()
    message = message_entry.get()
    tone = tone_combobox.get()
    
    try:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        time = datetime.datetime.strptime(time_str, "%H:%M").time()
        
        # Get the current datetime
        current_datetime = datetime.datetime.now()
        
        # Combine the current date and entered time into a datetime object
        entered_datetime = datetime.datetime.combine(date, time)
        
        if entered_datetime <= current_datetime:
            messagebox.showerror("Sorry", "Please select a future time.")
        else:
            alarms.append(Alarm(date, time, message, tone))
            save_alarms()
            messagebox.showinfo("Alarm added successfully!")
            list_alarms()
            
            # Clear the input fields after adding the alarm
            date_entry.delete(0, tk.END)
            time_entry.delete(0, tk.END)
            message_entry.delete(0, tk.END)
            
    except ValueError:
        messagebox.showerror("Sorry", "Invalid date or time format.")

def list_alarms():
    alarm_list.delete(0, tk.END)
    for alarm in alarms:
        alarm_list.insert(tk.END, f"{alarm.datetime.strftime('%Y-%m-%d %H:%M')} - {alarm.message} - {alarm.tone}")

def delete_alarm():
    selected_index = alarm_list.curselection()
    if selected_index:
        del alarms[selected_index[0]]
        save_alarms()
        list_alarms()  # Update list after deleting an alarm

def ring_alarm():
    # Get the current datetime
    current_datetime = datetime.datetime.now()
    
    # Define a time range around the current time (e.g., 1 second)
    time_tolerance = datetime.timedelta(seconds=1)
    
    # Define the range of time to check
    start_time = current_datetime - time_tolerance
    end_time = current_datetime + time_tolerance
    
    # Check if any alarm time falls within the time range
    alarms_within_range = [alarm for alarm in alarms if start_time <= alarm.datetime <= end_time]
    if alarms_within_range:
        for alarm in alarms_within_range:
            tone_path = os.path.join("tones", alarm.tone)  # Construct full path to tone
            print("Tone path:", tone_path)  # Print full path for debugging
            try:
                pygame.mixer.music.load(tone_path)
                pygame.mixer.music.play()
                
                # Ask the user if they want to snooze the alarm
                if messagebox.askyesno("Alarm", f"{alarm.message}\nSnooze or Dismiss?"):
                    # Snooze the alarm for the selected duration
                    snooze_alarm(alarm)
                else:
                    # Dismiss the alarm
                    dismiss_alarm(alarm)
                
                save_alarms()
                list_alarms()
            except pygame.error as e:
                print("Error loading tone:", e)  # Print any errors that occur during loading

    # Reschedule the alarm check
    app.after(1000, ring_alarm)

def snooze_alarm(alarm):
    global snooze_duration
    snooze_time = datetime.datetime.now() + snooze_duration
    alarm.datetime = snooze_time

def dismiss_alarm(alarm):
    global alarms
    alarms.remove(alarm)

def play_selected_tone():
    selected_tone = tone_combobox.get()
    if selected_tone:
        tone_path = os.path.join("tones", selected_tone)  # Construct full path to tone
        pygame.mixer.music.load(tone_path)
        pygame.mixer.music.play()

def stop_tone():
    pygame.mixer.music.stop()

def update_time():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time_label.configure(text=current_time)
    app.after(1000, update_time)  # Update time every second

# Initialize pygame mixer
pygame.mixer.init()

# Load alarms from file
load_alarms()

# Initialize snooze duration (default: 5 minutes)
snooze_duration = datetime.timedelta(minutes=1)

#configuring theme
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

# Create the main window
app = customtkinter.CTk()
app.title("ALARM")
app.geometry("900x900")

frame_1 = customtkinter.CTkFrame(master=app,
                                 width=900,
                                 height=900,
                                 fg_color="black",
                                 border_color="orange",
                                 border_width=1)

frame_1.pack(padx=50, pady=5)


frame = customtkinter.CTkFrame(master=app,
                               width=500,
                               height=400,
                               fg_color="black",
                               border_color="blue",
                               border_width=1)

frame.pack(padx=50, pady=5)

# Create a label for the heading
heading_label = customtkinter.CTkLabel(master=frame_1, text="Current Time and Date", font=("Lato", 20, "bold"), text_color="grey")
heading_label.grid(row=0, column=2, columnspan=2, padx=10, pady=5)

# Create a label to display current time
time_label = customtkinter.CTkLabel(master=frame_1, text="", font=("Lato", 18,"bold"), text_color="grey")
time_label.grid(row=1, column=2, columnspan=2, padx=10, pady=10)

# Create a label for alarm heading
heading_label = customtkinter.CTkLabel(master=frame, text="ALARM", font=("Lato", 20, "bold"), text_color="white")
heading_label.grid(row=0, column=0, columnspan=2, padx=5, pady=10)

# Add labels and entry fields for date, time, and message
my_label = customtkinter.CTkLabel(master=frame, text="Date", font=("Lato", 14,"bold"), text_color=("grey"))
my_label.grid(row=1, column=0, padx=5, pady=10)
date_entry = customtkinter.CTkEntry(master=frame, placeholder_text="YYYY-MM-DD", border_color="white")
date_entry.grid(row=1, column=1, padx=1, pady=10)

my_label = customtkinter.CTkLabel(master=frame, text="Time", font=("Lato", 14,"bold"), text_color=("grey"))
my_label.grid(row=2, column=0, padx=5, pady=10)
time_entry = customtkinter.CTkEntry(master=frame, placeholder_text="HH:MM", border_color="white")
time_entry.grid(row=2, column=1, padx=1, pady=10)

my_label = customtkinter.CTkLabel(master=frame, text="Message", font=("Lato", 14,"bold"), text_color=("grey"))
my_label.grid(row=3, column=0, padx=5, pady=10)
message_entry = customtkinter.CTkEntry(master=frame, placeholder_text="e.g wake up time,", border_color="white")
message_entry.grid(row=3, column=1, padx=1, pady=10)

my_label = customtkinter.CTkLabel(master=frame, text=" Alarm Tone", font=("Lato", 14,"bold"), text_color=("grey"))
my_label.grid(row=4, column=0, padx=5, pady=10)
tones = [filename for filename in os.listdir("tones") if filename.endswith(".mp3")]
tone_combobox = customtkinter.CTkComboBox(master=frame, values=tones, state="readonly", border_color="white")
tone_combobox.grid(row=4, column=1, padx=1, pady=10)

# Add buttons for playing and stopping tone
play_button = customtkinter.CTkButton(master=frame, text="Play Alarm Tone", font=("Lato", 12,"bold"), command=play_selected_tone)
play_button.grid(row=5, column=0, padx=10, pady=10)

stop_button = customtkinter.CTkButton(master=frame, text="Stop Alarm Tone", font=("Lato", 12,"bold"), command=stop_tone)
stop_button.grid(row=5, column=1, padx=10, pady=10)

# Add buttons for CRUD operations
add_button = customtkinter.CTkButton(master=frame, text="Set Alarm", font=("Lato", 12,"bold"), command=add_alarm)
add_button.grid(row=6, column=0, padx=10, pady=10)

delete_button = customtkinter.CTkButton(master=frame, text="Delete Alarm", font=("Lato", 12,"bold"),command=delete_alarm)
delete_button.grid(row=6, column=1, padx=10, pady=10)

# Add listbox to display alarms
alarm_list = tk.Listbox(master=frame, width=70, font=("Lato", 13,"bold"), background="grey",borderwidth=1)
alarm_list.grid(row=7, column=0, columnspan=2, padx=10, pady=20)

# Initialize the listbox with loaded alarms
list_alarms()

# Start ringing alarms automatically
ring_alarm()

# Call the update_time function to initially display time
update_time()

app.mainloop()
