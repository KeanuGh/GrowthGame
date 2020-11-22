import pygame
import sys
import os
import random as rand
import colorsys
from typing import Tuple
from math import floor, hypot, sin, cos, pi

# VARIABLES
# =============================
SIZE = width, height = 640, 480

white = 255, 255, 255
black = 0, 0, 0

FPS = 60  # frame rate cap
SATURATED = False  # 'game over'
SPAWNRATE = 150  # ms between particles spawning
LOOPNUM = 300  # number of particles to collide until colours loop round
MESSAGECHANCE = 300  # growth number to reach for 100% chance of a nice message

main = True


# DATA
# =============================
kind_words = [
    'GROWTH IS BEAUTIFUL',
    'YOU ARE ALIVE',
    'BE NOT AFRAID',
    'ALL IS WELL',
    'NATURE IS BEAUTIFUL',
    'THIS TOO SHALL PASS',
    'THIS IS THE CYCLE',
    'BREATH OUT',
    'SUCCESS TAKES TIME',
]


# FUNCTIONS
# =============================
def dist(a, b):
    """Gets distance between centers of two rects"""
    return hypot(a.rect.centerx - b.rect.centerx, a.rect.centery - b.rect.centery)


def touching_edge(shape: pygame.Rect) -> bool:
    """Is a block touching an edge"""
    if shape.x < 0 or shape.x > width:
        return True
    if shape.y < 0 or shape.y > height:
        return True
    else:
        return False


def rangedcolourpicker(i: int, sv=(0.6, 0.6)):
    """Return an RGB colour from range"""
    c = tuple([floor(i * 255) for i in colorsys.hsv_to_rgb(i / LOOPNUM % LOOPNUM, *sv)])
    check_colour_range(c)
    return c


def check_colour_range(col: tuple):
    """Makes sure colour range is correct"""
    for c in col:
        if c < 0 or c > 255:
            raise ValueError(f"Invalid colour {col}")


# OBJECTS
# =============================
class Particle(pygame.sprite.Sprite):
    def __init__(self,
                 edge_len: int = 10,
                 colour: Tuple[int, int, int] = white,
                 speed_mult: float = 1.5):
        super().__init__()

        self.speed = speed_mult * 3
        self.size = (edge_len, edge_len)
        self.colour = colour

        self.image = pygame.Surface(self.size)
        self.image.fill(self.colour)

        self.rect = self.image.get_rect()

        # movement
        self.movex = 0  # move along X
        self.movey = 0  # move along Y

    def move(self, x, y):
        """move self"""
        self.movex += self.speed * x
        self.movey += self.speed * y

    def update(self):
        raise NotImplementedError


class You(Particle):
    def __init__(self):
        super().__init__()

        # start in the middle of the screen
        self.rect.x = width // 2
        self.rect.y = height // 2

    def update(self):
        """update position"""
        # check you don't overshoot
        if self.rect.x + self.movex < 0:
            return
        if self.rect.x + self.movex > width:
            return
        if self.rect.y + self.movey < 0:
            return
        if self.rect.y + self.movey > height:
            return

        # simple move
        self.rect.x += self.movex
        self.rect.y += self.movey


class Other(Particle):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ATTATCHED = False  # whether or not the particle is attached to you
        self.num = None  # The 'attachment number'
        self.counter = 0  # counter for colour incrementing

        # colour
        self.image.fill((50, 50, 50))

        # choose an edge to spawn on
        self.rect.x, self.rect.y = (floor(rand.random() * width), floor(rand.random() * height))
        if rand.random() < .5:
            self.rect.x = 0 if self.rect.x < width // 2 else width
        else:
            self.rect.y = 0 if self.rect.y < height // 2 else height

        # choose an angle
        ang = rand.random() * 2 * pi

        # set movement towards screen
        self.movex = cos(ang) * self.speed
        if (self.rect.x + self.movex < 0) or (self.rect.x + self.movex > width):
            self.movex *= -1
        self.movey = sin(ang) * self.speed
        if (self.rect.y + self.movey < 0) or (self.rect.y + self.movey > height):
            self.movey *= -1

    def update(self):
        """update position"""
        if self.ATTATCHED:
            # move and increment colour
            self.movex = you.movex
            self.movey = you.movey
            # self.increment_colour(len(Growth) // 100)

        # What happens during a collision
        elif blocklist := self._is_collided():
            print(f"Collided! Growth of {len(Growth)}")
            # add to Growth
            self.remove(Others)
            Growth.add(self)
            self.ATTATCHED = True
            self.num = len(Growth) - 1  # player counts as 1
            self.counter = self.num  # start counter here

            self.image.fill(rangedcolourpicker(self.num))

            # make sure it snaps to edge
            # closest block
            edgeblock = min(blocklist, key=lambda x: dist(x, self))

            # is it closest to top, bottom, left or right?
            dists = [
                abs(self.rect.top - edgeblock.rect.bottom),
                abs(self.rect.bottom - edgeblock.rect.top),
                abs(self.rect.left - edgeblock.rect.right),
                abs(self.rect.right - edgeblock.rect.left)
            ]
            edge = dists.index(min(dists))
            if edge == 0:
                self.rect.top = edgeblock.rect.bottom
            elif edge == 1:
                self.rect.bottom = edgeblock.rect.top
            elif edge == 2:
                self.rect.left = edgeblock.rect.right
            elif edge == 3:
                self.rect.right = edgeblock.rect.left

            # don't adjust position when attaching or clipping will happen
            return

        else:
            # control boundary
            if touching_edge(self.rect):
                self.kill()

        # simple move
        self.rect.x += self.movex
        self.rect.y += self.movey

    def increment_colour(self, s):
        self.counter += 1
        self.image.fill(rangedcolourpicker(self.counter))

    def _is_collided(self):
        return pygame.sprite.spritecollide(self, Growth, dokill=False)


