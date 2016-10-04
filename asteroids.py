__author__ = 'frycek'
# program template for Spaceship
try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
turn_speed = 10
friction = 0.985
acceleration = 0.07
started = False


class ImageInfo:
    def __init__(self, center, size, radius=0, lifespan=None, animated=False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

# art assets created by Kim Lathrop, may be freely re-used
# in non-commercial projects, please credit Kim


debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/"
                                    "codeskulptor-assets/lathrop/"
                                    "debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/"
                                    "codeskulptor-assets/lathrop/"
                                    "nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300],)
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/"
                                    "codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35,)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/"
                                  "codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5, 5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/"
                                     "codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/"
                                      "codeskulptor-assets/lathrop/"
                                      "asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png,
#                      explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage."
                                       "googleapis.com/codeskulptor-assets/"
                                       "lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/"
                                  "codeskulptor-assets/sounddogs/"
                                  "soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/"
                                     "codeskulptor-assets/sounddogs/"
                                     "missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage."
                                         "googleapis.com/codeskulptor-assets/"
                                         "sounddogs/thrust.mp3")
# ship_thrust_sound.set_volume(.5)
explosion_sound = simplegui.load_sound("http://commondatastorage."
                                       "googleapis.comm/codeskulptor-assets/"
                                       "sounddogs/explosion.mp3")


# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]


def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)


def process_sprite_group(sets, canvas):
    temp_set = set([])
    for sprite in list(sets):
        if sprite.update():
            temp_set.add(sprite)
        else:
            sprite.draw(canvas)
            sprite.update()
    sets.difference_update(temp_set)


def group_collide(group, other_object):
    temp_set = set([])
    for sprite in group:
        if sprite.collide(other_object):
            temp_set.add(sprite)
    if temp_set:
        group.difference_update(temp_set)
        return True
    else:
        return False


def group_group_collide(group, other_group):
    num = 0
    temp_set = set([])
    for sprite in group:
        if group_collide(other_group, sprite):
            num += 1
            temp_set.add(sprite)
    if temp_set:
        group.difference_update(temp_set)
    return num


# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0.0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = 35  # info.get_radius()
        self.acc = [0.0, 0.0]

    def draw(self, canvas):
        # canvas.draw_circle(self.pos, self.radius, 1, "White", "White")
        if self.thrust:
            canvas.draw_image(self.image, [135, 45], self.image_size,
                              self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                              self.pos, self.image_size, self.angle)

    def update(self):
        if self.pos[0] < 0:
            self.pos[0] = WIDTH
        elif self.pos[0] > WIDTH:
            self.pos[0] = 0

        if self.pos[1] < 0:
            self.pos[1] = HEIGHT
        elif self.pos[1] > HEIGHT:
            self.pos[1] = 0

        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.angle += self.angle_vel

        if self.thrust:
            my_ship.acc = angle_to_vector(my_ship.angle)
        else:
            my_ship.acc[0] = 0
            my_ship.acc[1] = 0

        my_ship.vel[0] = (my_ship.vel[0] + (self.acc[0] * acceleration)) * \
            friction  # acceleration + friction
        my_ship.vel[1] = (my_ship.vel[1] + (self.acc[1] * acceleration)) * \
            friction  # acceleration + friction

    def turn(self, direction):
        self.angle_vel = direction * 0.01

    def thrust_update(self, on_off):
        if on_off:
            self.thrust = True
            ship_thrust_sound.play()
        else:
            self.thrust = False
            ship_thrust_sound.rewind()

    def missile(self):
        # global a_missile
        missile_pos = [self.pos[0] + angle_to_vector(my_ship.angle)[0] * 45,
                       self.pos[1] + angle_to_vector(my_ship.angle)[1] * 45]
        missile_vel = [self.vel[0] + angle_to_vector(my_ship.angle)[0] * 6,
                       self.vel[1] + angle_to_vector(my_ship.angle)[1] * 6]

        missile_group.add(Sprite(missile_pos, missile_vel, 0, 0, missile_image,
                          missile_info, missile_sound))

        missile_sound.play()

    def get_position(self):
        return self.pos

    def get_radius(self):
        return self.radius


# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound=None):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()

    def draw(self, canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size,
                          self.pos, self.image_size, self.angle)

    def update(self):
        if self.pos[0] < 0:
            self.pos[0] = WIDTH
        elif self.pos[0] > WIDTH:
            self.pos[0] = 0

        if self.pos[1] < 0:
            self.pos[1] = HEIGHT
        elif self.pos[1] > HEIGHT:
            self.pos[1] = 0

        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.angle += self.angle_vel
        self.age += 1
        if self.age >= self.lifespan:
            return True
        elif self.age < self.lifespan:
            return False

    def collide(self, other_object):
        if dist(self.get_position(), other_object.get_position())\
              < self.get_radius() + other_object.get_radius():
            return True
        else:
            return False

    def get_position(self):
        return self.pos

    def get_radius(self):
        return self.radius


def draw(canvas):
    global time, score, lives, started, rock_group

    # animate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(),
                      nebula_info.get_size(),
                      [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size,
                      (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size,
                      (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    if group_collide(rock_group, my_ship):
        lives -= 1
        if lives <= 0:
            started = False
            rock_group = set([])

    canvas.draw_text("SCORES: " + str(score), [580, 50], 30, "White", "serif")
    canvas.draw_text("LIVES: " + str(lives), [50, 50], 30, "White", "serif")

    # draw ship and sprites
    my_ship.draw(canvas)
    my_ship.update()
    process_sprite_group(rock_group, canvas)
    process_sprite_group(missile_group, canvas)

    score += group_group_collide(missile_group, rock_group)

    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(),
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2],
                          splash_info.get_size())


# timer handler that spawns a rock
def rock_spawner():
    # global rock_group
    if len(rock_group) < 12 and started:
        rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
        rock_vel = [random.randrange(-10, 10)/10.0,
                    random.randrange(-10, 10)/10.0]
        rock_spin = random.randrange(-40, 40) / 1000.0
        if dist(rock_pos, my_ship.get_position()) > 100:
            rock_group.add(Sprite(rock_pos, rock_vel, 0, rock_spin,
                           asteroid_image, asteroid_info))


# key handler
def key_down(key):
    if key == simplegui.KEY_MAP['space']:
        my_ship.missile()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.thrust_update(1)        # thrust ON
    elif key == simplegui.KEY_MAP['right']:
        my_ship.turn(turn_speed)
    elif key == simplegui.KEY_MAP['left']:
        my_ship.turn(-turn_speed)


def key_up(key):
    if key == simplegui.KEY_MAP['space']:
        pass
    elif key == simplegui.KEY_MAP['up']:
        my_ship.thrust_update(0)        # thrust OFF
    elif key == simplegui.KEY_MAP['right']:
        my_ship.turn(0)
    elif key == simplegui.KEY_MAP['left']:
        my_ship.turn(0)


# mouse handler
def click(pos):
    global started, score, lives
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        lives = 3
        score = 0
        soundtrack.rewind()
        soundtrack.play()


# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 4.7, ship_image, ship_info)

rock_group = set([])
# a_rock = Sprite([WIDTH / 3, HEIGHT / 3], [1, 1], 0, 0.01,
#                asteroid_image, asteroid_info)
missile_group = set([])
# a_missile = Sprite([2 * WIDTH / 3, 2 * HEIGHT / 3], [-3, 1], 0, 0,
#                   missile_image, missile_info, missile_sound)

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(key_down)
frame.set_keyup_handler(key_up)
frame.set_mouseclick_handler(click)
timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()
