from ball import Ball
from paddle import Paddle
from enum import Enum
import helpers as hp
from brick import Brick
import config as cf


class GameState(Enum):
    RUNNING = 1
    PAUSED = 2
    GAME_OVER = 3


class Game:
    def __init__(self, root, canvas):
        self.root = root
        self.canvas = canvas
        self.state = GameState.PAUSED
        self.score = 0
        self.lives = 3

        # self._draw_background()

        self.ball = Ball(canvas)
        self.paddle = Paddle(canvas)
        self.create_bricks()

        self.score_text = canvas.create_text(
            20,
            cf.HEIGHT - 30,
            text="SCORE: 0",
            fill="#aaaaff",
            anchor="w",
            font=("Courier", 18, "bold"),
        )
        self.lives_text = canvas.create_text(
            cf.WIDTH - 20,
            cf.HEIGHT - 30,
            text="LIVES: ♥ ♥ ♥",
            fill="#ff6699",
            anchor="e",
            font=("Courier", 18, "bold"),
        )
        self.status_text = canvas.create_text(
            cf.WIDTH / 2,
            cf.HEIGHT / 2 + 80,
            text="PRESS SPACE TO START",
            fill="#ffffff",
            anchor="center",
            font=("Courier", 22, "bold"),
        )

    # def _draw_background(self):
    #     for x in range(0, cf.WIDTH, 60):
    #         self.canvas.create_line(x, 0, x, cf.HEIGHT, fill="#111122", width=1)
    #     for y in range(0, cf.HEIGHT, 60):
    #         self.canvas.create_line(0, y, cf.WIDTH, y, fill="#111122", width=1)

    def update(self):
        missed = self.ball.move(self.paddle)
        if missed:
            self.lives -= 1
            self._update_hud()
            if self.lives <= 0:
                self.state = GameState.GAME_OVER
                self.canvas.itemconfig(
                    self.status_text, text="GAME OVER - PRESS SPACE", fill="#ff3366"
                )
            else:
                self.state = GameState.PAUSED
                self.paddle.reset()
                self.ball.reset_position()
                self.canvas.itemconfig(
                    self.status_text, text="PRESS SPACE TO CONTINUE", fill="#ffffff"
                )

        self.check_brick_collision()

    def draw(self):
        self.ball.draw(self.canvas)
        self.paddle.draw(self.canvas)
        for brick in self.bricks:
            brick.draw(self.canvas)

    def handle_input(self):
        pressed = lambda k: k in hp.keys and k not in hp.prev_keys

        if any(pressed(k) for k in cf.SPACE):
            if self.state == GameState.GAME_OVER:
                self._restart()
                return
            if self.state == GameState.RUNNING:
                self.state = GameState.PAUSED
                self.canvas.itemconfig(self.status_text, text="PAUSED", fill="#aaaaff")
            elif self.state == GameState.PAUSED:
                self.state = GameState.RUNNING
                self.canvas.itemconfig(self.status_text, text="")
            return

        if self.state == GameState.RUNNING:
            self.paddle.move(hp.keys)

    def loop(self):
        self.handle_input()

        if self.state == GameState.RUNNING:
            self.update()

        self.draw()
        hp.prev_keys = hp.keys.copy()
        self.root.after(16, self.loop)

    def _restart(self):
        self.score = 0
        self.lives = 3
        self.ball.reset_full()
        self.paddle.reset()
        for brick in self.bricks:
            self.canvas.coords(brick.obj, 0, 0, 0, 0)
            self.canvas.coords(brick.shadow_obj, 0, 0, 0, 0)
            self.canvas.coords(brick.highlight_obj, 0, 0, 0, 0)
        self.create_bricks()
        self._update_hud()
        self.state = GameState.PAUSED
        self.canvas.itemconfig(
            self.status_text, text="PRESS SPACE TO START", fill="#ffffff"
        )

    def _update_hud(self):
        self.canvas.itemconfig(self.score_text, text=f"SCORE: {self.score}")
        hearts = "♥ " * self.lives + "♡ " * (3 - self.lives)
        self.canvas.itemconfig(self.lives_text, text=f"LIVES: {hearts.strip()}")

    def create_bricks(self):
        self.bricks = []
        rows = cf.BRICK_ROW
        cols = cf.BRICK_COLS
        padding = cf.BRICK_PADDING
        brick_w = (cf.WIDTH - (cols + 1) * padding) / cols
        brick_h = cf.BRICK_H
        top_offset = cf.HEIGHT * 0.05
        total_width = cols * brick_w + (cols + 1) * padding
        start_x = (cf.WIDTH - total_width) / 2

        for r in range(rows):
            color = cf.BRICK_ROW_COLORS[r % len(cf.BRICK_ROW_COLORS)]
            for c in range(cols):
                x = start_x + padding + c * (brick_w + padding)
                y = top_offset + r * (brick_h + padding)
                brick = Brick(self.canvas, x, y, brick_w, brick_h, color=color, row=r)
                self.bricks.append(brick)

    def check_brick_collision(self):
        for brick in self.bricks:
            if not brick.alive:
                continue
            if (
                self.ball.x <= brick.x + brick.w
                and self.ball.x + self.ball.size >= brick.x
                and self.ball.y <= brick.y + brick.h
                and self.ball.y + self.ball.size >= brick.y
            ):
                self.alive = True
                brick.alive = False
                self.ball.vy *= -1
                self.score += 10
                self._update_hud()
                break
