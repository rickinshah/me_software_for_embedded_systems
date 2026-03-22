import config as cf


class Paddle:
    def __init__(self, canvas):
        self.x = cf.PADDLE_X
        self.y = cf.PADDLE_Y
        self.width = cf.PADDLE_WIDTH
        self.height = cf.PADDLE_HEIGHT
        self.speed = cf.PADDLE_SPEED
        self.obj = canvas.create_rectangle(
            self.x, self.y, self.x + self.width, self.y + self.height, fill="white"
        )

    def move(self, keys):
        if keys & set(cf.LEFT):
            self.x -= self.speed
        elif keys & set(cf.RIGHT):
            self.x += self.speed
        self.x = max(0, min(cf.WIDTH - self.width, self.x))

    def draw(self, canvas):
        canvas.coords(
            self.obj, self.x, self.y, self.x + self.width, self.y + self.height
        )

    @property
    def center(self):
        return self.x + self.width / 2
