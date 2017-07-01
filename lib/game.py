import numpy as np
from sprites import SpriteStorage
from actors import PyGameKeyboardPlayer, Bullet
import pygame

import enums

BLOCK_COUNT = 13

STATIC_OBJ_PER_BLOCK = 2
SPRITES_PER_OBJ = 2

PIXELS_PER_BLOCK = 16

STATIC_SPRITE_TYPE_COUNT = 4


class MapBuilder(object):
    MAP_SIZE = BLOCK_COUNT * STATIC_OBJ_PER_BLOCK * SPRITES_PER_OBJ

    def __init__(self):
        self._map = np.zeros((self.MAP_SIZE, self.MAP_SIZE), dtype=np.uint8)

    def _add_static(self, x, y, base):
        x *= SPRITES_PER_OBJ
        y *= SPRITES_PER_OBJ

        self._map[y, x] = base + 1
        self._map[y, x + 1] = base + 2
        self._map[y + 1, x] = base + 3
        self._map[y + 1, x + 1] = base + 4

    def add_bricks(self, x, y):
        base = enums.StaticObjectTypes.BRICK.value * STATIC_SPRITE_TYPE_COUNT
        self._add_static(x, y, base)
        return self

    def add_concrete(self, x, y):
        base = enums.StaticObjectTypes.CONCRETE.value * STATIC_SPRITE_TYPE_COUNT
        self._add_static(x, y, base)
        return self

    def get_map(self):
        return self._map.copy()


def brick_collision(x, y, direction, game_state):
    phase = (game_state.map[y, x] - 1) % 4
    game_state.map[y, x] = 0

    if direction == enums.ActorDirections.UP or direction == enums.ActorDirections.DOWN:
        if phase == 3 or phase == 1:
            game_state.map[y, x - 1] = 0

        if phase == 2 or phase == 0:
            game_state.map[y, x + 1] = 0
    else:
        if phase == 2 or phase == 3:
            game_state.map[y - 1, x] = 0

        if phase == 1 or phase == 0:
            game_state.map[y + 1, x] = 0


def concrete_collision(x, y, direction, game_state):
    pass


STATIC_COLLISION_HANDLERS = (
    brick_collision,
    concrete_collision
)


class BulletCollider(object):
    @staticmethod
    def collide_wall(bullet):
        bullet.source_tank.bullet = None

    @staticmethod
    def collide_static(bullet, new_x, new_y, game_state):
        """
        This algorithm assumes that bullet is no larger than minimal static environment block
        """
        bullet.source_tank.bullet = None

        x, y, dx, dy = bullet.get_collision_rect()
        x, y = new_x + x, new_y + y

        if bullet.direction == enums.ActorDirections.UP or bullet.direction == enums.ActorDirections.DOWN:
            if bullet.direction == enums.ActorDirections.UP:
                col_y_min = y / 4
                col_y_max = col_y_min + 1

            else:
                col_y_min = (y + dy) / 4
                col_y_max = col_y_min + 1

            col_x_min = x / 4
            col_x_max = (x + dx + 3) / 4

        else:
            if bullet.direction == enums.ActorDirections.LEFT:
                col_x_min = x / 4
                col_x_max = col_x_min + 1

            else:
                col_x_min = (x + dx) / 4
                col_x_max = col_x_min + 1

            col_y_min = y / 4
            col_y_max = (y + dy + 3) / 4

        need_update = False

        mat_min = (game_state.map[col_y_min, col_x_min] - 1) / 4
        if mat_min >= 0:
            STATIC_COLLISION_HANDLERS[mat_min](col_x_min, col_y_min, bullet.direction, game_state)
            need_update = True

        mat_max = (game_state.map[col_y_max - 1, col_x_max - 1] - 1) / 4
        if mat_max >= 0:
            STATIC_COLLISION_HANDLERS[mat_max](col_x_max - 1, col_y_max - 1, bullet.direction, game_state)
            need_update = True

        if need_update:
            return col_x_min - 1, col_y_min - 1, col_x_max - col_x_min + 2, col_y_max - col_y_min + 2

        return None

    @staticmethod
    def collide_actor(bullet, actor, game_state):
        pass


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

    def set_renderer(self, renderer):
        self._renderer = renderer

    def _move_actor(self, actor, direction, collider=None):
        self._renderer.clear_actor(actor)

        actor.direction = direction
        dx, dy = enums.DIRECTION_VECTORS[actor.direction.value]
        dx *= actor.moving_speed
        dy *= actor.moving_speed

        if self._check_can_move(actor, actor.x + dx, actor.y + dy, collider):
            actor.y += dy
            actor.x += dx
        actor.animate()

    def _apply_action(self, actor):
        action = actor.get_action(self._state)

        if action.value < 4:
            self._move_actor(actor, enums.ActorDirections(action.value))

        if actor.bullet is not None:
            self._move_actor(actor.bullet, actor.bullet.direction, BulletCollider)

        if action == enums.Actions.SHOOT:
            if actor.bullet is None:
                dx, dy = enums.BULLET_TANK_SHIFTS[actor.direction.value]
                actor.bullet = Bullet(actor.x + dx, actor.y + dy, actor.direction, actor)
                self._check_can_move(actor.bullet, actor.bullet.x, actor.bullet.y, collider=BulletCollider)

    def _check_can_move(self, actor, new_x, new_y, collider=None):
        x, y, dx, dy = actor.get_collision_rect()

        max_y = self._state.BOARD_SIZE - y - dy
        max_x = self._state.BOARD_SIZE - x - dx

        if 0 <= new_x <= max_x and 0 <= new_y <= max_y:
            if np.sum(self._state.map[(new_y + y) / 4: (new_y + y + dy + 3) / 4,
                                      (new_x + x) / 4: (new_x + x + dx + 3) / 4]) == 0:
                return True
            else:
                if collider is not None:
                    update_rec = collider.collide_static(actor, new_x, new_y, self._state)
                    if update_rec is not None:
                        self._renderer.update_bg(update_rec)
                return False

        if collider is not None:
            collider.collide_wall(actor)
        return False

    def tick(self):
        for actor in game_state.actors:
            self._apply_action(actor)


