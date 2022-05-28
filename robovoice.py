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


class ColorBar(object):
    def __init__(self):
        self._shutdown = False
        self.q = queue.Queue()
        # Setup the light bar
        self.dots = dotstar.DotStar(
                board.SCK, board.MOSI, NUM_PIXELS, brightness=BRIGHTNESS)
        self.dots.fill((0, 0, 0))

        self.t = threading.Thread(target=self._colorBar)

    def start(self):
        print('starting thread...')
        self.t.start()

    def setAmplitude(self, *args):
        """Should be called from the main thread."""
        mag = max(args) * 2
        self.q.put(mag)
        #print('mag=%s last_pixel=%s' % (mag, last_pixel))

    def _colorBar(self):
        print('_colorBar() starting')
        prev_value = last_pixel = 0
        while not self._shutdown:
            mag = self.q.get(block=True)
            #print('got %s' % mag)
            last_pixel = min(NUM_PIXELS, int(mag * NUM_PIXELS))
            if last_pixel == prev_value:
                # No change: Don't waste time writing to the bar.
                continue
            prev_value = last_pixel
            #print('change: %d' % (prev_value - last_pixel))
            #for idx in range(0, last_pixel):
            #    self.dots[idx] = (255, 0, 0)
            #for idx in range(last_pixel, NUM_PIXELS):
            #    self.dots[idx] = (0, 0, 0)
            #prev_last_pixel = last_pixel
            self._fillBar(last_pixel)

    def _fillBar(self, num_pixels):
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
        #print(f'start={color_fill_start} end={color_fill_end} max={NUM_PIXELS}')

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

        for idx in range(0, len(color_pixels)):
            self.dots[idx] = color_pixels[idx]


    def shutdown(self):
        print('shutting down')
        self._shutdown = True
        self.q.put(0)
        self.t.join()


def main():
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
    # TODO: polltime(.02)?

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
