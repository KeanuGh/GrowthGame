import pygame
import sys
import os
import glob
import random as rand
from typing import Tuple
from math import sqrt, sin, cos, pi

# VARIABLES
# =============================
# display
SCREENSIZE = WIDTH, HEIGHT = 640, 480
white = 255, 255, 255
grey = 50, 50, 50
black = 0, 0, 0

# engine
MAIN = True
FPS = 60  # frame rate cap
SATURATED = False  # 'game over'
GROWCOUNT = 0  # global counter for number of blocks attached to you

# particle settings
SIZERANGE = 3, 10
SPEEDRANGE = 0.8, 2
SPAWNRATE = 150  # ms between particles spawning
LOOPNUM = 600  # number of particles to collide until colours loop round
MESSAGECHANCE = 600  # growth number to reach for 100% chance of a nice message
NUMPOOF = 50  # number of stars when colliding

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
    return sqrt((a.rect.centerx - b.rect.centerx) ** 2 + (a.rect.centery - b.rect.centery) ** 2)


def outofbounds(shape: pygame.Rect) -> bool:
    """Is a block is outside the screen"""
    if shape.x < 0 or \
       shape.x > WIDTH or \
       shape.y < 0 or \
       shape.y > HEIGHT:
        return True
    else:
        return False


def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Converts from HSV colour format to RGB. (colorsys code reworked)"""
    if s == 0.0:
        v = int(v * 255)
        return v, v, v
    i = int(h * 6.)
    f = (h * 6.) - i
    p, q, t = int(255 * (v * (1. - s))), int(255 * (v * (1. - s * f))), int(255 * (v * (1. - s * (1. - f))))
    v = int(v * 255)
    i %= 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q


def rangedcolourpicker(i: int, sv=(0.6, 0.6)) -> Tuple[int, int, int]:
    """Return an RGB colour from range"""
    c = hsv_to_rgb(i / LOOPNUM % LOOPNUM, *sv)
    return c


def init_poof(pos: Tuple[float, float], col: Tuple[int, int, int]):
    for i in range(NUMPOOF):
        poof = Poof(pos, colour=col)
        Poofs.add(poof)


def resource_path(relative_path):
    """
    RESOURCE HANDLER
    this lets pyinstaller stick files in the right place
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# OBJECTS
# =============================
class Particle(pygame.sprite.Sprite):
    def __init__(self,
                 edge_len: int = 10,
                 colour: Tuple[int, int, int] = white,
                 speed_mult: float = 1.5):
        super().__init__()

        self.size = (edge_len, edge_len)
        self.speed = speed_mult * 3
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

    def set_col(self):
        self.image.fill(self.colour)


class You(Particle):
    def __init__(self):
        super().__init__()

        # start in the middle of the screen
        self.rect.x = WIDTH // 2
        self.rect.y = HEIGHT // 2

    def update(self):
        """update position"""
        # check you don't overshoot
        if self.rect.x + self.movex < 0:
            return
        if self.rect.x + self.movex > WIDTH:
            return
        if self.rect.y + self.movey < 0:
            return
        if self.rect.y + self.movey > HEIGHT:
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
        self._last_block = False  # flag as to whether this is the last block in the growth

        # colour
        self.image.fill(grey)

        # choose an edge to spawn on
        self.rect.x, self.rect.y = (int(rand.random() * WIDTH), int(rand.random() * HEIGHT))
        if rand.random() < .5:
            self.rect.x = 0 if self.rect.x < WIDTH // 2 else WIDTH
        else:
            self.rect.y = 0 if self.rect.y < HEIGHT // 2 else HEIGHT

        # choose an angle
        ang = rand.random() * 2 * pi

        # set movement towards screen
        self.movex = cos(ang) * self.speed
        if (self.rect.x + self.movex < 0) or (self.rect.x + self.movex > WIDTH):
            self.movex *= -1
        self.movey = sin(ang) * self.speed
        if (self.rect.y + self.movey < 0) or (self.rect.y + self.movey > HEIGHT):
            self.movey *= -1

    def update(self):
        """update position"""
        if self.ATTATCHED:
            # move and increment colour
            self.movex = you.movex
            self.movey = you.movey

            # self.increment_colour(len(Growth) // 100)

            # simple move
            self.rect.x += self.movex
            self.rect.y += self.movey

        # What happens during a collision
        elif blocklist := self._is_collided():
            # make sure it snaps to edge
            # first move back to where you were before the collision
            # (this helps prevents clipping in the case where the particle has moved too far into the crystal)
            self.rect.x -= self.movex
            self.rect.y -= self.movey

            # closest block
            edgeblock = min(blocklist, key=lambda x: dist(x, self))

            # is it closest to top, bottom, left or right?
            dists = [
                abs(self.rect.top - edgeblock.rect.bottom),
                abs(self.rect.bottom - edgeblock.rect.top),
                abs(self.rect.left - edgeblock.rect.right),
                abs(self.rect.right - edgeblock.rect.left),
            ]
            # snap to closest edge and update 'unsnapped' coordinate to prevent floating blocks
            edge = dists.index(min(dists))
            if edge == 0:
                self.rect.top = edgeblock.rect.bottom
                self.rect.x += self.movex
            elif edge == 1:
                self.rect.bottom = edgeblock.rect.top
                self.rect.x += self.movex
            elif edge == 2:
                self.rect.left = edgeblock.rect.right
                self.rect.y += self.movey
            elif edge == 3:
                self.rect.right = edgeblock.rect.left
                self.rect.y += self.movey

            # boop
            pygame.mixer.Sound.play(sound_size_dict.get(self.size[0], blip))
            # pygame.mixer.Sound.play(melody[(len(Growth) - 1) % (len(melody) - 1)])

            # TODO: try and prevent clipping by testing if particle is inside another particle in growth
            # and moving 'accordingly' if it is

            # add to Growth
            self.remove(Others)
            Growth.add(self)
            self.ATTATCHED = True
            self.num = len(Growth) - 1  # player counts as 1
            self.counter = self.num  # start counter here

            # DEBUG: set a weird colour (bright yellow?) if block is still clipped
            # if self._is_collided():
            #     self.colour = (229, 255, 0)
            # else:
            self.colour = rangedcolourpicker(self.num)

            # poof! effect
            init_poof(self.rect.center, self.colour)

            # off-white for the last block to collide
            self.image.fill((150, 150, 150))
            Growth.sprites()[-2].set_col()

            # don't adjust position when attaching or clipping will happen
            return

        else:
            # simple move
            self.rect.x += self.movex
            self.rect.y += self.movey

            # control boundary
            if outofbounds(self.rect):
                self.kill()
                del self

    # def increment_colour(self, s):
    #     self.counter += 1
    #     self.image.fill(rangedcolourpicker(self.counter))

    def _is_collided(self):
        return pygame.sprite.spritecollide(self, Growth, dokill=False)


