import config as cf


def lighten_color(hex_color, factor=0.6):
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


class Paddle:
    def __init__(self, canvas):
        self.x = cf.PADDLE_X
        self.y = cf.PADDLE_Y
        self.width = cf.PADDLE_WIDTH
        self.height = cf.PADDLE_HEIGHT
        self.speed = cf.PADDLE_SPEED

        color = cf.PADDLE_COLOR
        highlight = lighten_color(color)

        self.obj = canvas.create_rectangle(
            self.x,
            self.y,
            self.x + self.width,
            self.y + self.height,
            fill=color,
            outline="",
        )
        self.highlight_obj = canvas.create_rectangle(
            self.x + 2,
            self.y + 1,
            self.x + self.width - 2,
            self.y + self.height * 0.4,
            fill=highlight,
            outline="",
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
        canvas.coords(
            self.highlight_obj,
            self.x + 2,
            self.y + 1,
            self.x + self.width - 2,
            self.y + self.height * 0.4,
        )

    def reset(self):
        self.x = cf.PADDLE_X
        self.y = cf.PADDLE_Y

    @property
    def center(self):
        return self.x + self.width / 2
