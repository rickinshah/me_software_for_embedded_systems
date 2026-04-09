import tkinter as tk
from game import Game
import helpers as hp
import config as cf

root = tk.Tk()
root.title("BREAKOUT")
root.resizable(False, False)
canvas = tk.Canvas(root, width=cf.WIDTH, height=cf.HEIGHT, bg=cf.BG_COLOR, highlightthickness=0)
canvas.pack()

game = Game(root, canvas)

root.bind("<KeyPress>", hp.key_down)
root.bind("<KeyRelease>", hp.key_up)

game.loop()
root.mainloop()
