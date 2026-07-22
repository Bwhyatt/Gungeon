import pygame
import math
import os

# Rotates an image around a point other than its centre.
# Used because swords rotate around their handle instead of their middle.
def rotate_around_pivot(image, angle_deg, pivot_on_sprite, pivot_on_screen):
    w, h = image.get_size()
    # Finds the distance between the image centre and the rotation point.
    center = pygame.Vector2(w / 2, h / 2)
    offset = pivot_on_sprite - center

    # Rotates the offset so the pivot stays fixed while the image rotates.
    rotated_offset = offset.rotate(-angle_deg)

    rotated_image = pygame.transform.rotate(image, angle_deg)

    # Moves the rotated image back so the handle remains attached
    # to the original position.
    new_center = pivot_on_screen - rotated_offset
    rect = rotated_image.get_rect(center=new_center)

    return rotated_image, rect


class RegularSword:
    def __init__(self, size, Name, Targetpos, position, Enemy):
        # Size of the sword sprite and collision area.
        self.DamageCooldown = 0
        self.DamageCooldownTime = 0.5
        self.size = pygame.Vector2(size)

        path = f"SpriteSheets/Swords/{Name}.png"

        # Loads the sword sprite if it exists.
        # If the file does not exist, creates a placeholder instead
        # so the game does not crash.
        if os.path.exists(path):
            self.OriginalImage = pygame.image.load(path).convert_alpha()
            self.OriginalImage = pygame.transform.scale(self.OriginalImage, self.size)
        else:
            self.OriginalImage = self._make_placeholder_sprite()

        self.pos = pygame.Vector2(position)
        self.Targetpos = pygame.Vector2(Targetpos)

        # Determines whether this sword belongs to an enemy.
        # Enemy swords attack automatically while player swords use input.
        self.EnemyOwner = Enemy

        # Stores the currently rotated image, its rectangle,
        # and the pixel collision mask.
        self.Image = None
        self.ImageRect = None
        self.Mask = None

        # The sword rotates around this point instead of the centre.
        # 0.15 places the pivot near the handle of the sword.
        self.PivotOnSprite = pygame.Vector2(self.size.x * 0.15, self.size.y / 2)

        # Controls the delay between attacks.
        self.CoolDownDuration = 0.75
        self.CoolDownTimer = self.CoolDownDuration

        # Controls the length and state of a sword swing.
        self.SwingTimer = 0.25
        self.SwingDuration = 0
        self.Swinging = False

        # Controls the parry window and cooldown.
        self.ParryDuration = 0
        self.ParryTimer = 0.4
        self.ParryCoolDownDuration = 0.75
        self.ParryCoolDownTimer = self.ParryCoolDownDuration
        self.Parrying = False
        self.ParryRect = None

        # These values define the movement range of the sword swing.
        self.SwingStartAngle = -70
        self.SwingEndAngle = 40

        # These values define the parry animation range.
        self.ParryStartAngle = -25
        self.ParryEndAngle = 25

        # Current position in the sword rotation animation.
        self.CurrentAngleOffset = self.SwingStartAngle

        self.damage = 50
        self.tag = "Sword"

        # Prevents multiple hits on the same target during one swing.
        self.HasHit = False
        self.HitObjects = []
        self.hit_enemies = []
        # Controls whether this sword auto-attacks on cooldown when enemy-owned.
        # Enemies with their own attack/telegraph logic (e.g. Shielder) disable this.
        self.AutoSwing = True
    def _make_placeholder_sprite(self):
        # Creates a basic sprite if the sword image is missing.
        surf = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(surf, "red", surf.get_rect())
        return surf

    def determinedir(self, target):
        # Converts the direction towards the target into an angle.
        # This is used for rotating the sword towards the mouse/player.
        direction = target - self.pos
        return math.atan2(-direction.y, direction.x)

    def Swing(self, position, Targetpos=None):

        # Clears previous targets because every swing is a new attack.
        self.hit_enemies.clear()
        self.HitObjects.clear()

        self.Swinging = True
        self.HasHit = False
        self.SwingDuration = 0

        # Resets the cooldown immediately so the sword can't re-trigger
        # Swing() again on the next frame before it finishes swinging.
        self.CoolDownTimer = self.CoolDownDuration

        # Resets the sword back to the starting angle of the swing.
        self.CurrentAngleOffset = self.SwingStartAngle

        self.pos = pygame.Vector2(position)

        if Targetpos:
            self.Targetpos = pygame.Vector2(Targetpos)
    def Parry(self, position):

        # Starts the parry state and creates the area
        # that can detect incoming attacks.
        self.Parrying = True
        self.ParryDuration = 0

        self.ParryRect = pygame.Rect(
            position[0] - self.size.x,
            position[1] - self.size.y,
            self.size.x * 2,
            self.size.y * 2
        )

    def CanSwing(self):
        # Checks if the attack cooldown has finished.
        return self.CoolDownTimer <= 0

    def CanParry(self):
        # Checks if the parry cooldown has finished.
        return self.ParryCoolDownTimer <= 0

    def UpdateMask(self):

        # Combines the sword direction with the current swing angle.
        angle = math.degrees(self.acute_rad) + self.CurrentAngleOffset

        # Creates the rotated sword image while keeping the pivot fixed.
        self.Image, self.ImageRect = rotate_around_pivot(
            self.OriginalImage,
            angle,
            self.PivotOnSprite,
            self.pos
        )

        # Creates a pixel-perfect collision mask from the rotated image.
        self.Mask = pygame.mask.from_surface(self.Image)

    def Collision(self, obj):

        # The sword cannot damage anything unless it is swinging.

        if not self.Swinging:
            return False

        if self.DamageCooldown > 0:
            return False

        # Prevents hitting the same object multiple times per swing.
        if obj in self.HitObjects:
            return False

        if self.Mask is None or not hasattr(obj, "Rect"):
            return False

        # Creates a mask for the object being hit.
        # This allows collision with the rotated sword image.
        objMask = pygame.mask.Mask(
            (obj.Rect.width, obj.Rect.height),
            fill=True
        )

        # Calculates where the object's mask sits relative to the sword.
        offset = (
            obj.Rect.x - self.ImageRect.x,
            obj.Rect.y - self.ImageRect.y
        )

        if self.Mask.overlap(objMask, offset):
            self.HitObjects.append(obj)
            return True

        return False

    def ParryCollision(self, obj):

        # Checks if an object is inside the temporary parry area.
        if self.ParryRect and hasattr(obj, "Rect"):
            return self.ParryRect.colliderect(obj.Rect)

        return False

    def ResolveCollision(self, obj, damage):
        if hasattr(obj, "TakeDamage"):
            obj.TakeDamage(damage)
            self.DamageCooldown = self.DamageCooldownTime

    def ResolveParryCollision(self, obj):

        # Default parry behaviour stuns enemies.
        if hasattr(obj, "SelfStun"):
            obj.SelfStun(4)

    def SwingStateChange(self, dt):

        # Handles the sword moving through its attack animation.
        self.DamageCooldown -= dt

        if self.DamageCooldown < 0:
            self.DamageCooldown = 0
        if self.Swinging:
            self.SwingDuration += dt

            # Converts elapsed time into a value from 0-1.
            progress = min(
                self.SwingDuration / self.SwingTimer,
                1
            )

            # Moves the sword smoothly between the start and end angle.
            self.CurrentAngleOffset = (
                self.SwingStartAngle +
                (self.SwingEndAngle-self.SwingStartAngle)*progress
            )

            if self.SwingDuration >= self.SwingTimer:
                self.Swinging = False
                self.CoolDownTimer = self.CoolDownDuration
                self.HitObjects.clear()

        else:
            self.CoolDownTimer -= dt

        # Handles the parry duration.
        if self.Parrying:
            self.ParryDuration += dt

            if self.ParryDuration >= self.ParryTimer:
                self.Parrying = False
                self.ParryRect = None
                self.ParryCoolDownTimer = self.ParryCoolDownDuration

        else:
            self.ParryCoolDownTimer -= dt
    def update(self, dt, screen, keys, position, Targetpos):

        # Updates cooldowns, swing progress and parry timers.
        self.SwingStateChange(dt)

        self.pos = pygame.Vector2(position)
        self.Targetpos = pygame.Vector2(Targetpos)

        # Finds the direction the sword should face.
        self.acute_rad = self.determinedir(self.Targetpos)

        if self.EnemyOwner:

            # Enemy swords automatically attack when available,
            # unless something else (e.g. Shielder) drives their attacks manually.
            if self.AutoSwing and self.CanSwing():
                self.Swing(self.pos, self.Targetpos)

        else:

            # Left click performs a sword swing.
            if pygame.mouse.get_pressed()[0] and self.CanSwing() and not self.Swinging and not self.Parrying:
                self.Swing(self.pos, self.Targetpos)

            # Right click activates parry.
            if pygame.mouse.get_pressed()[2] and self.CanParry() and not self.Swinging and not self.Parrying:
                self.Parry(self.pos)

        # Updates the rotated sword image and collision mask.
        self.UpdateMask()

    def draw(self, screen, camera, size=None, position=None):

        # The sword is only visible during attacks or parries.
        if self.Image and (self.Swinging or self.Parrying):
            screen.blit(self.Image, camera.apply(self.ImageRect))


