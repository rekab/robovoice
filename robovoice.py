import pyo

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

def what(*args):
    print(args)

amp = pyo.PeakAmp(output, function=what)

s.start()
import code
code.interact(local=locals())
