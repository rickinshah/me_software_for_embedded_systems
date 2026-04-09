import config as cf


def lighten_color(hex_color, factor=0.4):
    """Return a lighter version of a hex color for the highlight."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def darken_color(hex_color, factor=0.5):
    """Return a darker version of a hex color for the shadow."""
    r = int(int(hex_color[1:3], 16) * factor)
    g = int(int(hex_color[3:5], 16) * factor)
    b = int(int(hex_color[5:7], 16) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


class Brick:
    def __init__(self, canvas, x, y, w, h, color="white", row=0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.alive = True
        self.color = color
        self.row = row

        shadow = darken_color(color)
        highlight = lighten_color(color)
        pad = 2

        self.shadow_obj = canvas.create_rectangle(
            x + 2, y + 2, x + w + 2, y + h + 2, fill=shadow, outline=""
        )
        self.obj = canvas.create_rectangle(x, y, x + w, y + h, fill=color, outline="")
        self.highlight_obj = canvas.create_rectangle(
            x + pad, y + pad, x + w - pad, y + h * 0.35, fill=highlight, outline=""
        )

    def draw(self, canvas):
        if self.alive:
            canvas.coords(
                self.shadow_obj,
                self.x + 2,
                self.y + 2,
                self.x + self.w + 2,
                self.y + self.h + 2,
            )
            canvas.coords(self.obj, self.x, self.y, self.x + self.w, self.y + self.h)
            canvas.coords(
                self.highlight_obj,
                self.x + 2,
                self.y + 2,
                self.x + self.w - 2,
                self.y + self.h * 0.35,
            )
        else:
            canvas.coords(self.shadow_obj, 0, 0, 0, 0)
            canvas.coords(self.obj, 0, 0, 0, 0)
            canvas.coords(self.highlight_obj, 0, 0, 0, 0)
