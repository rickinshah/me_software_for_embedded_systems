import math
import random
import config as cf


class Ball:
    def __init__(self, canvas):
        self.x = cf.BALL_X
        self.y = cf.BALL_Y
        self.vx = cf.BALL_VX
        self.vy = cf.BALL_VY
        self.size = cf.BALL_SIZE

        self.obj = canvas.create_oval(
            self.x,
            self.y,
            self.x + self.size,
            self.y + self.size,
            fill=cf.BALL_COLOR,
            outline="",
        )

    def move(self, paddle):
        self.x += self.vx
        self.y += self.vy

        if (
            self.vy > 0
            and self.y + self.size - self.vy <= paddle.y
            and self.x <= paddle.x + paddle.width
            and paddle.x <= self.x + self.size
            and paddle.y <= self.y + self.size
        ):
            speed, angle = self.calculate_speed_and_angle(paddle)
            self.vx = speed * math.sin(angle)
            if abs(self.vx) < 1:
                self.vx = random.choice([-2, 2])
            self.vy = -abs(speed * math.cos(angle))
        if self.x <= 0 or self.x + self.size >= cf.WIDTH:
            self.vx *= -1
        if self.y <= 0:
            self.vy *= -1
        if (self.y - self.size / 2) >= cf.HEIGHT:
            return True
        return False

    def draw(self, canvas):
        canvas.coords(self.obj, self.x, self.y, self.x + self.size, self.y + self.size)

    def calculate_speed_and_angle(self, paddle):
        cx, _ = self.center
        offset = (cx - paddle.center) / (paddle.width / 2)
        offset = max(-1, min(1, offset))
        speed = math.sqrt(self.vx**2 + self.vy**2)
        angle = offset * cf.MAX_ANGLE
        return speed, angle

    def reset_full(self):
        self.x = cf.BALL_X
        self.y = cf.BALL_Y
        self.vx = cf.BALL_VX
        self.vy = cf.BALL_VY

    def reset_position(self):
        self.y = cf.BALL_Y
        self.x = cf.BALL_X

    @property
    def center(self):
        return self.x + self.size / 2, self.y + self.size / 2
