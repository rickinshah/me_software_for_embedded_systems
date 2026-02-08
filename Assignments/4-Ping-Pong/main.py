import threading
import time

BUFFER_SIZE = 5

# Two buffers: ping (0) and pong (1)
buffer = [[None]*BUFFER_SIZE, [None]*BUFFER_SIZE]

write_buf = 0
read_buf  = 0

data_ready = [False, False]

lock = threading.Lock()

def producer():
    global write_buf, read_buf

    item_id = 0
    while item_id < 100:
        if not data_ready[write_buf]:
            print(f"Producer writing to buffer {write_buf}")

            for i in range(BUFFER_SIZE):
                buffer[write_buf][i] = f"item-{item_id}"
                item_id += 1
                time.sleep(0.1)

            with lock:
                data_ready[write_buf] = True
                write_buf = (write_buf + 1) & 1

def consumer():
    global write_buf, read_buf

    consumed = 0
    while consumed < 100:
        if data_ready[read_buf]:
            print(f"Consumer reading from buffer {read_buf}")

            for item in buffer[read_buf]:
                print("   consumed:", item)
                consumed += 1
                time.sleep(0.15)

            with lock:
                data_ready[read_buf] = False
                read_buf = (read_buf + 1) & 1

producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

producer_thread.start()
consumer_thread.start()

producer_thread.join()
consumer_thread.join()

print("Done")
