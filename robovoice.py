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

h = pyo.Harmonizer(mic, transpo=5, feedback=0.2, winsize=0.2)
#output = f.mix(2).out()
mix = h.mix(2)

feedback = pyo.Sig(0.7, mul=0.95)  # 0 --> 1
flg = pyo.Delay(pyo.DCBlock(mix), delay=.02, feedback=feedback)

# Mix the original source with its delayed version.
# Compress the mix to normalize the output signal.
output = pyo.Compress(mix + flg, thresh=-20, ratio=4).out()

#
######
## From: http://ajaxsoundstudio.com/pyodoc/examples/07-effects/05-hand-made-chorus.html
## Sets values for 8 LFO'ed delay lines (you can add more if you want!).
## LFO frequencies.
#freqs = [0.254, 0.465, 0.657, 0.879, 1.23, 1.342, 1.654, 1.879]
## Center delays in seconds.
#cdelay = [0.0087, 0.0102, 0.0111, 0.02254, 0.0134, 0.01501, 0.01707, 0.0178]
## Modulation depths in seconds.
#adelay = [0.009, 0.0042, 0.0043, 0.0014, 0.0015, 0.0016, 0.002, 0.0023]
#
## Create 8 sinusoidal LFOs with center delays "cdelay" and depths "adelay".
#lfos = pyo.Sine(freqs, mul=adelay, add=cdelay)
#
## Create 8 modulated delay lines with a little feedback and send the signals
## to the output. Streams 1, 3, 5, 7 to the left and streams 2, 4, 6, 8 to the
## right (default behaviour of the out() method).
#d = pyo.Delay(compressed, lfos, feedback=0.9, mul=0.7)
#
#lfo4 = pyo.Sine(0.5).range(0.1, 3.75)
#osc4 = pyo.SuperSaw(freq=187.5, detune=lfo4, mul=1)
#
#output = pyo.Selector([d, osc4]).out()

#####


# Feed peak amp to setAmplitude
amp = pyo.PeakAmp(output, function=setAmplitude)
# TODO: polltime(.02)?

# http://ajaxsoundstudio.com/pyodoc/api/classes/generators.html#pyo.SuperSaw

t = threading.Thread(target=colorBar)
t.start()

s.start()
import code
code.interact(local=locals())
shutdown = True
t.join()
