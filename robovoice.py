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
            print('change: %d' % (prev_last_pixel - last_pixel))
            for idx in range(0, last_pixel):
                dots[idx] = (255, 0, 0)
            for idx in range(last_pixel, NUM_PIXELS):
                dots[idx] = (0, 0, 0)
            prev_last_pixel = last_pixel
        time.sleep(.02)



# Setup pyo
s = pyo.Server()
s.setInputDevice(1)
s.setOutputDevice(1)
s.boot()

mic = pyo.Input(chnl=0)

h = pyo.Harmonizer(mic, transpo=5)
f = pyo.FreqShift(h, shift=50)
#voc = pyo.Vocoder(c, excite, freq=200, spread=1, q=50, slope=10)#.out()
mm = pyo.Mixer(outs=1, chnls=2, time=.025)
mm.addInput(0, f)
mm.setAmp(0, 0, 0.5)
output = pyo.Sig(mm[0]).out()

amp = pyo.PeakAmp(output, function=setAmplitude)

t = threading.Thread(target=colorBar)
t.start()

s.start()
import code
code.interact(local=locals())
shutdown = True
t.join()
