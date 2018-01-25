#!/usr/bin/python3

from tkinter import *
from tkinter import ttk
from tkinter import font
import time
import datetime
from pythonosc import osc_server, dispatcher, udp_client
import threading
import netifaces

# Network Variables -- CHANGE THESE
input_port = 8500
broadcast_port = 9000

# Other Settings -- Feel free to change
show_help = True

# Global State Variables
ip_address = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
broadcast_address = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['broadcast']
running = False
time = 0 

feedback = udp_client.SimpleUDPClient(broadcast_address, broadcast_port, allow_broadcast=True)

def quit(*args):
  root.destroy()
          
def show_time():
  global time
  global feeback
  global running

  # Calculate time
  hours = int(time / 3600)
  minutes = int((time - (hours * 3600)) / 60)
  seconds = time - (hours * 3600) - (minutes * 60)

  time_string = '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)

  # Show the time left
  txt.set(time_string)

  if (running):
    # Trigger the countdown after 1000ms
    root.after(1000, show_time)

  # Send out to show on OSC device
  feedback.send_message("/timer/time", time_string)

  # Update Time
  time += 1

# Use tkinter lib for showing the clock
root = Tk()
root.attributes("-fullscreen", True)
root.configure(background='black')
root.bind("x", quit)
style = ttk.Style()
style.theme_use('classic')

fnt = font.Font(family='Helvetica', size=150, weight='bold')
txt = StringVar()
txt.set("00:00:00")
lbl = ttk.Label(root, textvariable=txt, font=fnt, foreground="white", background="black")
lbl.place(relx=0.5, rely=0.5, anchor=CENTER)

fnt_instructions = font.Font(family='Helvetica', size=25, weight='bold')
txt_instructions = StringVar()
txt_instructions.set("Listening at {}:{}\n/timer/start -> Start stopwatch\n/timer/stop -> Stop (pause) stopwatch\n/timer/reset -> Set time back to 00:00:00".format(ip_address, input_port))
lbl_instructions = ttk.Label(root, textvariable=txt_instructions, font=fnt_instructions, foreground="white", background="black", padding=30)
if (show_help):
  lbl_instructions.pack(side=BOTTOM)

def start_timer(*args):
  global running
  if not running:
    running = True
    root.after(1000, show_time)

def stop_timer(*args):
  global running
  if running:
    running = False

def reset_timer(*args):
  global running
  global time
  time = 0 
  txt.set("00:00:00")
  feedback.send_message("/timer/time", "00:00:00")
  running = False

dispatcher = dispatcher.Dispatcher()
dispatcher.map("/timer/start", start_timer)
dispatcher.map("/timer/stop", stop_timer)
dispatcher.map("/timer/reset", reset_timer)
dispatcher.map("/timer/quit", quit)

# We use BlockingOSCUDPServer to execute each incoming command in order
server = osc_server.BlockingOSCUDPServer(("0.0.0.0", input_port), dispatcher)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.start()

# This is a blocking function, will release when quit is called
root.mainloop()

server.shutdown()