# STATES
# =============================
def regrow():
    Growth.empty()
    Others.empty()

    you.rect.x = width // 2
    you.rect.y = height // 2
    you.movex = 0
    you.movey = 0
    Growth.add(you)

    global SATURATED
    SATURATED = False


def saturated():
    # print to screen
    finaltext = satufont.render('SATURATION REACHED.', False, white)
    textrect = finaltext.get_rect()
    textrect.center = width // 2, height // 3

    scoretext = satufont.render(f'FINAL SIZE: {len(Growth)}', False, white)
    scorerect = scoretext.get_rect()
    scorerect.centerx = textrect.centerx
    scorerect.centery = textrect.centery + textrect.height

    texts = [finaltext, scoretext]
    trects = [textrect, scorerect]

    # Chance for kind words to appear as growth increases
    if rand.random() < len(Growth) / MESSAGECHANCE:
        kindtext = satufont.render(rand.choice(kind_words), False, white)
        kindrect = kindtext.get_rect()
        kindrect.centerx = textrect.centerx
        kindrect.centery = scorerect.centery + scorerect.height * 2

        texts.append(kindtext)
        trects.append(kindrect)

    while SATURATED:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    regrow()
                if event.key == ord('q') or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            screen.fill(background)
            for text, rect in zip(texts, trects):
                screen.blit(text, rect)
            pygame.display.update()
            clock.tick(FPS)


# SETUP
# =============================
pygame.init()

clock = pygame.time.Clock()

screen = pygame.display.set_mode(SIZE)

background = black
screen.fill(background)
pygame.display.set_caption('GROWTH')


# FONTS HANDLER
# ============================
# this lets pyinstaller stick the fonts in the right place
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# for saturation screen
satufont = pygame.font.Font(resource_path("data-latin.ttf"), 30)

# onscreen info
ingamefont = pygame.font.Font(resource_path("Ticketing.ttf"), 20)

# PLAYER
# =============================
you = You()
Growth = pygame.sprite.Group()
Growth.add(you)

# PARTICLES
# =============================
Others = pygame.sprite.Group()


# MAIN LOOP
# =============================
t = pygame.time.get_ticks()
while main:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            try:
                sys.exit()
            finally:
                main = False

        keys = pygame.key.get_pressed()

        # KEY PRESSES
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                you.move(-1, 0)
            if event.key == pygame.K_RIGHT:
                you.move(1, 0)
            if event.key == pygame.K_UP:
                you.move(0, -1)
            if event.key == pygame.K_DOWN:
                you.move(0, 1)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                you.move(1, 0)
            if event.key == pygame.K_RIGHT:
                you.move(-1, 0)
            if event.key == pygame.K_UP:
                you.move(0, 1)
            if event.key == pygame.K_DOWN:
                you.move(0, -1)
            if event.key == ord('q') or event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_SPACE:
                regrow()

    # HANDLE PARTICLES
    # ==================================
    # generate new particle
    if (t2 := pygame.time.get_ticks()) - t > SPAWNRATE:
        t = t2
        # random speed and size
        newsize = rand.randint(2, 10)
        newspeed = rand.uniform(1, 2)
        Others.add(Other(edge_len=newsize, speed_mult=newspeed))
        # print(f"n of Others: {len(Others)}")

    # End simulation
    for block in Growth:
        if touching_edge(block.rect):
            SATURATED = True
            saturated()

    # onscreen info
    sizetext = ingamefont.render(f'growth: {len(Growth)}', False, white)
    sizetextrect = sizetext.get_rect()
    sizetextrect.topleft = (10, 10)

    screen.fill(background)
    Growth.update()
    Others.update()

    Growth.draw(screen)
    Others.draw(screen)

    screen.blit(sizetext, sizetextrect)
    pygame.display.update()
    clock.tick(FPS)
