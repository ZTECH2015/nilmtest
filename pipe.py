from multiprocessing import Process, Pipe
import time
import numpy as np

def reader(pipe):
    output_p, input_p = pipe
    input_p.close()    # We are only reading
    while True:
        try:
            msg = output_p.recv()    # Read from the output pipe and do nothing
            print msg
        except EOFError:
            break

def writer(count, input_p):
    for ii in xrange(0, count):
        input_p.send(np.random.random(ii))
        time.sleep(1)             # Write 'count' numbers into the input pipe

if __name__=='__main__':
    for count in [10**4, 10**5, 10**6]:
        output_p, input_p = Pipe()
        reader_p = Process(target=reader, args=((output_p, input_p),))
        reader_p.start()     # Launch the reader process

        output_p.close()       # We no longer need this part of the Pipe()
        _start = time.time()
        writer(count, input_p) # Send a lot of stuff to reader()
        input_p.close()        # Ask the reader to stop when it reads EOF
        reader_p.join()
        print "Sending %s numbers to Pipe() took %s seconds" % (count, 
            (time.time() - _start))