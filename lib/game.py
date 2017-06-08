import numpy as np
from sprites import SpriteStorage, StaticObjectTypes
from actors import PyGameKeyboardPlayer
import pygame

from actors import Actions, ActorDirections, DIRECTION_VECTORS, Bullet

BLOCK_COUNT = 13

STATIC_OBJ_PER_BLOCK = 2
SPRITES_PER_OBJ = 2

PIXELS_PER_BLOCK = 16

STATIC_SPRITE_TYPE_COUNT = 4


class MapBuilder(object):
    MAP_SIZE = BLOCK_COUNT * STATIC_OBJ_PER_BLOCK * SPRITES_PER_OBJ

    def __init__(self):
        self._map = np.zeros((self.MAP_SIZE, self.MAP_SIZE), dtype=np.uint8)

    def add_bricks(self, x, y):
        base = StaticObjectTypes.BRICK.value * STATIC_SPRITE_TYPE_COUNT

        x *= SPRITES_PER_OBJ
        y *= SPRITES_PER_OBJ

        self._map[y, x] = base + 1
        self._map[y, x + 1] = base + 2
        self._map[y + 1, x] = base + 3
        self._map[y + 1, x + 1] = base + 4
        return self

    def get_map(self):
        return self._map.copy()


class GameState(object):
    BOARD_SIZE = BLOCK_COUNT * PIXELS_PER_BLOCK

    def __init__(self, map):
        self.map = map
        self.actors = []

    def add_actor(self, actor):
        self.actors.append(actor)
        return self


class GameEngine(object):
    def __init__(self, game_state):
        self._state = game_state

    def _apply_action(self, actor):
        action = actor.get_action(self._state)
        if action == Actions.GO_UP:
            actor.direction = ActorDirections.UP
            if self._check_can_move(actor, actor.x, actor.y - 1):
                actor.y -= 1
            else:
                actor.y = actor.y

        if action == Actions.GO_DOWN:
            actor.direction = ActorDirections.DOWN
            if self._check_can_move(actor, actor.x, actor.y + 1):
                actor.y += 1
            else:
                actor.y = actor.y

        if action == Actions.GO_LEFT:
            actor.direction = ActorDirections.LEFT
            if self._check_can_move(actor, actor.x - 1, actor.y):
                actor.x -= 1
            else:
                actor.x = actor.x

        if action == Actions.GO_RIGHT:
            actor.direction = ActorDirections.RIGHT
            if self._check_can_move(actor, actor.x + 1, actor.y):
                actor.x += 1
            else:
                actor.x = actor.x

        if actor.bullet is not None:
            delta_y, delta_x = DIRECTION_VECTORS[actor.bullet.direction.value]
            delta_y, delta_x = delta_y * 2, delta_x * 2
            actor.bullet.x += delta_x
            actor.bullet.y += delta_y

        if action == Actions.SHOOT:
            if actor.bullet is None:
                if actor.direction == ActorDirections.UP:
                    actor.bullet = Bullet(actor.y - 3, actor.x + 6, actor.direction)

                if actor.direction == ActorDirections.DOWN:
                    actor.bullet = Bullet(actor.y + 16, actor.x + 6, actor.direction)

                if actor.direction == ActorDirections.LEFT:
                    actor.bullet = Bullet(actor.y + 6, actor.x - 3, actor.direction)

                if actor.direction == ActorDirections.RIGHT:
                    actor.bullet = Bullet(actor.y + 6, actor.x + 16, actor.direction)

    def _check_can_move(self, actor, new_x, new_y):
        max_cor = self._state.BOARD_SIZE - actor.size
        if 0 <= new_x < max_cor and 0 <= new_y < max_cor:
            if np.sum(self._state.map[new_y / 4: (new_y + actor.size + 3) / 4,
                                      new_x / 4: (new_x + actor.size + 3) / 4]) == 0:
                return True
        return False

    def tick(self):
        for actor in game_state.actors:
            self._apply_action(actor)


def scale_up_screen(screen, scale):
    return np.kron(screen, np.ones((scale, scale), dtype=np.uint8))


class Renderer(object):
    def __init__(self, game_state, sprite_storage, scale=4):
        self.size = game_state.BOARD_SIZE
        self.screen_size = scale * self.size
        self._screen = np.zeros((self.size, self.size), dtype=np.uint8)
        self._scale = scale
        self._game_state = game_state
        self._sprite_storage = sprite_storage
        self._render_env()

    def render(self):
        for actor in self._game_state.actors:
            sprite = self._sprite_storage.get_player_actor_sprite(actor)
            self._screen[actor.y: actor.y + sprite.shape[0],
                         actor.x: actor.x + sprite.shape[1]] = sprite

            bullet = actor.bullet
            if bullet is not None:
                sprite = self._sprite_storage.get_bullet_actor_sprite(bullet)
                self._screen[bullet.y: bullet.y + sprite.shape[0],
                             bullet.x: bullet.x + sprite.shape[1]] = sprite

        return scale_up_screen(self._screen, self._scale)

    def _render_env(self):
        for x in xrange(self._game_state.map.shape[0]):
            for y in xrange(self._game_state.map.shape[1]):
                obj_index = self._game_state.map[y, x]
                if obj_index != 0:
                    sprite = self._sprite_storage.get_static_object_sprite(obj_index - 1)
                    self._screen[y * 4: y * 4 + sprite.shape[0],
                                 x * 4: x * 4 + sprite.shape[1]] = sprite

    def _rerender_env_sector(self, x0, y0, x1, y1):
        pass


if __name__ == "__main__":
    map_builder = MapBuilder()

    for i in range(5, 10):
        for j in range(5, 10):
            map_builder.add_bricks(i, j)

    map = map_builder.get_map()
    game_state = GameState(map).add_actor(PyGameKeyboardPlayer(192, 0))

    sprite_storage = SpriteStorage('../data/tank_sprite.png')

    pygame.init()

    engine = GameEngine(game_state)
    renderer = Renderer(game_state, sprite_storage)

    screen = pygame.display.set_mode((renderer.screen_size, renderer.screen_size))
    clock = pygame.time.Clock()
    while True:
        engine.tick()
        image = renderer.render()
        image = np.asarray(image, dtype=np.uint8)

        image = image.T
        sf = pygame.surfarray.make_surface(image)
        p = sprite_storage.palette
        i_p = iter(p)
        sf.set_palette(list(zip(i_p, i_p, i_p)))
        screen.blit(sf, (0, 0))
        pygame.display.flip()
        clock.tick(80)
