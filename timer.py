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
network_interface = 'en0'

# Other Settings -- Feel free to change
show_help_after_start = False

# Needed helper class
class RepeatedTimer(object):
  def __init__(self, interval, function, *args, **kwargs):
    self._timer     = None
    self.interval   = interval
    self.function   = function
    self.args       = args
    self.kwargs     = kwargs
    self.is_running = False

  def _run(self):
    self.is_running = False
    self.start()
    self.function(*self.args, **self.kwargs)

  def start(self):
    if not self.is_running:
      self._timer = Timer(self.interval, self._run)
      self._timer.start()
      self.is_running = True

  def stop(self):
    self._timer.cancel()
    self.is_running = False

def quit(*args):
  global timer
  timer.stop()
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

  # Send out to show on OSC device
  feedback.send_message("/timer/time", time_string)

  if (not show_help_after_start):
    txt_instructions.set("")

  # Update Time
  time += 1

def start_timer(*args):
  global timer
  timer.start()

def stop_timer(*args):
  global timer
  timer.stop()

def reset_timer(*args):
  global time
  global timer
  timer.stop()
  time = 0 
  txt.set("00:00:00")
  feedback.send_message("/timer/time", "00:00:00")

# Global State Variables
ip_address = netifaces.ifaddresses(network_interface)[netifaces.AF_INET][0]['addr']
broadcast_address = netifaces.ifaddresses(network_interface)[netifaces.AF_INET][0]['broadcast']
time = 0 
timer = RepeatedTimer(1, show_time)

feedback = udp_client.SimpleUDPClient(broadcast_address, broadcast_port, allow_broadcast=True)

# Use tkinter lib for showing the clock
root = Tk()
root.attributes("-fullscreen", True)
root.configure(background='black')
root.bind("x", quit)
style = ttk.Style()
style.theme_use('classic')

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

start_timer()

# This is a blocking function, will release when quit is called
root.mainloop()

server.shutdown()
