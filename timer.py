#!/usr/bin/python3

from tkinter import *
from tkinter import ttk
from tkinter import font
import time
import datetime
from pythonosc import osc_server, dispatcher, udp_client
import threading

# Network Variables -- CHANGE THESE
ip_address = "192.168.10.50"
input_port = 8500
broadcast_address = "192.168.10.255"
broadcast_port = 9000

# Other Settings -- Feel free to change
show_help = True
initial_time = 0 # in seconds

# Global State Variables
running = False
time = initial_time 

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
lbl = ttk.Label(root, textvariable=txt, font=fnt, foreground="white", background="black")
lbl.place(relx=0.5, rely=0.5, anchor=CENTER)

fnt_instructions = font.Font(family='Helvetica', size=25, weight='bold')
txt_instructions = StringVar()
txt_instructions.set("Send /timer/start to {}:{} to start the timer".format(ip_address, input_port))
lbl_instructions = ttk.Label(root, textvariable=txt_instructions, font=fnt_instructions, foreground="white", background="black")
if (show_help):
  lbl_instructions.place(relx=0.5, rely=0.9, anchor=CENTER)

def start_timer(*args):
  global running
  running = True
  root.after(1000, show_time)
  txt_instructions.set("Send /timer/stop to {}:{} to stop the timer".format(ip_address, input_port))

def stop_timer(*args):
  global running
  running = False
  txt_instructions.set("Sent /timer/start to {}:{} to resume the timer\nSend /timer/reset to {}:{} to set the time back to 00:00:00".format(ip_address, input_port, ip_address, input_port))

def reset_timer(*args):
  global running
  global time
  time = initial_time 
  running = False
  txt_instructions.set("Send /timer/start to {}:{} to start the timer".format(ip_address, input_port))

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
