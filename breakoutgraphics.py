"""
This program describes a class that sets up and operates
a game reminiscent of 'Breakout'. Utilizing user input,
the game starts with a click and follows a ball that bounces
of blocks and a paddle controlled by the user's mouse.
"""
from campy.graphics.gwindow import GWindow
from campy.graphics.gobjects import GOval, GRect, GLabel
from campy.gui.events.mouse import onmouseclicked, onmousemoved
import random

# Color names to cycle through for brick rows.
COLORS = ['RED', 'ORANGE', 'YELLOW', 'GREEN', 'BLUE']

BRICK_SPACING = 5      # Space between bricks (in pixels). This space is used for horizontal and vertical spacing.
BRICK_WIDTH = 40       # Height of a brick (in pixels).
BRICK_HEIGHT = 15      # Height of a brick (in pixels).
BRICK_ROWS = 10        # Number of rows of bricks.
BRICK_COLS = 10        # Number of columns of bricks.
BRICK_OFFSET = 50      # Vertical offset of the topmost brick from the window top (in pixels).
BALL_RADIUS = 10       # Radius of the ball (in pixels).
PADDLE_WIDTH = 75      # Width of the paddle (in pixels).
PADDLE_HEIGHT = 15     # Height of the paddle (in pixels).
PADDLE_OFFSET = 50     # Vertical offset of the paddle from the window bottom (in pixels).

INITIAL_Y_SPEED = 5.0  # Initial vertical speed for the ball.
MAX_X_SPEED = 3.5      # Maximum initial horizontal speed for the ball.


