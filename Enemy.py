import pygame
import Gun
import Sword
import math
import Wall
import SpriteSheetLoader
import DamageTexts
class BaseEnemy:#Use generalisation to make a bunch of different enemies that are the same but with a different gun
    def __init__(self, health, speed, position, size, WhichGun, WhichSword):
        #with the which gun do the same as what happened in player class
        self.health = health
        self.speed = speed
        self.pos = pygame.Vector2(position)
        self.size = pygame.Vector2(size)
        self.Rect = pygame.Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
        self.stunned = False
        self.stunTime = 0
        self.bulletList = []
        self.UsesGun = True if WhichGun != "None" else False
        self.UsesSword = True if WhichSword != "None" else False
        if(self.UsesGun):
            ChosenGun = Gun.WhichGun[WhichGun]
            self.gun = ChosenGun((50, 20), WhichGun, pygame.mouse.get_pos(), self.pos, True)
        if(self.UsesSword):
            ChosenSword = Sword.WhichSword[WhichSword]
            self.Sword = ChosenSword((100, 100), WhichSword, pygame.mouse.get_pos(), self.pos, True)
        self.CanMove = True
        self.AttackCoolDown = 5
        self.AttackCoolDownTimer = self.AttackCoolDown
        self.AttackDuration = 2
        self.ParryRect = None
        self.tag = "Enemy"
        self.Parryable = False
        self.dir = pygame.Vector2(0, 0)
        self.facing_direction = "down"
        self.BannedDirections = []
        self.KnockedBack = False
        self.KnockbackTimer = 0
        self.KnockbackDuration = 0
        self.KnockbackDirection = pygame.Vector2(0, 0)
        self.KnockbackSpeed = 0
        self.damage = 20
        self.animations = {
        "walk_up": SpriteSheetLoader.LoadSpriteSheet(
            "SpriteSheets/BaseEnemy/UpWalk.png",
            32,
            32
        ),

        "walk_down": SpriteSheetLoader.LoadSpriteSheet(
            "SpriteSheets/BaseEnemy/DownWalk.png",
            32,
            32
        ),

        "walk_side": SpriteSheetLoader.LoadSpriteSheet(
            "SpriteSheets/BaseEnemy/SideWalk.png",
            32,
            32
        )
    }   
        self.current_animation = "walk_down"
        self.frame_index = 0
        self.animation_timer = 0
        self.frame_duration = 0.15

        self.flip = False
        self.AnimationFinished = False
        self.IsAttacking = False
        self.dead = False
        self.melee_resistance = 1
        self.gun_resistance = 1
        self.damage_texts = []
    def Collision(self, obj2):#iterate through each of the player's bullets
        if(self.Rect.colliderect(obj2.Rect)):
            return True
        return False
    def TakeHit(self, damage, damage_type):
        multiplier = 1
        if damage_type == "melee":
            multiplier = self.melee_resistance
        elif damage_type == "gun":
            multiplier = self.gun_resistance
        if multiplier < 1:
            self.damage_texts.append(
                DamageTexts.DamageText("Resistant", self.pos)
            )

        if multiplier > 1:
            self.damage_texts.append(
                DamageTexts.DamageText("Weak", self.pos)
            )

        self.TakeDamage(damage * multiplier)
    def ResolveCollision(self, obj2):
        #even though the only things to collide with are bullets and walls, 
        #this makes it modular and is better practice
        #TBD
        if obj2.tag == "Bullet":
            self.TakeHit(obj2.damage, "gun")

        elif obj2.tag == "Sword":
            self.TakeHit(obj2.damage, "melee")
    def SelfStun(self, time):
        print("Stunned")
        self.stunTime = time
        self.stunned = True
    def Attack(self, dt, player_pos, selfpos):
        pass
    def Move(self, dt, player_pos, speed):

        direction = pygame.Vector2(player_pos) - self.pos

        if direction.length() > 0:
            direction = direction.normalize()
        Xamt = direction.x * speed * dt
        Yamt = direction.y * speed * dt

        # Animation direction
        if abs(direction.x) > abs(direction.y):

            if direction.x > 0:
                self.facing_direction = "right"
                self.flip = False
            else:
                self.facing_direction = "left"
                self.flip = True

        else:

            if direction.y > 0:
                self.facing_direction = "down"

            else:
                self.facing_direction = "up"


        self.pos += pygame.Vector2(Xamt, Yamt)
    def TakeDamage(self, damage):
        print("I took damage")
        self.health -= damage
    def Knockback(self, HitterPos, speed, duration, stunTime=0):
        direction = self.pos - pygame.Vector2(HitterPos)

        self.KnockedBack = True
        self.KnockbackDirection = direction
        self.KnockbackSpeed = speed
        self.KnockbackDuration = duration
        self.KnockbackTimer = duration

        self.SelfStun(stunTime)
    def kill(self):
        self.dead = True
    def CanAttacK(self, player_pos):
        pass #This will check if there is nothin obstructing the enemy like a wall, if it is out of range or if the attack is on cooldown for melee attacks
    def Die(self):
        print("Enemy died")
        self.dead = True
    def draw(self, screen, camera):
        #print(self.current_animation, self.frame_index, len(self.animations[self.current_animation]))
        image = self.animations[self.current_animation][self.frame_index]
        if(self.current_animation):
            image = self.animations[self.current_animation][self.frame_index]

        if self.flip:
            image = pygame.transform.flip(image, True, False)

        screen.blit(
            image,
            camera.apply(self.Rect)
        )
    def DetermineAction(self, dt, player_pos, ):
            if(self.CanMove):
                self.Move(dt, player_pos, self.speed)
    def GetAnimation(self):
        return None
    def UpdateAnimation(self, dt):
        self.AnimationFinished = False
        special = self.GetAnimation()
        if special is not None:
            new_animation = special
        elif self.facing_direction == "up":
            new_animation = "walk_up"
        elif self.facing_direction == "down":
            new_animation = "walk_down"
        else:
            new_animation = "walk_side"
        

        # Reset animation when changing
        if new_animation != self.current_animation:
            self.current_animation = new_animation
            self.frame_index = 0
            self.animation_timer = 0
            #print("Changed to ", new_animation)
        self.animation_timer += dt

        if self.animation_timer >= self.frame_duration:
            self.animation_timer = 0
            self.frame_index += 1

            if self.frame_index >= len(self.animations[self.current_animation]):
                self.AnimationFinished = True

                if self.current_animation == "ShellEnter":
                    self.frame_index = len(self.animations[self.current_animation]) - 1
                else:
                    self.frame_index = 0    
    def update(self, dt, player_pos, playerbulletlist, screen):
        for text in self.damage_texts[:]:
                text.update(dt)
                if text.timer >= text.duration:
                    self.damage_texts.remove(text)
        if self.health <= 0:
            self.Die()

        self.AttackDuration -= dt
        self.AttackCoolDownTimer -= dt
        for i in range(len(playerbulletlist)):
            if(self.Collision(playerbulletlist[i])):
                self.ResolveCollision(playerbulletlist[i])
         #make sure this happens after all the bullets update   
        if self.health <= 0:
            self.Die()
        if(self.stunned):
            self.stunTime -= dt
            if(self.stunTime <= 0):
                self.stunned = False
        if self.KnockedBack:
            self.pos += self.KnockbackDirection * self.KnockbackSpeed * dt
            self.KnockbackTimer -= dt
            if self.KnockbackTimer <= 0:
                self.KnockedBack = False    
        if(not self.stunned and not self.KnockedBack):
            self.DetermineAction(dt, player_pos)
        #run other functions
        if(self.UsesGun):
            self.bulletList = [b for b in self.bulletList if not getattr(b, "dead", False)]
        self.Rect = pygame.Rect( self.pos.x, self.pos.y, self.size[0], self.size[1])
        self.UpdateAnimation(dt)
        

