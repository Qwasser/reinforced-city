import numpy as np
from sprites import SpriteStorage
from actors import PyGameKeyboardPlayer
import pygame

from actors import Actions, ActorDirections


class GameState(object):
    BOARD_SIZE = 13 * 16

    def __init__(self):
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
            if self._check_can_move(actor, actor.x - 1, actor.x):
                actor.x -= 1
            else:
                actor.x = actor.x

        if action == Actions.GO_RIGHT:
            actor.direction = ActorDirections.RIGHT
            if self._check_can_move(actor, actor.x + 1, actor.x):
                actor.x += 1
            else:
                actor.x = actor.x

    def _check_can_move(self, actor, new_x, new_y):
        max_cor = self._state.BOARD_SIZE - actor.size
        if 0 <= new_x < max_cor and 0 <= new_y < max_cor:
            return True
        return False

    def tick(self):
        for actor in game_state.actors:
            self._apply_action(actor)


class Renderer(object):
    def __init__(self, game_state, sprite_storage, scale=4):
        self.size = game_state.BOARD_SIZE * scale
        self._screen = np.zeros((self.size, self.size), dtype=np.uint8)
        self._scale = scale
        self._game_state = game_state
        self._sprite_storage = sprite_storage

    def render(self):
        self._screen.fill(0)
        for actor in self._game_state.actors:
            sprite = self._sprite_storage.get_player_actor_sprite(actor, scale=self._scale)
            self._screen[actor.y * self._scale: actor.y * self._scale + sprite.shape[0],
                         actor.x * self._scale: actor.x * self._scale + sprite.shape[1]] = sprite
        return self._sprite_storage.array_to_img(self._screen)


if __name__ == "__main__":
    game_state = GameState().add_actor(PyGameKeyboardPlayer(192, 0))
    sprite_storage = SpriteStorage('../data/tank_sprite.png')

    pygame.init()

    engine = GameEngine(game_state)
    renderer = Renderer(game_state, sprite_storage)

    screen = pygame.display.set_mode((renderer.size, renderer.size))
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
