import numpy as np
from PIL import Image

from actors import ActorDirections, StepCycle


def scale_up_sprite(sprite, scale):
    return np.kron(sprite, np.ones((scale, scale), dtype=np.uint8))


class SpriteStorage(object):
    SPRITE_SIZE = 16

    SPRITE_OFFSETS = {
        'player': (0, 0)
    }

    def __init__(self, sprite_file):
        self.palette = None
        self._player_sprites = {}

        self._load_sprites(sprite_file)

    def _load_sprites(self, sprite_file):
        im = Image.open(sprite_file)
        im = im.convert(mode='P')
        self.palette = im.getpalette()
        im_array = np.asarray(im, dtype=np.uint8)
        self._load_player_sprites(im_array)

    def _load_player_sprites(self, sprite_array):
        sprite_index = 0

        base_x_offset, base_y_offset = self.SPRITE_OFFSETS['player']
        base_x_offset *= self.SPRITE_SIZE
        base_y_offset *= self.SPRITE_SIZE

        for direction in ActorDirections.__members__.items():
            for step_cycle in StepCycle.__members__.items():

                x_offset = base_x_offset + self.SPRITE_SIZE * sprite_index
                self._player_sprites[(direction[1], step_cycle[1])] =\
                    sprite_array[base_y_offset: base_y_offset + self.SPRITE_SIZE,
                                 x_offset: x_offset + self.SPRITE_SIZE]
                sprite_index += 1

    def array_to_img(self, img):
        img = Image.fromarray(img)
        img.putpalette(self.palette)
        return img

    def get_player_actor_sprite(self, actor, scale=1):
        return scale_up_sprite(self._player_sprites[actor.direction, actor.step_cycle], scale)

if __name__ == "__main__":
    pass

