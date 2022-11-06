"""
Stanford CS106AP Breakout Project
Adapted from Eric Roberts's Breakout by
Sonja Johnson-Yu, Kylie Jue, and Nick Bowman.

This program utilizes the BreakoutGraphics class to
create a game reminiscent of 'Breakout'. The game has
the user control the paddle with their mouse, hitting a ball
between the paddle and a series of blocks to be broken by
the bouncing ball. If all the blocks are cleared, the user has
won. If the user misses the ball with their paddle and the ball
falls through the bottom of the window, however, the user has
lost a life, losing the game if 3 lives are lost.
"""
from campy.gui.events.timer import pause
from breakoutgraphics import BreakoutGraphics

FRAME_RATE = 1000 / 120  # 120 frames per second.
NUM_LIVES = 3


def main():
    graphics = BreakoutGraphics()
    lives = NUM_LIVES

    # Add animation loop here!
    while True:

        # Display's a win to the user if all blocks have been
        if graphics.no_more_blocks():
            graphics.win()
            break

        # Resets the ball at the cost of one life or display's a loss if all lives are lost
        if graphics.ball_out_of_screen():
            lives -= 1
            if lives > 0:
                graphics.reset_ball()
            else:
                graphics.lose()
                break

        graphics.move_ball()
        graphics.handle_wall_collisions()
        graphics.handle_object_collision()

        pause(FRAME_RATE)


if __name__ == '__main__':
    main()
