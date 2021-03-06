import random
import arcade
import math
import time

from arcade.geometry import check_for_collision

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600
BALL_RADIUS = 20
SPRITE_SCALE = 1.0

class MyApplication(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """


    def __init__(self, width, height):
        super().__init__(width, height)

        self.ball_x_position = BALL_RADIUS
        self.ball_y_position = SCREEN_HEIGHT // 2
        self.ball_x_pixels_per_second = 70
        self.ball_velocity_x = random.uniform(0.5, 2.0)
        self.ball_velocity_y = random.choice([-2, 2])
        self.last_key = None
        self.contact_counter = 0
        self.paddle_ball_dif = 0.0
        self.rocket_count = 0
        self.invis_count = 0
        self.lightning_count = 0
        self.rocket_activate = False
        self.last_item = None
        self.board_speed_player = 2
        self.board_speed_computer = 2

        self.invis_timer = 0
        self.invis_activated = False
        self.invis_count = 0

        self.computer_score = 0
        self.player_score = 0

        self.all_sprites_list = None
        self.rocket_sprites_list = None
        self.item_sprites_list = None
        self.player_sprite = None
        self.computer_sprite = None

        arcade.set_background_color(arcade.color.WHITE)

    def resetGame(self):
        self.ball_sprite.center_x = SCREEN_WIDTH / 2
        self.ball_sprite.center_y = SCREEN_HEIGHT / 2
        self.ball_velocity_y = random.choice([-2, 2])
        self.ball_velocity_x = random.uniform(-2.0, 2.0)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.computer_sprite.center_x = SCREEN_WIDTH / 2


    def setup(self):

        #Sprite Lists
        self.all_sprites_list = arcade.SpriteList()
        self.rocket_sprites_list = arcade.SpriteList()
        self.item_sprites_list = arcade.SpriteList()

        #setup player
        self.player_sprite = arcade.Sprite("player.png", SPRITE_SCALE)
        self.computer_sprite = arcade.Sprite("enemy.png", SPRITE_SCALE)
        self.ball_sprite = arcade.Sprite("ball.png", SPRITE_SCALE)
        self.rocket = arcade.Sprite("onlyrocket.png", SPRITE_SCALE)

        self.player_sprite.center_y = 50
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.computer_sprite.center_x = SCREEN_WIDTH / 2
        self.computer_sprite.center_y = SCREEN_HEIGHT - 50
        self.ball_sprite.center_x = SCREEN_WIDTH / 2
        self.ball_sprite.center_y = SCREEN_HEIGHT / 2

        self.all_sprites_list.append(self.player_sprite)
        self.all_sprites_list.append(self.computer_sprite)

        self.start_time = time.time()
        self.current_time = None

    def rocketGen(self, x, y):

       rocket = arcade.Sprite("onlyrocket.png", SPRITE_SCALE)
       rocket.center_x = x
       rocket.center_y = y
       rocket.change_y = 5

       return rocket

    def lightningGen(self, x, y):

        lightning = arcade.Sprite("lightning.png", SPRITE_SCALE)
        lightning.center_x = x
        lightning.center_y = y

        return lightning

    def invisGen(self, x, y):

        invis = arcade.Sprite("invis.jpg", SPRITE_SCALE)
        invis.center_x = x
        invis.center_y = y

        return invis

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        #draw Sprites
        self.all_sprites_list.draw()
        self.rocket_sprites_list.draw()
        self.item_sprites_list.draw()
        if self.invis_activated is False:
            self.ball_sprite.draw()

        #draw Text

        arcade.draw_text("Computer Score: " + str(self.computer_score), 10, SCREEN_HEIGHT - 30, arcade.color.BLACK, 12)
        arcade.draw_text("Player Score: " + str(self.player_score), 10, 10, arcade.color.BLACK, 12)


    def animate(self, delta_time):

        #check timed events
        self.item_time_diff = time.time() - self.start_time
        self.invis_time_diff = time.time() - self.invis_timer

        if self.invis_time_diff > 1:
            self.invis_activated = False
            self.invis_timer = 0

        #gen items

        if self.item_time_diff > 10:

            tmp_coordinates = (self.player_sprite.get_points())

            item_choice = random.choice(['rocket', 'lightning', 'invis'])
            self.last_item = item_choice

            x = random.randint(0, self.player_sprite.center_x - self.player_sprite.width / 2 - 20) \
                    if tmp_coordinates[0][0] >= 25 else tmp_coordinates[1][0] + random.randint(50, 2200)

            y = random.randint(self.player_sprite.center_x + self.player_sprite.width / 2 + 20, SCREEN_WIDTH) \
                    if tmp_coordinates[1][0] <= SCREEN_WIDTH - 25 else tmp_coordinates[0][0] - random.randint(50, 200)

            item_dict = {
                'rocket': self.rocketGen(random.choice([x, y]), 50),
                'lightning': self.lightningGen(random.choice([x, y]), 50),
                'invis': self.invisGen(random.choice([x, y]), 50)
            }

            self.item_sprites_list.append(item_dict[item_choice])

            self.item_time_diff = 0
            self.start_time = time.time()

        #computer logic
        if self.ball_sprite.center_x > self.computer_sprite.center_x and \
                self.computer_sprite.center_x + self.computer_sprite.width / 2 < SCREEN_WIDTH:
            self.computer_sprite.center_x += self.board_speed_computer

        elif self.ball_sprite.center_x < self.computer_sprite.center_x and self.computer_sprite.center_x \
                - self.computer_sprite.width / 2 > 0:
            self.computer_sprite.center_x -= self.board_speed_computer

        #move player
        if self.last_key == 'LEFT' and self.player_sprite.center_x - self.player_sprite.width / 2 > 0:
            self.player_sprite.center_x -= self.board_speed_player

        elif self.last_key == 'RIGHT' and self.player_sprite.center_x + self.player_sprite.width / 2 <= SCREEN_WIDTH:
            self.player_sprite.center_x += self.board_speed_player

        self.ball_sprite.center_x += self.ball_velocity_x
        self.ball_sprite.center_y += self.ball_velocity_y

        #check collision

        if check_for_collision(self.ball_sprite, self.player_sprite) or check_for_collision(self.ball_sprite, self.computer_sprite):
            self.contact_counter += 1
            self.paddle_ball_dif = math.fabs(self.ball_sprite.center_x - self.player_sprite.center_x) if self.ball_sprite.center_y < SCREEN_WIDTH /2 \
            else math.fabs(self.ball_sprite.center_x - self.computer_sprite.center_x)
            self.ball_velocity_y *= -1

            if self.ball_velocity_x > 0:
                self.ball_velocity_x = (self.paddle_ball_dif * 0.0133333 + 0.75) * math.fabs(self.ball_velocity_y)
            else:
                self.ball_velocity_x = (self.paddle_ball_dif * 0.0133333 + 0.75) * math.fabs(self.ball_velocity_y) * -1

        #check itemPickup

        collision_list =  arcade.geometry.check_for_collision_with_list(self.player_sprite, self.item_sprites_list)
        for item in collision_list:
            self.item_sprites_list.remove(item)
            if self.last_item == 'rocket':
                self.rocket_count += 1
            elif self.last_item == 'lightning':
                self.lightning_count += 1
            elif self.last_item == 'invis':
                self.invis_count += 1


        #check screenborders
        if self.ball_sprite.center_x <= 0 or self.ball_sprite.center_x >= SCREEN_WIDTH:
            self.ball_velocity_x *= -1

        if self.contact_counter >= 2:
            self.ball_velocity_y += 0.5 if self.ball_velocity_y > 0 else -0.5

            self.contact_counter = 0
        #check if game over
        if self.ball_sprite.center_y < 0:
            self.computer_score+= 1
            self.resetGame()


        elif self.ball_sprite.center_y > SCREEN_HEIGHT:
            self.player_score += 1
            self.resetGame()

        #check item usage

        if self.rocket_activate is True and self.rocket_count > 0:
            self.rocketGen(self.player_sprite.center_x, self.player_sprite.center_y)
            self.rocket_activate = False
            self.rocket_sprites_list.append(self.rocketGen(self.player_sprite.center_x, self.player_sprite.center_y))
            self.rocket_count -= 1

        self.all_sprites_list.update()

        #update item pos

        for rocket in self.rocket_sprites_list:

            rocket.center_y += rocket.change_y

            if check_for_collision(rocket, self.computer_sprite):
                tmp_x = self.computer_sprite.center_x
                tmp_y = self.computer_sprite.center_y

                self.all_sprites_list.remove(self.computer_sprite)
                self.computer_sprite = arcade.Sprite("enemy_short.png", SPRITE_SCALE)
                self.all_sprites_list.append(self.computer_sprite)

                self.computer_sprite.center_x = tmp_x
                self.computer_sprite.center_y = tmp_y

                self.rocket_sprites_list.remove(rocket)

    def on_key_press(self, key, key_modifiers):

        if key == arcade.key.LEFT:
            self.last_key = 'LEFT'
        elif key == arcade.key.RIGHT:
            self.last_key = 'RIGHT'

        if key == arcade.key.SPACE:
            if  self.rocket_count > 0:
                self.rocket_activate = True
            elif self.invis_count > 0:
                self.invis_activated = True
                self.invis_timer = time.time()
                self.invis_count -= 1


window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)
window.setup()

arcade.run()