class Bowler(BaseEnemy):
    def __init__(self, health, speed, position, size, WhichGun, WhichSword):
        super().__init__(health,speed, position, size, WhichGun, WhichSword)
        self.pos = position
        self.AttackDuration = 2
        self.IsAttacking = False
        self.LaunchSpeed = 600
        self.ParryRect = pygame.Rect(self.pos[0] - self.size[0], self.pos[1] - self.size[1], self.size[0] * 2, self.size[1] * 2)
        self.launchTarget = (0,0)
        self.Parryable = True
        self.IsEnteringShell = False
        self.ShellEnterFinished = False
        self.animations["ShellEnter"] = SpriteSheetLoader.LoadSpriteSheet(
            "SpriteSheets/Bowler/ShellEnter.png",
            32,
            32
        )

        self.animations["Turtle_Spin"] = SpriteSheetLoader.LoadSpriteSheet(
            "SpriteSheets/Bowler/Turtle_Spin.png",
            32,
            32
        )
        print(SpriteSheetLoader.LoadSpriteSheet(
            "SpriteSheets/Bowler/Turtle_Spin.png",
            32,
            32
        ))
        self.IsEnteringShell = False
    def determinedir(self, Targetpos):
        angle = math.atan2(Targetpos.y - self.pos.y, Targetpos.x - self.pos.x)
        return angle
        #self.pos += pygame.Vector2(math.cos(angle) * LaunchSpeed * dt, math.sin(angle)* dt * LaunchSpeed)
    def GetAnimation(self):

        # print(
        #     self.IsEnteringShell,
        #     self.IsAttacking
        # )
        if self.IsEnteringShell:
            return "ShellEnter"

        if self.IsAttacking:
            return "Turtle_Spin"

        return None
    def Attack(self, player_pos):
        print("attacking")
        self.IsEnteringShell = True
        self.IsAttacking = False
        self.IsEnteringShell = True
        self.IsAttacking = False
        self.CanMove = False
        self.AttackDuration = 2
        self.AttackCoolDownTimer = self.AttackCoolDown
        self.angle = self.determinedir(player_pos)
        self.angleTargetPos = pygame.Vector2(player_pos)
        self.launchTarget = pygame.Vector2(player_pos)
        self.current_animation = "Turtle_Spin"
    def HasOverShot(self):
        if self.launchTarget == (0, 0):#(0,0) is a magic number and is just a placeholder position
            return False
        direction = pygame.Vector2(math.cos(self.angle), math.sin(self.angle))
        ToTarget = self.launchTarget - self.pos
        return ToTarget.dot(direction) < 0 # dot product will be negative if 
    def ResolveCollision(self, obj2):
        if(obj2.tag != "Wall" and obj2.tag != "Door" and obj2.tag != "Bullet"):
            obj2.TakeDamage(self.damage)
            self.kill()
            return
        if(obj2.tag == "Door"):
            self.kill()
            return
        if(obj2.tag == "Wall"):
            obj2.WallCollision(self)
            if( 1 in self.BannedDirections or  3 in self.BannedDirections):
                self.angle *= -1
            if(2 in self.BannedDirections  or 4 in self.BannedDirections ):
                self.IsAttacking = False
                self.CanMove = True
                self.AttackCoolDownTimer = self.AttackCoolDown
                return
        super().ResolveCollision(obj2)
    def DetermineAction(self, dt, player_pos):
        if self.CanMove:
            self.Move(dt, player_pos, self.speed)

        # Start attack
        if (self.CanMove and not self.IsAttacking and not self.IsEnteringShell and self.AttackDuration <= 0 and self.AttackCoolDownTimer <= 0):
            self.angle = self.determinedir(player_pos)
            self.Attack(player_pos)

        # Wait for shell animation to finish
        elif self.IsEnteringShell:

            if self.AnimationFinished:   # or your own finish check
                self.IsEnteringShell = False
                self.IsAttacking = True
                

        # Spin attack
        elif self.IsAttacking:

            self.pos += pygame.Vector2(
                math.cos(self.angle) * self.LaunchSpeed * dt,
                math.sin(self.angle) * self.LaunchSpeed * dt
            )

            if self.HasOverShot() or self.AttackDuration <= 0:
                self.IsAttacking = False
                self.CanMove = True
                self.AttackCoolDownTimer = self.AttackCoolDown
            print(self.current_animation)
            print(self.frame_index)
