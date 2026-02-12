import threading
import time
import random

BUFFER_SIZE = 5
ITEMS = 20

buffer = [None] * BUFFER_SIZE

head = 0
tail = 0
count = 0

lock = threading.Lock()

def producer():
    global head, count
    item_id = 0


    while item_id < ITEMS:
        with lock:
            if count < BUFFER_SIZE:
                print(f"Producer writing to {head}")
                buffer[head] = f"item-{item_id}"
                head = (head + 1) % BUFFER_SIZE
                item_id += 1
                count += 1
        time.sleep(random.uniform(0.1, 0.6))

def consumer():
    global tail, count
    consumed = 0

    while consumed < ITEMS:
        with lock:
            if count > 0:
                print(f"    consumed: {buffer[tail]}")
                tail = (tail + 1) % BUFFER_SIZE
                consumed += 1
                count -= 1
        time.sleep(random.uniform(0.1, 0.6))


producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

producer_thread.start()
consumer_thread.start()

producer_thread.join()
consumer_thread.join()

print("Done")
