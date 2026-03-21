import tkinter as tk
import time
import config as cf
import helpers as hp

root = tk.Tk()
canvas = tk.Canvas(root, width=cf.WIDTH, height=cf.HEIGHT, bg="black")
canvas.pack()

ball_x, ball_y, ball_size = cf.BALL_X, cf.BALL_Y, cf.BALL_SIZE
ball_vx, ball_vy = cf.BALL_VX, cf.BALL_VY
paddle_x, paddle_y, paddle_width, paddle_height = cf.PADDLE_X, cf.PADDLE_Y, cf.PADDLE_WIDTH, cf.PADDLE_HEIGHT
paddle_speed = cf.PADDLE_SPEED

ball = canvas.create_oval(ball_x, ball_y, ball_x + ball_size, ball_x + ball_size, fill="white")
rect = canvas.create_rectangle(paddle_x, paddle_y, paddle_x + paddle_width, paddle_y + paddle_height, fill="white")


def update():
    move_ball()
    move_paddle()

def draw():
    canvas.coords(rect, paddle_x, paddle_y, paddle_x+paddle_width, paddle_y+paddle_height)
    canvas.coords(ball, ball_x, ball_y, ball_x+ball_size, ball_y+ball_size)

def move_ball():
    global ball_x, ball_y, ball_vx, ball_vy

    ball_x += ball_vx
    ball_y += ball_vy

    if((ball_x + ball_size >= paddle_x and ball_x <= paddle_x + paddle_width) and ball_y < paddle_y and (paddle_y - (ball_y+ball_size) <= 0)) and (ball_vy > 0):
        ball_vy *= -1

    if(ball_x <= 0 or ball_x+ball_size >= cf.WIDTH):
        ball_vx *= -1
    if(ball_y <= 0):
        ball_vy *= -1
    if((ball_y-ball_size/2) >= cf.HEIGHT):
        ball_y= cf.BALL_Y

def move_paddle():
    global paddle_x
    if "Left" in hp.keys or "a" in hp.keys:
        paddle_x -= paddle_speed
    if "Right" in hp.keys or "d" in hp.keys:
        paddle_x += paddle_speed
    paddle_x = max(0, min(cf.WIDTH-paddle_width, paddle_x))

def game_loop():
    update()
    draw()
    root.after(16, game_loop)

root.bind("<KeyRelease>", hp.key_up)
root.bind("<KeyPress>", hp.key_down)
game_loop()
root.mainloop()