class Sheller(Bowler):
    def __init__(self, health,speed, position, size, WhichGun, WhichSword):
        super().__init__(health,speed, position, size, WhichGun, WhichSword)
        self.OverShootLimit = 2
        self.OverShootCount = 0
        self.pos = position
        self.AttackDuration = 3.5
        self.IsAttacking = False
        self.LaunchSpeed = 300
        self.ParryRect = None
        self.launchTarget = (0,0)
        self.BufferTimeLen = 0.5
        self.BufferTime = self.BufferTimeLen
        self.enablebuffertime = False
    def DetermineAction(self, dt, player_pos):
        if(self.enablebuffertime):
            self.BufferTime -= dt #after it has overshot this delays it running again
        #print(self.AttackDuration)
        if(self.IsAttacking):
            self.Parryable = True
            self.ParryRect = pygame.Rect(self.pos[0] - self.size[0], self.pos[1] - self.size[1], self.size[0] * 2, self.size[1] * 2)
        else:
            self.Parryable = False
            self.ParryRect = None
        if(not self.stunned):
            if(self.CanMove):
                self.Move(dt, player_pos, self.speed)
            if(self.CanMove and not self.IsAttacking and not self.IsEnteringShell and self.AttackDuration <= 0 and self.AttackCoolDownTimer <= 0):
                self.Attack(player_pos)
            elif(self.IsEnteringShell):
                if(self.AnimationFinished):
                    self.IsEnteringShell = False
                    self.IsAttacking = True
            elif(not self.CanMove and self.IsAttacking):
                self.pos += pygame.Vector2(math.cos(self.angle) * self.LaunchSpeed * dt, math.sin(self.angle)* dt * self.LaunchSpeed)
                if self.HasOverShot() and self.AttackDuration > 0 and self.OverShootCount < self.OverShootLimit:
                    self.enablebuffertime = True
                    if(self.BufferTime <= 0):
                        self.Attack(player_pos)
                        self.OverShootCount +=1
                        self.AttackDuration += self.BufferTimeLen
                        self.BufferTime = self.BufferTimeLen
                if self.AttackDuration <= 0:#Or collides with wall
                    self.IsAttacking = False
                    self.CanMove = True
                    self.AttackCoolDownTimer = self.AttackCoolDown
                    self.OverShootCount = 0
                    self.BufferTime = self.BufferTimeLen
