# Chord approximator

It performs Fourier transmission on samples from a wav file and finds peaks there. 
After that, it`s possible, for example, to play some sound from detected peaks.

It`s a very interesting and mult-step task, because the gragh is assumed to be extremely noisy.
It`s designed to be extremely robust and fast enough to run on microcontroller in real time.
So, many tecniques had been used. 
For example, gaussian window smooths the graph and only peaks, which are heiger than the value of the smoothed function, can be percieved as peaks.

Here`s an example of it`s work:
![Alt text](relative/Figure_1.png?raw=true "Title")
