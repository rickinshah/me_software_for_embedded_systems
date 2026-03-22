from ball import Ball
from paddle import Paddle
from enum import Enum
import helpers as hp
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
        self.ball = Ball(canvas)
        self.paddle = Paddle(canvas)

    def update(self):
        missed = self.ball.move(self.paddle)
        if missed:
            self.state = GameState.PAUSED
            self.ball.reset_position()

    def draw(self):
        self.ball.draw(self.canvas)
        self.paddle.draw(self.canvas)

    def handle_input(self):
        pressed = lambda k: k in hp.keys and k not in hp.prev_keys

        # 1. SPACE toggles pause (both directions)
        if any(pressed(k) for k in cf.SPACE):
            if self.state == GameState.RUNNING:
                self.state = GameState.PAUSED
            elif self.state == GameState.PAUSED:
                self.state = GameState.RUNNING
            return  # prevent double-trigger in same frame

        # 2. Any key resumes (only if paused)
        if self.state == GameState.PAUSED:
            if any(k not in hp.prev_keys for k in hp.keys):
                self.state = GameState.RUNNING

        # 3. Movement only when running
        if self.state == GameState.RUNNING:
            self.paddle.move(hp.keys)

    def loop(self):
        self.handle_input()

        if self.state == GameState.RUNNING:
            self.update()

        self.draw()

        hp.prev_keys = hp.keys.copy()

        self.root.after(16, self.loop)
