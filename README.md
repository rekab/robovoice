# RoboVoice

Animates a
[144 LED Adafruit DotStar strip](https://www.amazon.com/gp/product/B01BMRUPKE)
using the [pyo library](http://ajaxsoundstudio.com/software/pyo/) to pick up
and change a voice to sound _kinda_ robotic.

Tested with a
[C-Media external USB sound card](https://www.amazon.com/gp/product/B001MSS6CS/)
on a rpi4.


## Installation

### Hardware

Plug in DotStar pins:

* Yellow: GPIO11 (`SCLK`) - clock
* Green: GPIO10 (MOSI) - data
* Black: GND

DotStar gets its power using 5v a micro USB.

* [Micro USB pinboard](https://www.amazon.com/gp/product/B0183KF7TM/)
* 1000µF (6.3V or higher) capacitor close to the strip (between 5V and GND
  wires) to handle inrush curent.

### Software pre-reqs

```
sudo apt install libportaudio2
sudo apt install libportmidi0
sudo apt install liblo-tools
sudo apt install libsndfile1

python3 -m venv voice-env
source voice-env/bin/activate
pip install -r requirements.txt
```

Add to crontab:

```
@reboot /home/pi/code/robovoice/run.sh 2>&1 | multilog s1000000 n10 /home/pi/robovoice-logs/
```
