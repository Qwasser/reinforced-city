import enums
import pygame


class Actor(object):
    def __init__(self, x, y, sprite, direction, moving_speed=1):
        self.x = x
        self.y = y
        self.direction = direction
        self.sprite = sprite
        self.moving_speed = moving_speed

    def animate(self):
        raise NotImplemented

    def get_collision_rect(self):
        return enums.get_collision_rect(self.sprite, self.direction)


class TankActor(Actor):
    def __init__(self, x, y, tank_sprite):
        assert tank_sprite in enums.TANK_SPRITES

        super(TankActor, self).__init__(x, y, tank_sprite, enums.ActorDirections.UP)
        self.step_cycle = enums.TankAnimationCycle.FIRST
        self._step_counter = 0
        self.bullet = None
        self.tank_sprite = tank_sprite

    def get_action(self, game_state):
        pass

    def animate(self):
        self._step_counter += 1
        self._step_counter %= 3
        if self._step_counter == 0:
            if self.step_cycle == enums.TankAnimationCycle.FIRST:
                self.step_cycle = enums.TankAnimationCycle.SECOND
            else:
                self.step_cycle = enums.TankAnimationCycle.FIRST

    def remove_bullet(self):
        self.bullet = None


class Bullet(Actor):
    def __init__(self, y, x, direction, source_tank):
        super(Bullet, self).__init__(x, y, enums.ActorSpriteEnum.BULLET, direction, moving_speed=2)
        self.x = x
        self.y = y
        self.direction = direction
        self.source_tank = source_tank

    def animate(self):
        pass


class PyGameKeyboardPlayer(TankActor):
    """
    This player works only if pygame was initialized
    """
    def __init__(self, x, y, tank_sprite):
        super(PyGameKeyboardPlayer, self).__init__(x, y, tank_sprite)

    def get_action(self, field):
        pygame.event.get(pygame.KEYDOWN)  # code below does not work without this

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            return enums.Actions.GO_UP

        if keys[pygame.K_a]:
            return enums.Actions.GO_LEFT

        if keys[pygame.K_s]:
            return enums.Actions.GO_DOWN

        if keys[pygame.K_d]:
            return enums.Actions.GO_RIGHT

        if keys[pygame.K_SPACE]:
            return enums.Actions.SHOOT

        return enums.Actions.DO_NOTHING
