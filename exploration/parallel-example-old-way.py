import threading
import time

start = time.perf_counter()


def do_something(seconds):
    print(f'sleeping for {seconds} second(s)...')
    time.sleep(seconds)
    print('awake')


threads = []
for i in range(10):
    t = threading.Thread(target=do_something, args=[1.5])
    t.start()
    threads.append(t)

for thread in threads:
    thread.join()

finish = time.perf_counter()
print(f'finished in {round(finish-start,2)}seconds')
