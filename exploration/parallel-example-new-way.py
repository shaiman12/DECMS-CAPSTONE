import concurrent.futures
import time

start = time.perf_counter()


def do_something(seconds):
    print(f'sleeping for {seconds} second(s)...')
    time.sleep(1)
    return 'awake'


with concurrent.futures.ThreadPoolExecutor() as executor:
    threads = []
    for i in range(10):
        f = executor.submit(do_something, 1)
        threads.append(f)

    for thread in concurrent.futures.as_completed(threads):
        print(thread.result())

finish = time.perf_counter()
print(f'finished in {round(finish-start,2)}seconds')
