import threading

BUFFER_SIZE = 5
ITEMS = 100

buffer = [None] * BUFFER_SIZE

write_buf = 0
read_buf = 0

full = threading.Semaphore(0)
empty = threading.Semaphore(BUFFER_SIZE)


def producer():
    global write_buf

    item_id = 0

    while item_id < ITEMS:
        empty.acquire()
        print(f"Producer writing to {write_buf}")
        buffer[write_buf] = f"item-{item_id}"
        write_buf = (write_buf + 1) % BUFFER_SIZE
        item_id += 1
        full.release()

def consumer():
    global read_buf

    consumed = 0

    while consumed < ITEMS:
        full.acquire()
        print(f"    consumed: {buffer[read_buf]}")
        read_buf = (read_buf + 1) % BUFFER_SIZE
        consumed += 1
        empty.release()


producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

producer_thread.start()
consumer_thread.start()

producer_thread.join()
consumer_thread.join()

print("Done")