class PinBaller(Bowler):
    def __init__(self, health,speed, position, size, WhichGun, WhichSword):
        super().__init__(health,speed, position, size, WhichGun, WhichSword)
        self.OverShootLimit = 2
        self.OverShootCount = 0
        self.pos = position
        self.AttackDuration = 4
        self.IsAttacking = False
        self.IsEnteringShell = False
        self.LaunchSpeed = 200
        self.ParryRect = None
        self.launchTarget = (0,0)
        self.BufferTimeLen = 0.5
        self.BufferTime = self.BufferTimeLen
        self.enablebuffertime = False
    def ResolveCollision(self, obj2):
        if(obj2.tag != "Wall" and obj2.tag != "Door" and obj2.tag != "Bullet"):
            obj2.TakeDamage(self.damage)
            self.kill()
        if(obj2.tag == "Door"):
            self.kill()
            return
        if(obj2.tag == "Wall"):
            obj2.WallCollision(self)
            if(self.IsAttacking):
                if( 1 in self.BannedDirections or  3 in self.BannedDirections):
                    self.angle *= -1
                if(2 in self.BannedDirections  or 4 in self.BannedDirections ):
                    self.angle += math.pi
                    self.angle *= -1
                    return
        if(obj2.tag == "Bullet"):
            self.TakeDamage(obj2.damage)
    def DetermineAction(self, dt, player_pos):
        if self.IsAttacking:
            self.Parryable = True
            self.ParryRect = pygame.Rect(
                self.pos[0] - self.size[0],
                self.pos[1] - self.size[1],
                self.size[0] * 2,
                self.size[1] * 2
            )
        else:
            self.Parryable = False
            self.ParryRect = None


        # Normal movement
        if self.CanMove:
            self.Move(dt, player_pos, self.speed)


        # Start attack
        if (
            self.CanMove
            and not self.IsAttacking
            and not self.IsEnteringShell
            and self.AttackDuration <= 0
            and self.AttackCoolDownTimer <= 0
        ):
            self.Attack(player_pos)


        # Wait for shell animation
        elif self.IsEnteringShell:

            if self.AnimationFinished:
                self.IsEnteringShell = False
                self.IsAttacking = True
        # Spin movement
        elif self.IsAttacking:

            self.pos += pygame.Vector2(
                math.cos(self.angle) * self.LaunchSpeed * dt,
                math.sin(self.angle) * self.LaunchSpeed * dt
            )
            if self.AttackDuration <= 0:
                self.IsAttacking = False
                self.CanMove = True
                self.AttackCoolDownTimer = self.AttackCoolDown
