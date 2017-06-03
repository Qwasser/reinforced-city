import numpy as np
from PIL import Image
from enum import Enum

from actors import ActorDirections, StepCycle


class StaticObjectTypes(Enum):
    BRICK = 0
    CONCRETE = 1


class SpriteStorage(object):
    SPRITE_SIZE = 16

    SPRITE_OFFSETS = {
        'player': (0, 0),
    }

    STATIC_SPRITE_OFFSETS = {
        StaticObjectTypes.BRICK: (16 * 16, 0),
        StaticObjectTypes.CONCRETE: (16 * 16, 16),
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
        self._load_static_object_sprites(im_array)

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
        return self._player_sprites[actor.direction, actor.step_cycle]

    def _load_static_object_sprites(self, sprite_array):
        self.static_object_sprites = np.zeros((len(StaticObjectTypes) * 4, 4, 4), dtype=np.uint8)
        for type in list(StaticObjectTypes):
            base = type.value * 4
            x_offset, y_offset = self.STATIC_SPRITE_OFFSETS[type]
            self.static_object_sprites[base] = sprite_array[y_offset: y_offset + 4, x_offset: x_offset + 4]
            self.static_object_sprites[base + 1] = sprite_array[y_offset: y_offset + 4, x_offset + 4: x_offset + 8]
            self.static_object_sprites[base + 2] = sprite_array[y_offset + 4: y_offset + 8, x_offset: x_offset + 4]
            self.static_object_sprites[base + 3] = sprite_array[y_offset + 4: y_offset + 8, x_offset + 4: x_offset + 8]

    def get_static_object_sprite(self, index):
        return self.static_object_sprites[index]

if __name__ == "__main__":
    pass

