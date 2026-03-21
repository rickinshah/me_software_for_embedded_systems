keys = set()

def key_down(event):
    keys.add(event.keysym)

def key_up(event):
    keys.discard(event.keysym)
