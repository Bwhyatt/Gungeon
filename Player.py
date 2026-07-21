
import pygame
import Gun
import Sword
from SpriteSheetLoader import LoadSpriteSheet
class Realplayer:
    def __init__(self, speed, size, pos, health, GivenGun, GivenSword):
       self.GivenGun = GivenGun
       self.GivenSword = GivenSword
       ChosenSword = Sword.WhichSword[GivenSword]
       ChosenGun = Gun.WhichGun[GivenGun]
       self.speed = speed
       self.size = pygame.Vector2(size)
       self.pos = pygame.Vector2(pos)
       self.Rect = pygame.Rect( self.pos.x, self.pos.y, self.size[0], self.size[1])
       self.alive = True
       self.Maxhealth = health
       self.health = self.Maxhealth
       self.gun = ChosenGun(Gun.GunSizes.get(GivenGun, (50, 20)), GivenGun, pygame.mouse.get_pos(), self.pos, False)
       self.Sword = ChosenSword((40, 40), GivenSword, pygame.mouse.get_pos(), self.pos, False)
       self.inventory = []
       self.BannedDirections = []
       self.tag = "Player"
       self.animations = {
        "idle": LoadSpriteSheet(
            "SpriteSheets/Player/Idle.png",
            16,
            32
        ),

        "walk_up": LoadSpriteSheet(
            "SpriteSheets/Player/UpWalk.png",
            16,
            32
        ),

        "walk_side": LoadSpriteSheet(
            "SpriteSheets/Player/SideWalk.png",
            16,
            32
        )
        }

       self.current_animation = "idle"
       self.frame_index = 0
       self.animation_timer = 0

       self.last_direction = "right"
       self.moving = False
       self.dead = False
       self.weapon_mode = "gun"
    def SwapWeapon(self):
        if self.weapon_mode == "gun":
            self.weapon_mode = "sword"
        else:
            self.weapon_mode = "gun"
    def update(self, screen, keys, dt, mousepos):#Every frame handles movement and animations
        if self.health <= 0:
            self.kill()
            return
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0

        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1
        if dx != 0 or dy != 0:#determines the direction the player is running in
            self.moving = True
            if dx != 0:
                self.last_direction = "left" if dx < 0 else "right"

            elif dy < 0:
                self.last_direction = "up"
        else:
            self.moving = False
        self.move(keys, dt, self.speed)
        if not self.moving:
            if(self.current_animation != "idle"):
                self.frame_index = 0
            self.current_animation = "idle"

        elif self.last_direction == "up":
            if(self.current_animation != "walk_up"):
                self.frame_index = 0
            self.current_animation = "walk_up"


        elif self.last_direction in ["left", "right"]:
            self.current_animation = "walk_side"
            if(self.current_animation != "walk_side"):
                self.frame_index = 0
        self.animation_timer += 1
        if self.animation_timer > 8:#every 8th frame this will change
            self.frame_index += 1
            self.animation_timer = 0
        if keys[pygame.K_v]:
            if not hasattr(self, "v_pressed"):
                self.v_pressed = False

            if not self.v_pressed:
                self.SwapWeapon()

            self.v_pressed = True
        else:
            self.v_pressed = False
            if self.frame_index >= len(self.animations[self.current_animation]):
                self.frame_index = 0
        #for now keys will be passed in
        self.Rect = pygame.Rect( self.pos.x, self.pos.y, self.size[0], self.size[1])
    def draw(self, screen, camera):# will put the current animation frame of the player on the screen
        self.image = self.animations[self.current_animation][int(self.frame_index)]

        if self.last_direction == "left":
            self.image = pygame.transform.flip(self.image, True, False)
        if hasattr(self, "image"):
            screen.blit(self.image, camera.apply(self.Rect.topleft))
        else:
            pygame.draw.rect(screen, (0,255,0), camera.apply(self.Rect)
            )
    def move(self, keys, dt, speed):
        if keys[pygame.K_w]:
            self.pos.y -= speed * dt
        if keys[pygame.K_s]:
            self.pos.y += speed * dt
        if keys[pygame.K_a]:
            self.pos.x -= speed * dt
        if keys[pygame.K_d]:
            self.pos.x += speed * dt
        #size, shape, speed, mousepos, position
        #bullet angle is tan (y component on x component)
        #x position of bullet is incremented speed multiplied by cos component
    def kill(self):
        self.dead = True
        print("Game Over")
    def TakeDamage(self, damage):#Self explanitory
        self.health -= damage
    def Regen(self, healing):
        self.health += healing
    #wall collision