class VampireSword(RegularSword):
    def __init__(self, size, Name, Targetpos, position, Enemy):
        super().__init__(size, Name, Targetpos, position, Enemy)

        # Amount of health restored after damaging an enemy.
        self.RegenAmount = 10

    def ResolveCollision(self, obj, damage):

        # Performs normal sword damage first.
        super().ResolveCollision(obj, damage)

        # Restores health to the owner if the owner has health.
        if hasattr(self.EnemyOwner, "health"):
            self.EnemyOwner.health += self.RegenAmount

            # Prevents healing above maximum health.
            self.EnemyOwner.health = min(
                self.EnemyOwner.health,
                self.EnemyOwner.Maxhealth
            )


class BaseballBat(RegularSword):
    def __init__(self, size, Name, Targetpos, position, Enemy):
        super().__init__(size, Name, Targetpos, position, Enemy)

        # Controls how long the player holds the attack
        # before releasing the charged hit.
        self.Charging = False
        self.ChargeDuration = 0
        self.MaxChargeTime = 6

    def update(self, dt, screen, keys, position, Targetpos):

        self.SwingStateChange(dt)

        self.pos = pygame.Vector2(position)
        self.Targetpos = pygame.Vector2(Targetpos)

        self.acute_rad = self.determinedir(self.Targetpos)

        if not self.EnemyOwner:

            # Holding attack starts charging instead of immediately swinging.
            if pygame.mouse.get_pressed()[0] and self.CanSwing() and not self.Charging:
                self.Charging = True
                self.ChargeDuration = 0

            if self.Charging:

                # Increases damage while the button is held.
                self.ChargeDuration += dt

                # Releasing the button performs the charged attack.
                if not pygame.mouse.get_pressed()[0]:

                    self.damage = int(
                        20 +
                        80 * min(
                            self.ChargeDuration / self.MaxChargeTime,
                            1
                        )
                    )

                    self.Swing(
                        self.pos,
                        self.Targetpos
                    )

                    self.Charging = False

        self.UpdateMask()


    def ResolveCollision(self, obj, damage):

        # Applies knockback if the target supports it.
        if hasattr(obj, "Knockback"):

            # More charge creates stronger knockback.
            strength = min(
                self.ChargeDuration / self.MaxChargeTime,
                1
            )

            obj.Knockback(
                self.pos,
                speed=10 + strength*25,
                duration=0.2 + strength*0.3,
                stunTime=0.2 + strength*0.5
            )

        super().ResolveCollision(obj, damage)


