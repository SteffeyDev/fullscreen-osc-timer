#!/usr/bin/python3

from tkinter import *
from tkinter import ttk
from tkinter import font
import time
import datetime
from pythonosc import osc_server, dispatcher, udp_client
import netifaces
from threading import Timer, Thread

# Network Variables -- CHANGE THESE
input_port = 8500
broadcast_port = 9000
network_interface = 'eth0'

# Other Settings -- Feel free to change
show_help_after_start = False

def quit(*args):
  stop_timer()
  root.destroy()
          
def show_time():
  start = datetime.datetime.now()

  global start_time
  global feeback
  global running

  time_diff = datetime.datetime.now() - start_time
  time = int(time_diff.total_seconds())

  if (not running):
    return

  # Calculate time
  hours = int(time / 3600)
  minutes = int((time - (hours * 3600)) / 60)
  seconds = time - (hours * 3600) - (minutes * 60)

  time_string = '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)

  # Show the time left
  txt.set(time_string)

  # Send out to show on OSC device
  feedback.send_message("/timer/time", time_string)

  if (not show_help_after_start):
    txt_instructions.set("")

  end = datetime.datetime.now()
  exec_time = end - start
  root.after(int(998 - (exec_time.total_seconds() * 1000)), show_time)

def start_timer(*args):
  global running
  global start_time
  global stopped
  global stop_time
  if not running:
    running = True
    if stopped:
      start_time = start_time + (datetime.datetime.now() - stop_time)
    else:
      start_time = datetime.datetime.now()
    stopped = False
    root.after(1000, show_time)

def stop_timer(*args):
  global running
  global stopped
  global stop_time
  if running:
    stop_time = datetime.datetime.now()
    stopped = True
    running = False

def reset_timer(*args):
  global running
  global stopped
  running = False
  stopped = False
  txt.set("00:00:00")
  feedback.send_message("/timer/time", "00:00:00")

# Global State Variables
ip_address = netifaces.ifaddresses(network_interface)[netifaces.AF_INET][0]['addr']
broadcast_address = netifaces.ifaddresses(network_interface)[netifaces.AF_INET][0]['broadcast']
running = False
start_time = None
stopped = False

feedback = udp_client.SimpleUDPClient(broadcast_address, broadcast_port, allow_broadcast=True)

# Use tkinter lib for showing the clock
root = Tk()
root.attributes("-fullscreen", True)
root.configure(background='black')
root.bind("x", quit)
style = ttk.Style()
style.theme_use('classic')
root.config(cursor="none")

fnt = font.Font(family='Helvetica', size=170, weight='bold')
txt = StringVar()
txt.set("00:00:00")
lbl = ttk.Label(root, textvariable=txt, font=fnt, foreground="white", background="black")
lbl.place(relx=0.5, rely=0.5, anchor=CENTER)

fnt_instructions = font.Font(family='Helvetica', size=25, weight='bold')
txt_instructions = StringVar()
txt_instructions.set("Listening at {}:{}\n/timer/start -> Start stopwatch\n/timer/stop -> Stop (pause) stopwatch\n/timer/reset -> Set time back to 00:00:00".format(ip_address, input_port))
lbl_instructions = ttk.Label(root, textvariable=txt_instructions, font=fnt_instructions, foreground="white", background="black", padding=30)
lbl_instructions.pack(side=BOTTOM)

dispatcher = dispatcher.Dispatcher()
dispatcher.map("/timer/start", start_timer)
dispatcher.map("/timer/stop", stop_timer)
dispatcher.map("/timer/reset", reset_timer)
dispatcher.map("/timer/quit", quit)

# We use BlockingOSCUDPServer to execute each incoming command in order
server = osc_server.BlockingOSCUDPServer(("0.0.0.0", input_port), dispatcher)
server_thread = Thread(target=server.serve_forever)
server_thread.start()

# This is a blocking function, will release when quit is called
root.mainloop()

server.shutdown()