class BreakoutGraphics:

    def __init__(self, ball_radius=BALL_RADIUS, paddle_width=PADDLE_WIDTH,
                 paddle_height=PADDLE_HEIGHT, paddle_offset=PADDLE_OFFSET,
                 brick_rows=BRICK_ROWS, brick_cols=BRICK_COLS,
                 brick_width=BRICK_WIDTH, brick_height=BRICK_HEIGHT,
                 brick_offset=BRICK_OFFSET, brick_spacing=BRICK_SPACING,
                 title='Breakout'):

        # Create a graphical window, with some extra space.
        window_width = brick_cols * (brick_width + brick_spacing) - brick_spacing
        window_height = brick_offset + 3 * (brick_rows * (brick_height + brick_spacing) - brick_spacing)
        self.window = GWindow(width=window_width, height=window_height, title=title)

        # Create a paddle.
        paddle_x = window_width / 2 - paddle_width / 2
        self.paddle_y = window_height - paddle_offset
        self.paddle = GRect(width=paddle_width, height=paddle_height, x=paddle_x, y=self.paddle_y)
        self.paddle.filled = True
        self.window.add(self.paddle)

        # Center a filled ball in the graphical window.
        ball_x = window_width / 2 - ball_radius
        ball_y = window_height / 2 - ball_radius
        self.ball = GOval(width=2*ball_radius, height=2*ball_radius, x=ball_x, y=ball_y)
        self.ball.filled = True
        self.window.add(self.ball)

        # Default initial velocity for the ball.
        self.vx = 0
        self.vy = 0

        # Initialize our mouse listeners.
        onmouseclicked(self.handle_click)
        onmousemoved(self.handle_move)

        # Draw bricks.
        brick_y = brick_offset
        for n in range(brick_rows):
            if n > 9:
                c = n - 10 * (n // 10)
            else:
                c = n
            color = COLORS[c // 2]
            brick_x = 0
            for i in range(brick_cols):
                self.brick = GRect(width=brick_width, height=brick_height, x=brick_x, y=brick_y)
                self.brick.filled = True
                self.brick.fill_color = color
                self.window.add(self.brick)
                brick_x += brick_width + brick_spacing
            brick_y += brick_height + brick_spacing

            # Brick Counter
            self.counter = brick_cols * brick_rows

    def handle_click(self, event):
        """
        Starts the game if the user clicks their mouse.
        """
        if self.vx == 0 and self.vy == 0:
            self.set_ball_velocity()

    def set_ball_velocity(self):
        """
        Set's the ball's new velocity upon being called on.
        """
        self.vx = random.uniform(-MAX_X_SPEED, MAX_X_SPEED)
        self.vy = INITIAL_Y_SPEED

    def handle_move(self, event):
        """
        Moves the paddle based on the center of the user's mouse (Will NOT
        move outside the window).
        """
        self.window.remove(self.paddle)
        if event.x - PADDLE_WIDTH / 2 <= 0:
            paddle_x = 0
        elif event.x + PADDLE_WIDTH / 2 > self.window.width:
            paddle_x = self.window.width - PADDLE_WIDTH
        else:
            paddle_x = event.x - PADDLE_WIDTH / 2
        self.paddle = GRect(width=PADDLE_WIDTH, height=PADDLE_HEIGHT, x=paddle_x, y=self.paddle_y)
        self.paddle.filled = True
        self.window.add(self.paddle)

    def handle_wall_collisions(self):
        """
        Change's the ball's velocity according to which window
        boundary it hit (not including the bottom side).
        """
        # Second Boolean needed to prevent ball sticking to right/left wall after rapid bouncing on side bricks
        if (self.ball.x <= 0 and self.vx < 0) or (self.ball.x >= self.window.width - self.ball.width and self.vx > 0):
            self.vx = -self.vx
        # Second Boolean needed to prevent ball sticking to top wall after rapid bouncing on top bricks
        elif self.ball.y <= 0 and self.vy < 0:
            self.vy = -self.vy

    def move_ball(self):
        """
        Moves the ball at the set velocity.
        """
        self.ball.move(self.vx, self.vy)

    def object_collision(self):
        """
        Returns the statement that confirms or denies an object's
        presence at the ball's boundaries at any point in the
        ball's movement.
        """
        n = 0
        x = self.ball.x
        y = self.ball.y
        while n != 4:
            obj = self.window.get_object_at(x, y)
            if obj is not None:
                return obj
            n += 1
            if n == 1:
                x += BALL_RADIUS * 2
            elif n == 2:
                y += BALL_RADIUS * 2
            elif n == 3:
                x -= BALL_RADIUS * 2

    def handle_object_collision(self):
        """
        Uses the statement given by object_collision() to
        bounce the ball off of a given object (and break a
        brick if needed).
        """
        obj = self.object_collision()
        if obj is None:
            pass
        elif obj is self.paddle:
            if self.vy > 0:
                self.bounce_ball()
        else:
            self.bounce_ball()
            self.window.remove(obj)
            self.counter -= 1

    def bounce_ball(self):
        """
        Helper function that causes a ball to bounce off of
        a given object.
        """
        self.vy = -self.vy

    def ball_out_of_screen(self):
        """
        Returns a boolean that allows the program to work
        with the scenario that the ball moved outside the
        window (through the bottom of the window).
        """
        out_of_screen = self.ball.y >= self.window.height
        return out_of_screen

    def reset_ball(self):
        """
        Reset's the ball (and the velocity) back to its original
        position, allowing the user to manually start the ball's
        movement once more.
        """
        ball_x = self.window.width / 2 - BALL_RADIUS
        ball_y = self.window.height / 2 - BALL_RADIUS
        self.ball = GOval(width=2 * BALL_RADIUS, height=2 * BALL_RADIUS, x=ball_x, y=ball_y)
        self.ball.filled = True
        self.window.add(self.ball)
        self.vx = 0
        self.vy = 0

    def lose(self):
        """
        Shows the user that they have lost the game, signifying a break
        in the program (break not actually done by this function).
        """
        display = GLabel('YOU LOSE. GAME OVER!')
        display_x = self.window.width / 2 - display.width / 2
        display_y = self.window.height / 2 + display.height / 2
        self.window.add(display, display_x, display_y)

    def win(self):
        """
        Shows the user that they have won the game, signifying a break
        in the program (break not actually done by this function).
        """
        self.window.remove(self.ball)
        display = GLabel('YOU WIN. CONGRATULATIONS!')
        display_x = self.window.width / 2 - display.width / 2
        display_y = self.window.height / 2 + display.height / 2
        self.window.add(display, display_x, display_y)

    def no_more_blocks(self):
        """
        Boolean to allow the program to complete an action in the
        scenario that the number of blocks == 0.
        """
        return self.counter == 0