class ReturnToSender(RegularSword):
    def __init__(self, size, Name, Targetpos, position, Enemy):
        super().__init__(size, Name, Targetpos, position, Enemy)

        # Lower damage sword focused on reflecting attacks.
        self.damage = 20

    def ResolveParryCollision(self, obj):

        # Returns damage back to the attacker.
        if hasattr(obj, "TakeDamage"):
            obj.TakeDamage(obj.damage*2)

        # Stuns the enemy after a successful parry.
        if hasattr(obj, "SelfStun"):
            obj.SelfStun(1)



class ShielderSword(RegularSword):
    def __init__(self, size, Name, Targetpos, position, Enemy):
        super().__init__(size, Name, Targetpos, position, Enemy)

        # Tracks successful parries before granting a shield.
        self.successful_parries = 0
        self.damage = 15

    def ResolveParryCollision(self, obj):

        self.successful_parries += 1

        # Parried enemies are temporarily stunned.
        if hasattr(obj, "SelfStun"):
            obj.SelfStun(2)

        # After three successful parries, grant a shield.
        if self.successful_parries >= 3:

            if hasattr(self.EnemyOwner, "shield"):
                self.EnemyOwner.shield += (
                    self.EnemyOwner.Maxhealth * 0.2
                )

            self.successful_parries = 0



class HeavyHitter(RegularSword):
    def __init__(self, size, Name, Targetpos, position, Enemy):
        super().__init__(size, Name, Targetpos, position, Enemy)

        # Trades attack speed for stronger attacks.
        self.damage = 50
        self.CoolDownDuration = 1.5



# Automatically creates a dictionary containing every sword subclass.
# This allows weapons to be selected by name without manually adding each one.
WhichSword = {
    cls.__name__: cls
    for cls in RegularSword.__subclasses__()
}

# Adds the base sword class manually because it is not a subclass.
WhichSword["RegularSword"] = RegularSword