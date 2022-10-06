import adafruit_dotstar as dotstar
import board
import pyo
import queue
import sys
import threading
import time

NUM_PIXELS = 73
BRIGHTNESS = 0.5

# Number of pixels that "fade" in.
GRADIENT_WIDTH = 5

# Pre-computed two-dimmensional array of pixel colors
BAR_GRADIENTS = []

def PrecomputeBarGradients():
    for num_pixels in range(0, NUM_PIXELS+1):
        up_gradient = [
                # (r, g, b) values: gets whiter
                (10+p, (p*p)//500, (p*p)//500)
                # Step from 0 to 255
                for p in range(0, 255, 255//GRADIENT_WIDTH)]

        between_color = (20, 255, 0)

        down_gradient = up_gradient[:]
        # Start with a black bar.
        color_pixels = [(0, 0, 0)] * NUM_PIXELS

        # Where we start and end coloring in.
        color_fill_start = max((NUM_PIXELS//2) - (num_pixels//2), 0)
        color_fill_end = min(color_fill_start + num_pixels, NUM_PIXELS - 1)

        while color_fill_start <= color_fill_end:
            if up_gradient:
                color_pixels[color_fill_start] = up_gradient.pop(0)
            else:
                color_pixels[color_fill_start] = between_color
            color_fill_start += 1
            if down_gradient:
                color_pixels[color_fill_end] = down_gradient.pop(0)
            else:
                color_pixels[color_fill_end] = between_color
            color_fill_end -= 1

        BAR_GRADIENTS.append(color_pixels)


class ColorBar(object):
    def __init__(self):
        self._queueFull = False
        self._numFullQueue = 0
        self._shutdown = False
        self.q = queue.Queue(maxsize=15)
        # Setup the light bar
        self.dots = dotstar.DotStar(
            board.SCK, board.MOSI, NUM_PIXELS,
            brightness=BRIGHTNESS, auto_write=False)
        self.dots.fill((0, 0, 0))

        self.t = threading.Thread(target=self._colorBar)

    def start(self):
        print('starting thread...')
        self.t.start()

    def setAmplitude(self, *args):
        """Should be called from the main thread."""
        mag = max(args) * 2
        # Don't block to prevent lag
        try:
            self.q.put_nowait(mag)
            self._queueFull = False
        except queue.Full:
            if self._queueFull:
                self._numFullQueue += 1
            self._queueFull = True
            print(f'{time.ctime()}: queue full!')
            if self._numFullQueue > 50:
                print(f'{time.ctime()}: giving up!')
                self._shutdown = True
                sys.exit(0)

    def _colorBar(self):
        print('_colorBar() starting')
        prev_value = last_pixel = 0
        while not self._shutdown:
            mag = self.q.get(block=True)
            last_pixel = min(NUM_PIXELS, int(mag * NUM_PIXELS))
            if last_pixel == prev_value:
                # No change: Don't waste time writing to the bar.
                continue
            # Save the value for next time.
            prev_value = last_pixel

            # Lookup the pixel values from the pre-computed global
            color_pixels = BAR_GRADIENTS[last_pixel]
            for idx in range(0, len(color_pixels)):
                self.dots[idx] = color_pixels[idx]
            # auto_write turned off for performance, necessary to call show()
            self.dots.show()

    def shutdown(self):
        print('shutting down')
        self._shutdown = True
        try:
            self.q.put_nowait(0)
        except:
            pass
        self.t.join()


def main():
    # Initialize globals
    PrecomputeBarGradients()

    # Setup pyo
    s = pyo.Server()
    s.setInputDevice(1)
    s.setOutputDevice(1)
    s.boot()

    mic = pyo.Input(chnl=0)

    #h = pyo.Harmonizer(mic, transpo=5, feedback=0.2, winsize=0.2)
    h = pyo.Harmonizer(mic, transpo=-3, feedback=0.2, winsize=0.02)
    mix = h.mix(2)

    feedback = pyo.Sig(0.8, mul=0.95)
    flg = pyo.Delay(pyo.DCBlock(mix), delay=.025, feedback=feedback)

    # Mix the original source with its delayed version.
    # Compress the mix to normalize the output signal.
    output = pyo.Compress(mix + flg, thresh=-20, ratio=4).out()

    # Feed peak amp to setAmplitude
    cb = ColorBar()
    amp = pyo.PeakAmp(output, function=cb.setAmplitude)
    amp.polltime(.1)

    cb.start()
    s.start()
    if sys.stdout.isatty():
        import code
        code.interact(local=locals())
    else:
        while True:
            time.sleep(1)

    cb.shutdown()

if __name__ == '__main__':
    main()