class Poof(Particle):
    """Particle effect"""

    def __init__(self, pos: Tuple[float, float], **kwargs):
        super().__init__(edge_len=1, **kwargs)

        self.rect.center = pos

        # choose an angle and move
        ang = rand.random() * 2 * pi
        self.movex = cos(ang) * self.speed
        self.movey = sin(ang) * self.speed

    def update(self):
        # simple move
        self.rect.x += self.movex
        self.rect.y += self.movey
        if outofbounds(self.rect):
            self.kill()
            del self


# STATES
# =============================
def regrow():
    Growth.empty()
    Others.empty()
    Poofs.empty()

    global you
    you = You()
    Growth.add(you)

    global SATURATED, MAIN, PAUSED
    SATURATED = False
    PAUSED = False
    MAIN = True
    pygame.mixer.Sound.play(blip)


def paused():
    pausetext = ingamefont.render(f'PAUSED', False, white)
    pausetextrect = pausetext.get_rect()
    pausetextrect.topright = (WIDTH - 10, 10)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.key == ord('q') or e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if e.key == ord('p'):
                    return

        screen.blit(pausetext, pausetextrect)
        pygame.display.update()
        clock.tick(FPS)


def saturated():
    # print to screen
    finaltext = satufont.render('SATURATION REACHED.', False, white)
    textrect = finaltext.get_rect()
    textrect.center = WIDTH // 2, HEIGHT // 3

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
        for e in pygame.event.get():

            if e.type == pygame.QUIT:
                pygame.quit()
                quit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    you.image.fill(white)
                    regrow()
                if e.key == ord('q') or e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            Growth.draw(screen)
            for text, rect in zip(texts, trects):
                screen.blit(text, rect)
            pygame.display.update()
            clock.tick(FPS)


# SETUP
# =============================
pygame.init()

clock = pygame.time.Clock()

screen = pygame.display.set_mode(SCREENSIZE)

# display settings
background = black
screen.fill(background)
pygame.display.set_caption('GROWTH')

# sounds
blip = pygame.mixer.Sound(resource_path('sounds/Blip1.wav'))
ouch = pygame.mixer.Sound(resource_path('sounds/Ouch1.wav'))
# melody = [pygame.mixer.Sound(note) for note in glob.glob('sounds/melody/melody*.ogg')]

# to make each size of block make a different noise
boops = [pygame.mixer.Sound(f) for f in glob.glob(resource_path('sounds/Boops/Boop?.wav'))]
sound_size_dict = {  # will have to try and rework this for variable size ranges but it'll do for now
    3: boops[0],
    4: boops[1],
    5: boops[2],
    6: boops[3],
    7: boops[4],
    8: boops[5],
    9: boops[6],
    10: boops[7]
}

# startup noise
pygame.mixer.Sound.play(blip)

# for saturation screen
satufont = pygame.font.Font(resource_path("data-latin.ttf"), 30)

# onscreen info
ingamefont = pygame.font.Font(resource_path("Ticketing.ttf"), 20)

# PLAYER
# =============================
you = You()
Growth = pygame.sprite.Group()  # to hold you and all particles attached to you
Growth.add(you)

# PARTICLES
# =============================
Others = pygame.sprite.Group()  # to hold unattached particles
Poofs = pygame.sprite.Group()  # to hold particle effects

# MAIN LOOP
# =============================
t1 = pygame.time.get_ticks()
while MAIN:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            try:
                sys.exit()
            finally:
                MAIN = False

        keys = pygame.key.get_pressed()

        # KEY PRESSES
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                regrow()
            if event.key == ord('p'):
                paused()
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

    # HANDLE PARTICLES
    # ==================================
    # generate new particle
    if (t2 := pygame.time.get_ticks()) - t1 > SPAWNRATE:
        t1 = t2
        # random speed and size
        newsize = rand.randint(*SIZERANGE)
        newspeed = rand.uniform(*SPEEDRANGE)
        Others.add(Other(edge_len=newsize, speed_mult=newspeed))

    # End simulation
    for block in Growth:
        if outofbounds(block.rect):
            SATURATED = True
            MAIN = False
            # pygame.mixer.Sound.play(ouch)
            saturated()

    # onscreen info
    sizetext = ingamefont.render(f'growth: {len(Growth)}', False, white)
    sizetextrect = sizetext.get_rect()
    sizetextrect.topleft = (10, 10)

    screen.fill(background)
    Growth.update()
    Others.update()
    Poofs.update()

    Growth.draw(screen)
    Others.draw(screen)
    Poofs.draw(screen)

    screen.blit(sizetext, sizetextrect)
    pygame.display.update()
    clock.tick(FPS)
