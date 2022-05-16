import adafruit_dotstar as dotstar
import board
import pyo
import threading
import time

NUM_PIXELS = 73
BRIGHTNESS = 0.5

# Setup the light bar
dots = dotstar.DotStar(
        board.SCK, board.MOSI, NUM_PIXELS, brightness=BRIGHTNESS)
dots.fill((0, 0, 0))

shutdown = False
last_pixel = 0
prev_last_pixel = 0

def setAmplitude(*args):
    global last_pixel
    mag = max(args) * 2
    last_pixel = min(NUM_PIXELS, int(mag * NUM_PIXELS))
    #print('mag=%s last_pixel=%s' % (mag, last_pixel))

def colorBar():
    print('colorBar() starting')
    global last_pixel, prev_last_pixel, shutdown
    while not shutdown:
        if last_pixel != prev_last_pixel:
            #print('change: %d' % (prev_last_pixel - last_pixel))
            for idx in range(0, last_pixel):
                dots[idx] = (255, 0, 0)
            for idx in range(last_pixel, NUM_PIXELS):
                dots[idx] = (0, 0, 0)
            prev_last_pixel = last_pixel
        time.sleep(.01)



# Setup pyo
s = pyo.Server()
s.setInputDevice(1)
s.setOutputDevice(1)
s.boot()

mic = pyo.Input(chnl=0)

h = pyo.Harmonizer(mic, transpo=5)
f = pyo.FreqShift(h, shift=50)
#output = f.mix(2).out()
mix = f.mix(2)


#####
# From: http://ajaxsoundstudio.com/pyodoc/examples/07-effects/05-hand-made-chorus.html
# Sets values for 8 LFO'ed delay lines (you can add more if you want!).
# LFO frequencies.
freqs = [0.254, 0.465, 0.657, 0.879, 1.23, 1.342, 1.654, 1.879]
# Center delays in seconds.
cdelay = [0.0087, 0.0102, 0.0111, 0.01254, 0.0134, 0.01501, 0.01707, 0.0178]
# Modulation depths in seconds.
adelay = [0.001, 0.0012, 0.0013, 0.0014, 0.0015, 0.0016, 0.002, 0.0023]

# Create 8 sinusoidal LFOs with center delays "cdelay" and depths "adelay".
lfos = pyo.Sine(freqs, mul=adelay, add=cdelay)

# Create 8 modulated delay lines with a little feedback and send the signals
# to the output. Streams 1, 3, 5, 7 to the left and streams 2, 4, 6, 8 to the
# right (default behaviour of the out() method).
output = pyo.Delay(mix, lfos, feedback=0.9, mul=0.7).out()

#####


# Feed peak amp to setAmplitude
amp = pyo.PeakAmp(output, function=setAmplitude)

t = threading.Thread(target=colorBar)
t.start()

s.start()
import code
code.interact(local=locals())
shutdown = True
t.join()