class Shielder(BaseEnemy):
    def __init__(self, health, speed, position, size, WhichGun, WhichSword):
        super().__init__(health, speed, position, size, WhichGun, WhichSword)
        #shield stuff
        self.ShieldDirection = pygame.Vector2(0,0)
        self.ShieldActive = True
        self.ShieldBroken = False
        #sword stuff
        #attack stuff
        self.AttackCoolDown = 3
        self.AttackCoolDownTimer = self.AttackCoolDown
        self.AttackDuration = 1
        self.IsAttacking = False
        self.damage = 40
        self.Parryable = True
        self.animations = {
            "walk_up": SpriteSheetLoader.LoadSpriteSheet(
            "SpriteSheets/Shielder/UpWalk.png",
            64,
            64
        ),
        "walk_down": SpriteSheetLoader.LoadSpriteSheet(
            "SpriteSheets/Shielder/DownWalk.png",
            64,
            64
        ),
        "walk_side": SpriteSheetLoader.LoadSpriteSheet(
            "SpriteSheets/Shielder/RightWalk.png",
            64,
            64
        )
        }
    # BaseEnemy.__init__ — add
        self.dead = False
        self.BlockedDirections = {
            "up": "down", "down": "up", "left": "right", "right": "left"
        }  # bullet arriving FROM this direction gets blocked, when facing the paired direction

    def GetBulletDirection(self, velocity):
        if abs(velocity.x) > abs(velocity.y):
            return "left" if velocity.x > 0 else "right"  # bullet moving right = coming FROM the left
        else:
            return "up" if velocity.y > 0 else "down"

    def IsBulletBlocked(self, bullet):
        if self.stunned:
            return False
        velocity = pygame.Vector2(math.cos(bullet.acute_rad), math.sin(bullet.acute_rad))
        incoming_from = self.GetBulletDirection(velocity)
        return incoming_from == self.BlockedDirections[self.facing_direction]

    def ResolveCollision(self, obj2):
        if obj2.tag == "Bullet":
            if self.IsBulletBlocked(obj2.velocity):
                return  # no damage, bullet unaffected here — Bullet.py must handle its own removal
            if self.stunned:
                self.TakeDamage(obj2.damage)
    def FacePlayer(self, player_pos):
        self.ShieldDirection = pygame.Vector2(player_pos) - self.pos
        if(self.ShieldDirection.length() > 0):
            self.ShieldDirection = self.ShieldDirection.normalize()

    def TakeDirectionalDamage(self, damage, hitPosition):
        if(self.ShieldActive and not self.ShieldBroken):
            HitDirection = pygame.Vector2(hitPosition) - self.pos
            if(HitDirection.length() > 0):
                HitDirection = HitDirection.normalize()
            if(HitDirection.dot(self.ShieldDirection) > 0.5):
                print("Blocked by shield")
                return
        self.health -= damage

    def SelfStun(self, time):
        super().SelfStun(time)
        self.ShieldBroken = True

    def Attack(self, player_pos):
        self.IsAttacking = True
        self.CanMove = False
        self.AttackDuration = 1
        if(self.Sword != None):
            self.Sword.Swing(self.pos)

    def DetermineAction(self, dt, player_pos):
        self.FacePlayer(player_pos)
        if(self.CanMove):
            self.Move(dt, player_pos, self.speed)
        if(self.CanMove and not self.IsAttacking and self.AttackDuration <= 0 and self.AttackCoolDownTimer <= 0):
            self.Attack(player_pos)
        elif(not self.CanMove and self.IsAttacking):
            if(self.Sword != None):
                pass
            if(self.AttackDuration <= 0):
                self.IsAttacking = False
                self.CanMove = True
                self.AttackCoolDownTimer = self.AttackCoolDown

    def update(self, dt, player_pos, playerbulletlist, screen):
        super().update(dt, player_pos, playerbulletlist, screen)
        
        if(self.Sword != None):
            self.Sword.update(dt, screen, None, self.pos, player_pos)
        if(not self.stunned):
            self.ShieldBroken = False
class MeleeSlime(BaseEnemy):
    def __init__(self, health, speed, position, size, WhichGun, WhichSword):
        super().__init__(health, speed, position, size, WhichGun, WhichSword)

        self.damage = 20
        self.AttackCoolDown = 1
        self.AttackCoolDownTimer = self.AttackCoolDown
        self.AttackDuration = 0
        self.tag = "Enemy"

        # melee slime stats
        self.melee_resistance = 1
        self.gun_resistance = 2

        self.ContactDamageCooldown = 1
        self.ContactDamageTimer = 0


    def DetermineAction(self, dt, player_pos):
        if not self.stunned:
            self.Move(dt, player_pos, self.speed)


    def update(self, dt, player_pos, playerbulletlist, screen, player=None):

        super().update(dt, player_pos, playerbulletlist, screen)

        self.ContactDamageTimer -= dt

        if player is not None:
            if self.Collision(player):
                if self.ContactDamageTimer <= 0:
                    player.TakeDamage(self.damage)
                    self.ContactDamageTimer = self.ContactDamageCooldown


    def ResolveCollision(self, obj2):
        super().ResolveCollision(obj2)
class GunSlime(MeleeSlime):
    def __init__(self, health, speed, position, size, WhichGun, WhichSword):
        super().__init__(health, speed, position, size, WhichGun, WhichSword)

        # gun slime stats
        self.melee_resistance = 0
        self.gun_resistance = 2