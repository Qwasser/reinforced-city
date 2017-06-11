import numpy as np
from PIL import Image


import enums


def scale_up_sprite(sprite, scale):
    return np.kron(sprite, np.ones((scale, scale), dtype=np.uint8))


class SpriteStorage(object):
    TILE_SIZE = 16
    STATIC_OBJECT_PART_SIZE = 4
    STATIC_OBJECT_PART_OFFSETS = [
        (0, 0),
        (0, STATIC_OBJECT_PART_SIZE),
        (STATIC_OBJECT_PART_SIZE, 0),
        (STATIC_OBJECT_PART_SIZE, STATIC_OBJECT_PART_SIZE)
    ]

    SPRITE_TILE_OFFSETS = {
        enums.ActorSpriteEnum.PLAYER_1_TANK: (0, 0),
        enums.ActorSpriteEnum.BULLET: (20, 6),
        enums.StaticObjectTypes.BRICK: (16, 0),
        enums.StaticObjectTypes.CONCRETE: (16, 1),
        enums.ActorSpriteEnum.QUICK_TANK: (8, 5)
    }

    def __init__(self, sprite_file, scale):
        self.palette = None
        self._player_sprites = {}
        self._bullet_sprites = {}
        self._scale = scale
        self._load_sprites(sprite_file)

    def _load_sprites(self, sprite_file):
        im = Image.open(sprite_file)
        im = im.convert(mode='P')
        self.palette = im.getpalette()

        im_array = np.asarray(im, dtype=np.uint8)

        for tank_sprite in enums.TANK_SPRITES:
            self._load_tank_sprites(im_array, tank_sprite)

        self._load_bullet_sprites(im_array)
        self._load_static_object_sprites(im_array)

    def _get_sprite_offsets(self, sprite_type):
        base_x_offset, base_y_offset = self.SPRITE_TILE_OFFSETS[sprite_type]
        return base_x_offset * self.TILE_SIZE, base_y_offset * self.TILE_SIZE

    def _crop_sprite_and_rescale(self, rect, sprite_array):
        x, y, dx, dy = rect
        sprite = sprite_array[y: y + dy, x: x + dx]
        return scale_up_sprite(sprite, self._scale)

    def _load_tank_sprites(self, sprite_array, tank_sprite_type):
        sprite_index = 0

        base_x_offset, base_y_offset = self._get_sprite_offsets(tank_sprite_type)

        for direction in enums.ActorDirections:
            for step_cycle in enums.TankAnimationCycle:
                x_offset = base_x_offset + self.TILE_SIZE * sprite_index
                sprite_rect = (x_offset, base_y_offset, self.TILE_SIZE, self.TILE_SIZE)

                sprite_key = (tank_sprite_type, direction, step_cycle)
                self._player_sprites[sprite_key] = self._crop_sprite_and_rescale(sprite_rect, sprite_array)
                sprite_index += 1

    def _load_bullet_sprites(self, sprite_array):
        base_x_offset, base_y_offset = self._get_sprite_offsets(enums.ActorSpriteEnum.BULLET)

        sprite_index = 0
        for direction in enums.ActorDirections:
            x_offset = base_x_offset + self.TILE_SIZE / 2 * sprite_index

            sprite = sprite_array[base_y_offset: base_y_offset + self.TILE_SIZE,
                                  x_offset: x_offset + self.TILE_SIZE / 2]

            rect = enums.BULLET_SPRITE_RECTS[direction.value]

            self._bullet_sprites[direction] = self._crop_sprite_and_rescale(rect, sprite)
            sprite_index += 1

    def _load_static_object_sprites(self, sprite_array):
        self.static_object_sprites = np.zeros((len(enums.StaticObjectTypes) * self.STATIC_OBJECT_PART_SIZE,
                                               self.STATIC_OBJECT_PART_SIZE * self._scale,
                                               self.STATIC_OBJECT_PART_SIZE * self._scale),
                                              dtype=np.uint8)

        for type in list(enums.StaticObjectTypes):
            base = type.value * len(self.STATIC_OBJECT_PART_OFFSETS)

            x_offset, y_offset = self._get_sprite_offsets(type)

            for i, part_offset in enumerate(self.STATIC_OBJECT_PART_OFFSETS):
                x = x_offset + part_offset[0]
                y = y_offset + part_offset[1]
                sprite = sprite_array[y: y + self.STATIC_OBJECT_PART_SIZE, x: x + self.STATIC_OBJECT_PART_SIZE]
                self.static_object_sprites[base + i] = scale_up_sprite(sprite, self._scale)

    def array_to_img(self, img):
        img = Image.fromarray(img)
        img.putpalette(self.palette)
        return img

    def get_tank_actor_sprite(self, actor):
        return self._player_sprites[actor.sprite, actor.direction, actor.step_cycle]

    def get_bullet_actor_sprite(self, bullet):
        return self._bullet_sprites[bullet.direction]

    def get_static_object_sprite(self, index):
        return self.static_object_sprites[index]

if __name__ == "__main__":
    sprite_storage = SpriteStorage('../data/tank_sprite.png', 4)
    for key, item in sprite_storage._bullet_sprites.items():
        print key
        print item
