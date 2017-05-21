import numpy as np
from sprites import SpriteStorage
from actors import DummyPlayer
import PIL as pillow


class GameState(object):
    BOARD_SIZE = 13 * 16

    def __init__(self):
        self.actors = []

    def add_actor(self, actor):
        self.actors.append(actor)
        return self


class GameEngine(object):
    def __init__(self):
        # init field
        pass

    def tick(self):
        pass


class Renderer(object):
    def __init__(self, game_state, sprite_storage, scale=4):
        size = game_state.BOARD_SIZE * scale
        self._screen = np.zeros((size, size), dtype=np.uint8)
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
    game_state = GameState().add_actor(DummyPlayer(192, 0))
    sprite_storage = SpriteStorage('../data/tank_sprite.png')
    renderer = Renderer(game_state, sprite_storage)
    renderer.render().show()
