import pygame
import sys
import random as rand
from typing import Tuple
from math import floor, hypot, sin, cos, pi


# VARIABLES
# =============================
SIZE = width, height = 640, 480

white = 255, 255, 255
black = 0, 0, 0
red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255

FPS = 60  # frame rate
SATURATED = False  # 'game over'

main = True


# FUNCTIONS
# =============================
def dist(a, b):
    """Gets distance between centers of two rects"""
    return hypot(a.rect.centerx - b.rect.centerx, a.rect.centery - b.rect.centery)


def touching_edge(shape: pygame.Rect) -> bool:
    """Is a block touching an edge"""
    if 0 in {shape.left, shape.top} \
            or shape.right == width \
            or shape.bottom == height:
        return True
    else:
        return False


# OBJECTS
# =============================
class Particle(pygame.sprite.Sprite):
    def __init__(self,
                 edge_len: int = 20,
                 colour: Tuple[int, int, int] = white,
                 speed_mult: float = 1):
        super().__init__()

        self.speed = speed_mult * edge_len // 2
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


class You(Particle):
    def __init__(self):
        super().__init__()

        # start in the middle of the screen
        self.rect.x = width // 2
        self.rect.y = height // 2

    def update(self):
        """update position"""
        prevx = self.rect.x
        prevy = self.rect.y

        # simple move
        self.rect.x += self.movex
        self.rect.y += self.movey

        # control boundary
        if self.rect.left < 0 or self.rect.right > width:
            self.rect.x = prevx
        if self.rect.top < 0 or self.rect.bottom > height:
            self.rect.y = prevy


class Other(Particle):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ATTATCHED = False  # whether or not the particle is attached to you

        # colour
        self.image.fill((50, 50, 50))

        # choose an edge to spawn on
        self.rect.x, self.rect.y = (floor(rand.random() * width), floor(rand.random() * height))
        self.rect.x = 0 if self.rect.x < width // 2 else width
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

        # print(f"Other generated at {self.rect.x, self.rect.y}, "
        #       f"moving in direction ({self.movex:.2g}, {self.movey:.2g})")

    def update(self):
        """update position"""

        if self.ATTATCHED:
            self.movex = you.movex
            self.movey = you.movey

        elif blocklist := self._is_collided():
            print(f"Collided! Growth of {len(Growth)}")
            # add to Growth
            self.remove(Others)
            Growth.add(self)
            self.ATTATCHED = True

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
            print(f'edge was {edge}')
            return

        else:
            # control boundary
            if self.rect.x < 0 or self.rect.x > width:
                self.movex *= -1
                # print("removed at", self.rect.x, self.rect.y)
                self.kill()
            if self.rect.y < 0 or self.rect.y > height:
                # print("removed at", self.rect.x, self.rect.y)
                self.kill()

        # simple move
        self.rect.x += self.movex
        self.rect.y += self.movey

    def _is_collided(self):
        return pygame.sprite.spritecollide(self, Growth, dokill=False)


# SETUP
# =============================
pygame.init()

clock = pygame.time.Clock()

screen = pygame.display.set_mode(SIZE)

background = black
screen.fill(background)
pygame.display.set_caption('GROWTH')
font = pygame.font.Font("data-latin.ttf", 32)


# PLAYER
# =============================
you = You()
Growth = pygame.sprite.Group()
Growth.add(you)


# PARTICLES
# =============================
Others = pygame.sprite.Group()


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
    finaltext = font.render('SATURATION REACHED.', False, white)
    textrect = finaltext.get_rect()
    textrect.center = width // 2, height // 2

    scoretext = font.render(f'FINAL SIZE: {len(Growth)}', False, white)
    scorerect = scoretext.get_rect()
    scorerect.center = tuple([x + textrect.height for x in textrect.center])

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
            screen.blit(finaltext, textrect)
            screen.blit(scoretext, scorerect)
            pygame.display.update()
            clock.tick(FPS)


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
            if event.key == ord('q'):
                pygame.quit()
                sys.exit()

    # HANDLE PARTICLES
    # ==================================
    # generate new particle
    if (t2 := pygame.time.get_ticks()) - t > 500:
        t = t2
        Others.add(Other())
        # print(f"n of Others: {len(Others)}")

    for block in Growth:
        if touching_edge(block.rect):
            SATURATED = True
            saturated()

    screen.fill(background)
    Growth.update()
    Others.update()

    Growth.draw(screen)
    Others.draw(screen)

    pygame.display.update()
    clock.tick(FPS)
