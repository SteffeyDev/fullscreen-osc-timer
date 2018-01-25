# Full Screen OSC-Controlled Timer

This is a simple python script that shows a white stopwatch on a black background that is OSC controller.  Works great during shows on a Raspberry Pi or other lightweight micro-computer.

## Installation

```sh
pip3 install python-osc
pip3 install netifaces
git clone https://github.com/steffeydev/fullscreen-osc-timer
```

You may need to update the interface name in the script if it is not `eth0`

Feel free to change input and output ports in script

## Running

```sh
cd fullscreen-osc-timer
python3 timer.py
```
