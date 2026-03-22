import tkinter as tk
from game import Game
import helpers as hp
import config as cf

root = tk.Tk()
canvas = tk.Canvas(root, width=cf.WIDTH, height=cf.HEIGHT, bg="black")
canvas.pack()

game = Game(root, canvas)

root.bind("<KeyPress>", hp.key_down)
root.bind("<KeyRelease>", hp.key_up)

game.loop()
root.mainloop()
