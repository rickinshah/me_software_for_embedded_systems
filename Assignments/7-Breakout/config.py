import math

HEIGHT = 1000
WIDTH = 1200
BALL_X, BALL_Y = WIDTH / 2, HEIGHT / 2
BALL_VX, BALL_VY, BALL_SIZE = HEIGHT / 120, HEIGHT / 120, HEIGHT / 60
PADDLE_WIDTH, PADDLE_HEIGHT = WIDTH / 16, HEIGHT / 60
PADDLE_X, PADDLE_Y = (WIDTH - PADDLE_WIDTH) / 2, (HEIGHT - (HEIGHT / 25))
PADDLE_SPEED = HEIGHT * 1.5 / 100
BRICK_ROW = 10
BRICK_COLS = 12
BRICK_H = HEIGHT * 3 / (10 * BRICK_ROW)
BRICK_PADDING = WIDTH * 0.005
MAX_ANGLE = math.radians(60)
LEFT = ["a", "Left"]
RIGHT = ["d", "Right"]
SPACE = ["space"]
ALL_KEYS = LEFT + RIGHT + SPACE

BRICK_ROW_COLORS = [
    "#FF2D55",  # row 0 - neon red/pink
    "#FF6B35",  # row 1 - orange
    "#FFD60A",  # row 2 - yellow
    "#34C759",  # row 3 - green
    "#30D158",  # row 4 - mint
    "#5E5CE6",  # row 5 - purple
    "#BF5AF2",  # row 6 - violet
    "#FF375F",  # row 7 - pink
    "#FF9F0A",  # row 8 - amber
    "#0A84FF",  # row 9 - blue
]

BG_COLOR = "#0a0a1a"
PADDLE_COLOR = "#E0E0FF"
BALL_COLOR = "#FFFFFF"