class Renderer(object):
    OFF_BOARD_SPACE = 8

    def __init__(self, game_state, screen, scale=4):
        self.size = (game_state.BOARD_SIZE + self.OFF_BOARD_SPACE * 2) * scale
        self._scale = scale
        self._game_state = game_state
        self._sprite_storage = SpriteStorage('../data/tank_sprite.png', self._scale)

        self._screen = screen
        self._screen.init_screen(self.size, self._sprite_storage.palette)

        self._render_env()

    def render(self):
        for actor in self._game_state.actors:
            sprite = self._sprite_storage.get_tank_actor_sprite(actor)
            self._lay_sprite(sprite, actor.x, actor.y)

            bullet = actor.bullet
            if bullet is not None:
                sprite = self._sprite_storage.get_bullet_actor_sprite(bullet)

                self._lay_sprite(sprite, bullet.x, bullet.y)

        return self._screen

    def _make_screen_rect(self, x, y, dx, dy):
        return ((x + self.OFF_BOARD_SPACE) * self._scale,
                (y + self.OFF_BOARD_SPACE) * self._scale,
                 dx * self._scale,
                 dy * self._scale)

    def _render_env(self):
        for x in xrange(self._game_state.map.shape[0]):
            for y in xrange(self._game_state.map.shape[1]):
                obj_index = self._game_state.map[y, x]
                if obj_index != 0:
                    sprite = self._sprite_storage.get_static_object_sprite(obj_index - 1)
                    self._lay_sprite(sprite, x * 4, y * 4)

    def _lay_sprite(self, sprite, x, y):
        x += self.OFF_BOARD_SPACE
        y += self.OFF_BOARD_SPACE
        self._screen.put_sprite(sprite.T, (x * self._scale,
                                           y * self._scale,
                                           sprite.shape[0],
                                           sprite.shape[1]))

    def clear_actor(self, actor):
        _, _, dx, dy = actor.get_collision_rect()
        self._screen.clear(self._make_screen_rect(actor.x, actor.y, dx, dy))

    def update_bg(self, rec):
        for x in xrange(rec[0], rec[0] + rec[2]):
            for y in xrange(rec[1], rec[1] + rec[3]):
                obj_index = self._game_state.map[y, x]
                if obj_index != 0:
                    sprite = self._sprite_storage.get_static_object_sprite(obj_index - 1)
                    self._lay_sprite(sprite, x * 4, y * 4)

                else:
                    self._screen.clear(self._make_screen_rect(x * 4, y * 4, 4, 4))


class PyGameScreen(object):
    def __init__(self):
        self._screen = None
        self._palette = None

    def init_screen(self, size, palette=None):
        self._screen = pygame.display.set_mode((size, size))
        self._palette = palette

    def _make_surface(self, sprite):
        sprite_sf = pygame.surfarray.make_surface(sprite)
        i_p = iter(self._palette)
        sprite_sf.set_palette(list(zip(i_p, i_p, i_p)))
        return sprite_sf

    def put_sprite(self, sprite, rect):
        self._screen.blit(self._make_surface(sprite), rect)

    def clear(self, rect):
        self._screen.fill(0, rect)


if __name__ == "__main__":
    map_builder = MapBuilder()

    for i in range(0, 20):
        for j in range(0, 20):
            if j % 2 == 0:
                map_builder.add_concrete(i, j)
            else:
                map_builder.add_bricks(i, j)

    map = map_builder.get_map()
    game_state = GameState(map).add_actor(PyGameKeyboardPlayer(0, 192, enums.ActorSpriteEnum.PLAYER_1_TANK))

    pygame.init()

    engine = GameEngine(game_state)
    renderer = Renderer(game_state, PyGameScreen())
    engine.set_renderer(renderer)

    clock = pygame.time.Clock()
    while True:
        engine.tick()
        image = renderer.render()
        pygame.display.flip()
        pygame.time.delay(16)
