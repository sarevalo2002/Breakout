"""
Stanford CS106AP Breakout Project
Adapted from Eric Roberts's Breakout by
Sonja Johnson-Yu, Kylie Jue, and Nick Bowman.

This program describes a class that sets up and operates
a game reminiscent of 'Breakout'. Utilizing user input,
the game starts with a click and follows a ball that bounces
of blocks and a paddle controlled by the user's mouse.

EXTENSION: Greater Control
- This extension gives the user greater control on the movement
of the ball, allowing them to use the far sides/corners of the
paddle to allow the ball to bounce back the direction it came
from (NOTICE the ball will not bounce back the direction it
came if it's hit anywhere on the same edge of the paddle it's
coming from; the ball must hit the corner or far vertical/
horizontal edges of the paddle to better connect the path of
the ball to real world physics).

- This extension also edited the velocities so that the game
never has a velocity close to 0.

- This extension also gives the user the ability to move the
paddle quickly to cause the ball to move faster, similar to
a baseball bat hitting a ball (signified with a red ball),
allowing the user to score even more points (This "batted"
effect can NOT occur while the ball is in a "batted" state,
meaning the effect does not stack, so the user can only bat
a ball while the ball is its normal black color).


EXTENSION: Improved Interface Display
- This extension allows the user to easily see their lives as
well as adds a score to keep the player pushing to do better
in the game to score higher.

- This extension also introduces an intro message
to inform the user of the rules and goal of the game,
before signalling them to simply click to begin.


EXTENSION: The Kicker
-This extension adds some intensity to the game, as when the
user destroys various amounts of bricks within a single life,
the ball moves faster and faster. If the user is doing really
well, they'll have to face the "killer kicker", causing the
ball to move extremely fast but also doubling the points
given by any color brick.
"""
from campy.graphics.gwindow import GWindow
from campy.graphics.gobjects import GOval, GRect, GLabel
from campy.gui.events.mouse import onmouseclicked, onmousemoved
import random
import time

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
        paddle_y = window_height - paddle_offset
        self.paddle = GRect(width=paddle_width, height=paddle_height, x=paddle_x, y=paddle_y)
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

        # EXTENSION (Greater Control)
        self.left_point = 0
        self.right_point = 0

        self.elapsed_time = 0
        self.total_distance = 0
        self.bounce_counter = 0

        # EXTENSION (Improved Interface Display)
        self.intro_number = 1
        self.intro = GLabel("Welcome to Breakout! You have 3 lives, and the higher" +
                            "\nthe color of the brick, the more points it's worth. If" +
                            "\nyou can break enough bricks in one life the bricks' point" +
                            "\nvalue will double, at a cost...Click anywhere to begin!")
        self.window.add(self.intro, self.window.width / 2 - self.intro.width / 8, self.window.height * 0.7)

        self.score = 0

        self.score_display = GLabel('SCORE: ' + str(self.score))
        self.score_x = window_width - self.score_display.width - 1
        self.score_y = window_height - 1
        self.window.add(self.score_display, self.score_x, self.score_y)

        self.lives = GLabel('LIVES:')
        lives_x = 1
        lives_y = window_height - 1
        self.window.add(self.lives, lives_x, lives_y)

        self.life_counter = 3
        self.life_x = self.lives.width + ball_radius
        self.life_y = window_height - 2 * ball_radius - 1

        self.life_1 = GOval(width=2*ball_radius, height=2*ball_radius)
        self.life_2 = GOval(width=2 * ball_radius, height=2 * ball_radius)
        self.life_3 = GOval(width=2 * ball_radius, height=2 * ball_radius)
        self.life_1.filled = self.life_2.filled = self.life_3.filled = True
        self.life_1.fill_color = self.life_2.fill_color = self.life_3.fill_color = 'green'

        self.window.add(self.life_1, self.life_x, self.life_y)
        self.life_x += ball_radius * 2 + BRICK_SPACING

        self.window.add(self.life_2, self.life_x, self.life_y)
        self.life_x += ball_radius * 2 + BRICK_SPACING

        self.window.add(self.life_3, self.life_x, self.life_y)

        # EXTENSION (The Kicker)
        self.kicker_counter = 0

    def handle_click(self, event):
        """
        Starts the game if the user clicks their mouse.

        EXTENSION HERE (Improved Interface Display).
        The intro message will be deleted when the user
        starts the game.
        """
        if self.vx == 0 and self.vy == 0:
            self.set_ball_velocity()
            if self.intro_number == 1:
                self.intro_number -= 1
                self.window.remove(self.intro)

    def set_ball_velocity(self):
        """
        Set's the ball's new velocity upon being called on.

        EXTENSION HERE (Greater Control).
        Some values have been changed to better the game so that
        it doesn't become boring with a velocity close to 0.
        """
        x_speed = [random.uniform(-MAX_X_SPEED, -1), random.uniform(1, MAX_X_SPEED)]
        self.vx = random.choice(x_speed)
        self.vy = INITIAL_Y_SPEED

    def handle_move(self, event):
        """
        Moves the paddle based on the center of the user's mouse (Will NOT
        move outside the window).

        EXTENSION HERE (Greater Control).
        The time and distance between movements is
        recorded for every change in the cursor's position.
        """
        start_time = time.time()
        distance = self.paddle.x
        if event.x - PADDLE_WIDTH / 2 < 0:
            self.paddle.x = 0
        elif event.x + PADDLE_WIDTH / 2 > self.window.width:
            self.paddle.x = self.window.width - PADDLE_WIDTH
        else:
            self.paddle.x = event.x - PADDLE_WIDTH / 2
        end_distance = self.paddle.x
        end_time = time.time()
        self.elapsed_time = abs(start_time - end_time)
        self.total_distance = abs(end_distance - distance)

    def handle_wall_collisions(self):
        """
        Change's the ball's velocity according to which window
        boundary it hit (not including the bottom side).

        EXTENSION HERE (Greater Control).
        The bounce counter decreases by 1 every time the ball
        bounces off a wall.
        """
        # Second Boolean needed to prevent ball sticking to right/left wall after rapid bouncing on side bricks
        if (self.ball.x <= 0 and self.vx < 0) or (self.ball.x >= self.window.width - self.ball.width and self.vx > 0):
            self.vx = -self.vx
            self.check_batting_score()
        # Second Boolean needed to prevent ball sticking to top wall after rapid bouncing on top bricks
        elif self.ball.y <= 0 and self.vy < 0:
            self.vy = -self.vy
            self.check_batting_score()

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

        EXTENSION HERE (Greater Control).
        If the object returns far sides of a paddle, the ball
        changes both x and y velocities.

        Due to the method in which finding an object is inspected,
        the length of left_point must be smaller than the length of
        right_point.

        If the player moves the paddle quick enough in one direction,
        the ball will turn red and move faster for a few bounces,
        allowing the player to create a "batting" like method to
        control the ball and earn more points because of it.

        EXTENSION HERE (Improved Interface Display).
        In order to not have the ball remove the lives and score,
        anything under the paddle will be treated as if the
        inspected coordinates came up as None.

        The score calculator has been added here to add points
        whenever a ball breaks a brick of a certain color.

        EXTENSION HERE (The Kicker).
        Every time a brick is broken, the kicker_activator
        is called, and activates the kicker at 7, 14, and 50
        bricks broken (within one life).
        """
        left_point = self.paddle.x + BALL_RADIUS / 4
        right_point = self.paddle.x + PADDLE_WIDTH - BALL_RADIUS * 2
        obj = self.object_collision()
        if obj is None or obj.y >= self.window.height - PADDLE_OFFSET + PADDLE_HEIGHT + 10:
            pass
        elif obj is self.paddle:
            if self.vy > 0:
                self.batting_paddle()
                if self.ball.x < left_point and self.vx > 0:
                    self.bounce_ball()
                    self.vx = -self.vx
                elif self.ball.x > right_point and self.vx < 0:
                    self.bounce_ball()
                    self.vx = -self.vx
                else:
                    self.bounce_ball()
                    self.check_batting_score()
        else:
            self.bounce_ball()
            self.window.remove(obj)
            self.counter -= 1
            self.score_calculator(obj.y)
            self.add_in_score()
            self.kicker_activator()
            self.check_batting_score()

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

        EXTENSION HERE (The Kicker).
        The kicker counter will reset upon the ball's reset.
        """
        ball_x = self.window.width / 2 - BALL_RADIUS
        ball_y = self.window.height / 2 - BALL_RADIUS
        self.ball = GOval(width=2 * BALL_RADIUS, height=2 * BALL_RADIUS, x=ball_x, y=ball_y)
        self.ball.filled = True
        self.window.add(self.ball)
        self.vx = 0
        self.vy = 0
        self.kicker_counter = 0
        self.bounce_counter = 0

    def lose(self):
        """
        Shows the user that they have lost the game, signifying a break
        in the program (break not actually done by this function).
        """
        display = GLabel('YOU LOSE. GAME OVER!')
        display_x = self.window.width / 2 - display.width / 2
        display_y = self.window.height / 2 + display.height / 2
        self.window.add(display, display_x, display_y)
        self.window.remove(self.score_display)
        real_score = GLabel('Your Final Score is: ' + str(self.score))
        display_x = self.window.width / 2 - real_score.width / 2
        display_y += display.height + 5
        self.window.add(real_score, display_x, display_y)

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
        self.window.remove(self.score_display)
        real_score = GLabel('Your Final Score is: ' + str(self.score))
        display_x = self.window.width / 2 - real_score.width / 2
        display_y += display.height + 5
        self.window.add(real_score, display_x, display_y)

    def no_more_blocks(self):
        """
        Boolean to allow the program to complete an action in the
        scenario that the number of blocks == 0.
        """
        return self.counter == 0

    def display_lives(self):
        """
        EXTENSION HERE (Improved Interface Display).
        Reduces the number of lives shown to the user
        while changing the color scheme of the lives.
        """
        self.life_counter -= 1
        if self.life_counter == 2:
            self.window.remove(self.life_3)
            self.life_2.fill_color = self.life_1.fill_color = 'yellow'
        if self.life_counter == 1:
            self.window.remove(self.life_2)
            self.life_1.fill_color = 'red'
        if self.life_counter == 0:
            self.window.remove(self.life_1)

    def add_in_score(self):
        """
        EXTENSION HERE (Improved Interface Display).
        Updates the score based upon the block that was
        hit.
        """
        self.window.remove(self.score_display)
        self.score_display = GLabel('SCORE: ' + str(self.score))
        self.score_x = self.window.width - self.score_display.width - 1
        self.window.add(self.score_display, self.score_x, self.score_y)

    def score_calculator(self, y_level):
        """
        EXTENSION HERE (Improved Interface Display).
        Calculates the needed points to be added to the
        score depending on the y coordinate of the brick
        due to its relation to the color of the brick.
        """
        red = 16
        orange = 8
        yellow = 4
        green = 2
        blue = 1
        score_spacing = 2 * BRICK_HEIGHT + BRICK_SPACING * 2
        if y_level < PADDLE_OFFSET + score_spacing:
            self.color_calculator(red)
        elif y_level < PADDLE_OFFSET + score_spacing * 2:
            self.color_calculator(orange)
        elif y_level < PADDLE_OFFSET + score_spacing * 3:
            self.color_calculator(yellow)
        elif y_level < PADDLE_OFFSET + score_spacing * 4:
            self.color_calculator(green)
        elif y_level < PADDLE_OFFSET + score_spacing * 5:
            self.color_calculator(blue)

    def color_calculator(self, color):
        """
        EXTENSION HERE (Greater Control).
        The point value for each brick will double
        while the ball has been "batted".

        EXTENSION HERE (Improved Interface Display).
        Calculates the needed points to be added to the
        score depending on the color of the brick.

        EXTENSION HERE (The Kicker).
        Once the kicker_counter passes 50, each brick
        will have double its original point value for
        the duration of that life.
        """
        self.score += color
        # Used 2 if statements to allow combined "batted" & "killer kicker" ball to score 3x as many points
        if self.kicker_counter > 50:
            self.score += color
        if self.bounce_counter > 0:
            self.score += color

    def kicker_activator(self):
        """
        EXTENSION HERE (The Kicker).
        Activates the normal kicker when the kicker_counter
        reaches 7, the hard kicker at 14, and the killer
        kicker at 50.
        """
        self.kicker_counter += 1
        if self.kicker_counter == 7:
            self.vx *= 2
        elif self.kicker_counter == 14:
            self.vy *= 1.5
        elif self.kicker_counter == 50:
            self.vx *= 2
            self.vy *= 1.75

    def batting_paddle(self):
        """
        EXTENSION HERE (Greater Control).
        Sets the changes and the condition for the ball
        to turn red and move quicker when it's hit by
        the paddle rapidly (Can only occur if the ball
        is not in a "batted" state).
        """
        if self.total_distance / self.elapsed_time > 15000 and self.bounce_counter == 0:
            self.ball.fill_color = 'red'
            self.vx *= 1.5
            self.vy *= 1.25
            self.bounce_counter = 10

    def check_batting_score(self):
        """
        EXTENSION HERE (Greater Control).
        Checks the batting score for every bounce and
        resets the ball to its previous state if it
        has bounced enough times without being hit by
        the paddle.
        """
        if self.bounce_counter > 0:
            self.bounce_counter -= 1
            if self.bounce_counter == 0:
                self.ball.fill_color = 'black'
                self.vx /= 1.5
                self.vy /= 1.25
