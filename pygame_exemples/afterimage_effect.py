import pygame
import random
import gzip
import base64
#afterimage effect pygame
#https://stackoverflow.com/questions/57029253/how-to-add-afterimages-in-pygame
TILESIZE = 64
GRID_W, GRID_H = (10, 7)
LOOKUP = None

class Shadow(pygame.sprite.Sprite):
    def __init__(self, source):
        super().__init__()
        self._layer = 5
        self.image = source.image.copy().convert_alpha()
        self.image.fill((0, 0, 200, 100), special_flags=pygame.BLEND_ADD)
        self.rect = source.rect.copy()
        self.timeout = 200

    def update(self, events, dt):
        self.timeout -= dt
        if self.timeout <= 0:
            self.kill()

class Actor(pygame.sprite.Sprite):
    def __init__(self, grid_pos):
        super().__init__()
        self._layer = 10
        data, size = gzip.decompress(base64.b64decode(HYDRA)), (64, 64)
        self.image = pygame.image.fromstring(data, size, "RGB")
        self.image.set_colorkey((71, 108, 108))
        self.rect = self.image.get_rect()
        self.pos = pygame.math.Vector2()
        self.update_pos(grid_pos)
        self.timeout = 1000
        self.shadow_timeout = 100

    def update_pos(self, grid_pos):
        self.target_pos = None
        self.target_grid_pos = None
        self.grid_pos = grid_pos
        self.rect.center = get_grid_rect(grid_pos).center
        self.pos = pygame.math.Vector2(self.rect.center)

    def move_random(self):
        d = random.choice([-1, 1])
        x, y = self.grid_pos
        if random.randint(0, 2):
            x += d
        else:
            y += d
        self.target_pos = pygame.math.Vector2(get_grid_rect((x, y)).center)
        self.target_grid_pos = (x, y)

    def update(self, events, dt):
        self.timeout -= dt
        if self.timeout <= 0:
            self.timeout = 1000
            self.move_random()
        if self.target_grid_pos:
            self.shadow_timeout -= dt
            if self.shadow_timeout <= 0:
                self.shadow_timeout = 100
                self.groups()[0].add(Shadow(self))
            self.pos = self.pos.lerp(self.target_pos, 0.1)
            if self.pos.distance_to(self.target_pos) < 1:
                self.update_pos(self.target_grid_pos)
        self.rect.center = self.pos

def get_grid_rect(pos):
    x, y = pos
    return LOOKUP[y][x]

def create_grid():
    surf = pygame.Surface((TILESIZE * GRID_W, TILESIZE * GRID_H))
    surf.set_colorkey((2, 2, 2))
    surf.fill((2, 2, 2))
    grid = []
    for y in range(GRID_H):
        line = []
        for x in range(GRID_W):
            r = pygame.Rect(x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE)
            line.append(r)
            pygame.draw.rect(surf, pygame.Color('grey'), r, 1)
        grid.append(line)

    return grid, surf

def main():
    screen = pygame.display.set_mode((TILESIZE * GRID_W, TILESIZE * GRID_H))
    dt, clock = 0, pygame.time.Clock()
    grid, grid_surf = create_grid()
    global LOOKUP 
    LOOKUP = grid
    sprites = pygame.sprite.LayeredUpdates(Actor((4, 3)))
    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                return
        sprites.update(events, dt)
        screen.fill((30, 30, 30))
        screen.blit(grid_surf, (0, 0))
        sprites.draw(screen)
        pygame.display.flip()
        dt = clock.tick(60)

HYDRA = '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'

if __name__ == '__main__':
    main()
