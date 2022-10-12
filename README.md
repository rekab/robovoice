# RoboVoice

Animates a 144 LED Adafruit DotStar strip using the pyo library.

Tested with a C-Media external USB sound card on a rpi4.

https://docs.google.com/document/d/1wDfdpEdLlfDwexNORDDVtKARrnzqxjQtfFlcrvqhabM/edit

## Installation

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
@reboot /home/pi/code/robovoice/daemon.sh 2>&1 | multilog s1000000 n10 /home/pi/robovoice-logs/
```
