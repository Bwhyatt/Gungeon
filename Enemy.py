import pygame
import Gun
import Sword
import math
import Wall
import SpriteSheetLoader
import DamageTexts

class BaseEnemy:#Use generalisation to make a bunch of different enemies that are the same but with a different gun
    def __init__(self, health, speed, position, size, WhichGun, WhichSword):
        # Stores the basic stats shared by every enemy type.
        self.health = health
        self.speed = speed

        # Position is stored as a Vector2 so movement calculations can use vector operations.
        self.pos = pygame.Vector2(position)

        # Size is used for collision and drawing scaling.
        self.size = pygame.Vector2(size)

        # Rectangle used for collision detection.
        self.Rect = pygame.Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)

        # Controls whether the enemy can currently act or move.
        self.stunned = False
        self.stunTime = 0

        # Stores bullets fired by the enemy's weapon.
        self.bulletList = []

        # Checks if the enemy has a gun or sword based on the values passed in.
        self.UsesGun = True if WhichGun != "None" else False
        self.UsesSword = True if WhichSword != "None" else False

        # Creates the correct weapon class from the weapon dictionaries.
        if(self.UsesGun):
            ChosenGun = Gun.WhichGun[WhichGun]
            self.gun = ChosenGun((20, 20), WhichGun, pygame.mouse.get_pos(), self.pos, True)

        if(self.UsesSword):
            ChosenSword = Sword.WhichSword[WhichSword]
            self.Sword = ChosenSword(getattr(self, "SwordSize", (100,100)),WhichSword,pygame.mouse.get_pos(),self.pos,True)

        # Movement and attack states.
        self.CanMove = True
        self.AttackCoolDown = 5
        self.AttackCoolDownTimer = self.AttackCoolDown
        self.AttackDuration = 2

        # Used for enemies that can block or interact with parries.
        self.ParryRect = None
        self.tag = "Enemy"
        self.Parryable = False

        # Stores movement direction and current animation facing direction.
        self.dir = pygame.Vector2(0, 0)
        self.facing_direction = "down"

        # Stores directions blocked by walls during certain attacks.
        self.BannedDirections = []

        # Knockback variables used when enemies are hit by heavy attacks.
        self.KnockedBack = False
        self.KnockbackTimer = 0
        self.KnockbackDuration = 0
        self.KnockbackDirection = pygame.Vector2(0, 0)
        self.KnockbackSpeed = 0

        # Base contact damage dealt by the enemy.
        self.damage = 20

        # Loads the default walking animations.
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

        # Animation tracking variables.
        self.current_animation = "walk_down"
        self.frame_index = 0
        self.animation_timer = 0
        self.frame_duration = 0.15

        self.flip = False
        self.AnimationFinished = False

        # Attack state variables.
        self.IsAttacking = False

        # Death state.
        self.dead = False

        # Damage resistance multipliers for different damage types.
        self.melee_resistance = 1
        self.gun_resistance = 1

        # Stores floating damage number objects.
        self.damage_texts = []
    def Collision(self, obj2):#iterate through each of the player's bullets
        # Checks if another object's collision rectangle overlaps with this enemy.
        if(self.Rect.colliderect(obj2.Rect)):
            return True
        return False

    def TakeHit(self, damage, damage_type):
        # Applies resistance depending on whether the damage came from a sword or gun.
        multiplier = 1

        if damage_type == "melee":
            multiplier = self.melee_resistance

        elif damage_type == "gun":
            multiplier = self.gun_resistance

        # Damage is divided by resistance so higher resistance reduces damage taken.
        self.TakeDamage(damage / multiplier)

    def ResolveCollision(self, obj2):
        # Handles what happens when the enemy collides with different object types.
        # This keeps collision behaviour inside the enemy rather than inside bullets/swords.

        if obj2.tag == "Bullet":
            self.TakeHit(obj2.damage, "gun")
            obj2.destroy()

        elif obj2.tag == "Sword":
            self.TakeHit(obj2.damage, "melee")

    def SelfStun(self, time):
        # Prevents the enemy from moving or attacking for a set amount of time.
        print("Stunned")
        self.stunTime = time
        self.stunned = True

    def Attack(self, dt, player_pos, selfpos):
        # Empty base method because different enemies have their own attack behaviour.
        pass

    def Move(self, dt, player_pos, speed):

        # Finds the direction from the enemy towards the player.
        direction = pygame.Vector2(player_pos) - self.pos

        # Normalising makes movement speed consistent regardless of distance.
        if direction.length() > 0:
            direction = direction.normalize()

        # Calculates movement amount using speed and delta time.
        Xamt = direction.x * speed * dt
        Yamt = direction.y * speed * dt

        # Updates the animation direction depending on the dominant movement axis.
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


        # Applies the calculated movement to the enemy position.
        self.pos += pygame.Vector2(Xamt, Yamt)
    def TakeDamage(self, damage):
        # Removes health from the enemy when damage is received.
        self.health -= damage

    def Knockback(self, HitterPos, speed, duration, stunTime=0):
        # Calculates the direction away from the object that hit the enemy.
        direction = self.pos - pygame.Vector2(HitterPos)

        # Stores knockback information so it can be applied over multiple frames.
        self.KnockedBack = True
        self.KnockbackDirection = direction
        self.KnockbackSpeed = speed
        self.KnockbackDuration = duration
        self.KnockbackTimer = duration

        # Applies stun alongside knockback.
        self.SelfStun(stunTime)

    def kill(self):
        # Marks the enemy as dead.
        self.dead = True

    def CanAttacK(self, player_pos):
        # Base method for enemies that need custom attack checks.
        # Child classes can override this with their own conditions.
        pass

    def Die(self):
        # Changes the enemy state to dead.
        self.dead = True

    def draw(self, screen, camera):
        # Gets the current animation frame to display.
        image = self.animations[self.current_animation][self.frame_index]

        # Flips the sprite horizontally when facing left.
        if self.flip:
            image = pygame.transform.flip(image, True, False)

        # Draws the enemy sprite using the camera offset.
        screen.blit(
            image,
            camera.apply(self.Rect)
        )

    def DetermineAction(self, dt, player_pos):
        # Base enemy behaviour is simply moving towards the player.
        # Specific enemies override this function for unique behaviour.
        if(self.CanMove):
            self.Move(dt, player_pos, self.speed)

    def GetAnimation(self):
        # Allows child classes to provide their own animation states.
        return None

    def UpdateAnimation(self, dt):
        # Resets the animation completion flag every frame.
        self.AnimationFinished = False

        # Allows child classes to override the current animation.
        special = self.GetAnimation()

        if special is not None:
            new_animation = special

        # Uses movement direction to select the correct walking animation.
        elif "walk_down" in self.animations:
            if self.facing_direction == "up":
                new_animation = "walk_up"
            elif self.facing_direction == "down":
                new_animation = "walk_down"
            else:
                new_animation = "walk_side"

        else:
            # Enemies with only one animation always use that animation.
            new_animation = list(self.animations.keys())[0]


        # Resets the animation if the animation type changes.
        if new_animation != self.current_animation:
            self.current_animation = new_animation
            self.frame_index = 0
            self.animation_timer = 0


        # Tracks how long the current frame has been displayed.
        self.animation_timer += dt

        # Moves to the next frame when enough time has passed.
        if self.animation_timer >= self.frame_duration:
            self.animation_timer = 0
            self.frame_index += 1

            # Loops the animation once the final frame is reached.
            if self.frame_index >= len(self.animations[self.current_animation]):
                self.AnimationFinished = True
                self.frame_index = 0
        

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

                # Keeps special animations such as entering shells on their final frame.
                if self.current_animation == "ShellEnter":
                    self.frame_index = len(self.animations[self.current_animation]) - 1
                else:
                    self.frame_index = 0
    def update(self, dt, player_pos, playerbulletlist, screen, player=None):

        # Updates all floating damage numbers and removes expired ones.
        for text in self.damage_texts[:]:
                text.update(dt)
                if text.timer >= text.duration:
                    self.damage_texts.remove(text)

        # Checks if the enemy has no health left.
        if self.health <= 0:
            self.Die()

        # Reduces attack timers every frame.
        self.AttackDuration -= dt
        self.AttackCoolDownTimer -= dt

        # Checks collision with all player bullets.
        for i in range(len(playerbulletlist)):
            if(self.Collision(playerbulletlist[i])):
                self.ResolveCollision(playerbulletlist[i])

        # Checks death again after taking bullet damage.
        # This makes sure the enemy dies immediately after being hit.
        if self.health <= 0:
            self.Die()

        # Handles stun duration.
        if(self.stunned):
            self.stunTime -= dt

            if(self.stunTime <= 0):
                self.stunned = False

        # Applies knockback movement while the enemy is being pushed.
        if self.KnockedBack:
            self.pos += self.KnockbackDirection * self.KnockbackSpeed * dt
            self.KnockbackTimer -= dt

            if self.KnockbackTimer <= 0:
                self.KnockedBack = False    

        # Allows normal enemy behaviour only if not stunned or knocked back.
        if(not self.stunned and not self.KnockedBack):
            self.DetermineAction(dt, player_pos)

        # Removes bullets that are no longer active.
        if(self.UsesGun):
            self.bulletList = [b for b in self.bulletList if not getattr(b, "dead", False)]

        # Updates collision rectangle position after movement.
        self.Rect = pygame.Rect(
            self.pos.x,
            self.pos.y,
            self.size[0],
            self.size[1]
        )

        # Updates the current animation frame.
        self.UpdateAnimation(dt)
        

class Bowler(BaseEnemy):
    def __init__(self, health, speed, position, size, WhichGun, WhichSword):
        # Creates the normal enemy properties first.
        super().__init__(health,speed, position, size, WhichGun, WhichSword)

        self.pos = position

        # Controls the timing and behaviour of the rolling attack.
        self.AttackDuration = 2
        self.IsAttacking = False
        self.LaunchSpeed = 600

        # Area around the enemy used for parry detection.
        self.ParryRect = pygame.Rect(
            self.pos[0] - self.size[0],
            self.pos[1] - self.size[1],
            self.size[0] * 2,
            self.size[1] * 2
        )

        # Position the enemy is currently charging towards.
        self.launchTarget = (0,0)

        # Allows this enemy's attack to be parried.
        self.Parryable = True

        # Controls the shell entering animation before attacking.
        self.IsEnteringShell = False
        self.ShellEnterFinished = False

        # Adds attack-specific animations.
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

        self.IsEnteringShell = False
    def update(self, dt, player_pos, playerbulletlist, screen, player):
        # Checks collision with the player during the rolling attack.
        if self.IsAttacking and player is not None:
            if self.Collision(player):
                self.ResolveCollision(player)

        # Runs the normal enemy update process.
        return super().update(
            dt,
            player_pos,
            playerbulletlist,
            screen,
            player
        )

    def determinedir(self, Targetpos):
        # Calculates the angle from the enemy towards the target position.
        angle = math.atan2(Targetpos.y - self.pos.y, Targetpos.x - self.pos.x)
        return angle

    def GetAnimation(self):

        # Uses special animations while entering the shell or attacking.
        if self.IsEnteringShell:
            return "ShellEnter"

        if self.IsAttacking:
            return "Turtle_Spin"

        # Uses normal walking animation otherwise.
        return None

    def Attack(self, player_pos):
        # Starts the shell transformation before the rolling attack.
        print("attacking")
        self.IsEnteringShell = True
        self.IsAttacking = False
        self.IsEnteringShell = True
        self.IsAttacking = False

        # Stops normal movement while preparing the attack.
        self.CanMove = False

        # Resets attack timers.
        self.AttackDuration = 2
        self.AttackCoolDownTimer = self.AttackCoolDown

        # Stores the direction and target of the charge.
        self.angle = self.determinedir(player_pos)
        self.angleTargetPos = pygame.Vector2(player_pos)
        self.launchTarget = pygame.Vector2(player_pos)

        # Changes animation immediately to the spinning state.
        self.current_animation = "Turtle_Spin"

    def HasOverShot(self):
        # Checks if the enemy has travelled past its original target.
        if self.launchTarget == (0, 0):#(0,0) is a magic number and is just a placeholder position
            return False

        direction = pygame.Vector2(
            math.cos(self.angle),
            math.sin(self.angle)
        )

        ToTarget = self.launchTarget - self.pos

        # A negative dot product means the enemy has passed the target.
        return ToTarget.dot(direction) < 0

    def ResolveCollision(self, obj2):
        # Handles collisions specific to the Bowler attack.

        if(obj2.tag == "Player"):
            # Deals contact damage during the charge.
            obj2.TakeDamage(self.damage)
            return

        if(obj2.tag == "Door"):
            # Removes itself if it hits a door.
            self.kill()
            return

        if(obj2.tag == "Wall"):
            # Lets the wall handle collision response.
            obj2.WallCollision(self)

            # Reflects the charge when hitting horizontal walls.
            if(1 in self.BannedDirections or 3 in self.BannedDirections):
                self.angle *= -1

            # Stops attacking when hitting vertical walls.
            if(2 in self.BannedDirections or 4 in self.BannedDirections):
                self.IsAttacking = False
                self.CanMove = True
                self.AttackCoolDownTimer = self.AttackCoolDown
                return

        # Uses the normal enemy collision behaviour for everything else.
        super().ResolveCollision(obj2)

    def DetermineAction(self, dt, player_pos):

        # Allows normal movement when not attacking.
        if self.CanMove:
            self.Move(dt, player_pos, self.speed)

        # Starts attack when cooldowns are complete.
        if (
            self.CanMove
            and not self.IsAttacking
            and not self.IsEnteringShell
            and self.AttackDuration <= 0
            and self.AttackCoolDownTimer <= 0
        ):
            self.angle = self.determinedir(player_pos)
            self.Attack(player_pos)

        # Waits until the shell animation finishes.
        elif self.IsEnteringShell:

            if self.AnimationFinished:
                self.IsEnteringShell = False
                self.IsAttacking = True
                

        # Moves quickly towards the player during the rolling attack.
        elif self.IsAttacking:

            self.pos += pygame.Vector2(
                math.cos(self.angle) * self.LaunchSpeed * dt,
                math.sin(self.angle) * self.LaunchSpeed * dt
            )

            # Ends the attack after passing the target or running out of time.
            if self.HasOverShot() or self.AttackDuration <= 0:
                self.IsAttacking = False
                self.CanMove = True
                self.AttackCoolDownTimer = self.AttackCoolDown


class Sheller(Bowler):
    def __init__(self, health,speed, position, size, WhichGun, WhichSword):
        # Uses the Bowler base behaviour but modifies the attack.
        super().__init__(health,speed, position, size, WhichGun, WhichSword)

        # Allows multiple charges before returning to normal.
        self.OverShootLimit = 2
        self.OverShootCount = 0

        self.pos = position
        self.AttackDuration = 3.5
        self.IsAttacking = False
        self.LaunchSpeed = 300

        # Sheller does not use the normal parry rectangle.
        self.ParryRect = None

        self.launchTarget = (0,0)

        # Adds a delay between repeated charges.
        self.BufferTimeLen = 0.5
        self.BufferTime = self.BufferTimeLen
        self.enablebuffertime = False
    def DetermineAction(self, dt, player_pos):

        # Controls the delay between repeated attacks after overshooting.
        if(self.enablebuffertime):
            self.BufferTime -= dt #after it has overshot this delays it running again

        # Makes the enemy parryable only while attacking.
        if(self.IsAttacking):
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

        if(not self.stunned):

            # Allows normal movement when not charging.
            if(self.CanMove):
                self.Move(dt, player_pos, self.speed)

            # Starts a new attack when cooldowns are complete.
            if(
                self.CanMove 
                and not self.IsAttacking 
                and not self.IsEnteringShell 
                and self.AttackDuration <= 0 
                and self.AttackCoolDownTimer <= 0
            ):
                self.Attack(player_pos)

            # Waits for the shell animation before moving.
            elif(self.IsEnteringShell):

                if(self.AnimationFinished):
                    self.IsEnteringShell = False
                    self.IsAttacking = True

            # Handles the rolling attack movement.
            elif(not self.CanMove and self.IsAttacking):

                self.pos += pygame.Vector2(
                    math.cos(self.angle) * self.LaunchSpeed * dt,
                    math.sin(self.angle) * self.LaunchSpeed
                )

                # Allows another charge if the enemy overshoots enough times.
                if self.HasOverShot() and self.AttackDuration > 0 and self.OverShootCount < self.OverShootLimit:

                    self.enablebuffertime = True

                    if(self.BufferTime <= 0):

                        self.Attack(player_pos)

                        self.OverShootCount +=1

                        # Extends the attack duration for another charge.
                        self.AttackDuration += self.BufferTimeLen

                        self.BufferTime = self.BufferTimeLen

                # Ends attack after duration expires.
                if self.AttackDuration <= 0:
                    self.IsAttacking = False
                    self.CanMove = True
                    self.AttackCoolDownTimer = self.AttackCoolDown
                    self.OverShootCount = 0
                    self.BufferTime = self.BufferTimeLen


class PinBaller(Bowler):
    def __init__(self, health,speed, position, size, WhichGun, WhichSword):

        # Uses Bowler's setup and modifies the attack behaviour.
        super().__init__(health,speed, position, size, WhichGun, WhichSword)

        self.OverShootLimit = 2
        self.OverShootCount = 0

        self.pos = position

        # Longer attack duration and slower movement than Bowler.
        self.AttackDuration = 4
        self.IsAttacking = False
        self.IsEnteringShell = False
        self.LaunchSpeed = 200

        self.ParryRect = None
        self.launchTarget = (0,0)

        # Delay used between repeated charges.
        self.BufferTimeLen = 0.5
        self.BufferTime = self.BufferTimeLen
        self.enablebuffertime = False

    def ResolveCollision(self, obj2):

        # Damages the player when hitting them during an attack.
        if(obj2.tag == "Player" and self.IsAttacking):
            obj2.TakeDamage(self.damage)

        # Removes itself when hitting a door.
        if(obj2.tag == "Door"):
            self.kill()
            return

        if(obj2.tag == "Wall"):

            # Lets the wall handle collision movement.
            obj2.WallCollision(self)

            # Changes direction when bouncing off walls.
            if(self.IsAttacking):

                if(1 in self.BannedDirections or 3 in self.BannedDirections):
                    self.angle *= -1

                if(2 in self.BannedDirections or 4 in self.BannedDirections):
                    self.angle += math.pi
                    self.angle *= -1
                    return

        # Bullets can damage the PinBaller directly.
        if(obj2.tag == "Bullet"):
            obj2.dead = True
            self.TakeDamage(obj2.damage)
    def DetermineAction(self, dt, player_pos):

        # Updates parry state depending on whether the enemy is attacking.
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


        # Normal movement when not attacking.
        if self.CanMove:
            self.Move(dt, player_pos, self.speed)


        # Starts the rolling attack when conditions are met.
        if (
            self.CanMove
            and not self.IsAttacking
            and not self.IsEnteringShell
            and self.AttackDuration <= 0
            and self.AttackCoolDownTimer <= 0
        ):
            self.Attack(player_pos)


        # Waits for shell animation before starting the attack.
        elif self.IsEnteringShell:

            if self.AnimationFinished:
                self.IsEnteringShell = False
                self.IsAttacking = True


        # Moves in the chosen direction while attacking.
        elif self.IsAttacking:

            self.pos += pygame.Vector2(
                math.cos(self.angle) * self.LaunchSpeed * dt,
                math.sin(self.angle) * self.LaunchSpeed * dt
            )

            # Ends attack after duration finishes.
            if self.AttackDuration <= 0:
                self.IsAttacking = False
                self.CanMove = True
                self.AttackCoolDownTimer = self.AttackCoolDown


class Shielder(BaseEnemy):
    def __init__(self, health, speed, position, size, WhichGun, WhichSword):

        # Loads all standard enemy properties.
        super().__init__(health, speed, position, size, WhichGun, WhichSword)
        if self.Sword:
            self.Sword.size = pygame.Vector2(150,150)
            self.Sword.OriginalImage = pygame.transform.scale(
                self.Sword.OriginalImage,
                self.Sword.size
            )
            self.Sword.PivotOnSprite = pygame.Vector2(
                self.Sword.size.x * 0.15,
                self.Sword.size.y / 2
            )

            # Shielder controls its own attack timing/telegraph in
            # DetermineAction/Attack, so stop the generic auto-swing.
            self.Sword.AutoSwing = False
        # Direction the shield is currently facing.
        self.ShieldDirection = pygame.Vector2(0,0)

        # Size of the sword used by this enemy.
        self.SwordSize = (150,150)

        # Shield state variables.
        self.ShieldActive = True
        self.ShieldBroken = False

        # Attack variables.
        self.AttackCoolDown = 3
        self.AttackCoolDownTimer = self.AttackCoolDown

        self.AttackDuration = 0
        self.IsAttacking = False

        # Controls the warning before the sword swing.
        self.PreparingAttack = False
        self.PrepareTimer = 0
        self.PrepareDuration = 1

        self.damage = 40

        # Allows this enemy to interact with parry mechanics.
        self.Parryable = True


        # Shielder has different sized sprites from BaseEnemy.
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


        # Stores which direction blocks incoming bullets.
        self.dead = False

        self.BlockedDirections = {
            "up": "down",
            "down": "up",
            "left": "right",
            "right": "left"
        }


    def draw(self, screen, camera):

        super().draw(screen, camera)

        # Shows a warning circle before the attack happens.
        if self.PreparingAttack:

            pygame.draw.circle(
                screen,
                "red",
                camera.apply(self.Rect).center,
                40,
                3
            )



    def GetBulletDirection(self, velocity):

        # Determines the direction a bullet is travelling from.
        if abs(velocity.x) > abs(velocity.y):

            return "left" if velocity.x > 0 else "right"

        else:

            return "up" if velocity.y > 0 else "down"



    def IsBulletBlocked(self, bullet):

        # Stunned enemies cannot block attacks.
        if self.stunned:
            return False


        # Converts the bullet angle into a movement direction.
        velocity = pygame.Vector2(
            math.cos(bullet.acute_rad),
            math.sin(bullet.acute_rad)
        )

        incoming_from = self.GetBulletDirection(velocity)


        # Checks whether the shield is facing the bullet.
        return incoming_from == self.BlockedDirections[self.facing_direction]
    
    def ResolveCollision(self, obj2):

        if obj2.tag == "Bullet":

            if self.IsBulletBlocked(obj2):
                return

            self.TakeDamage(obj2.damage)

    def FacePlayer(self, player_pos):

        # Calculates the direction the shield should face towards the player.
        self.ShieldDirection = pygame.Vector2(player_pos) - self.pos

        if self.ShieldDirection.length() > 0:

            self.ShieldDirection = self.ShieldDirection.normalize()



    def TakeDirectionalDamage(self, damage, hitPosition):

        # Checks if the shield can block damage from the incoming direction.
        if self.ShieldActive and not self.ShieldBroken:

            HitDirection = pygame.Vector2(hitPosition) - self.pos

            if HitDirection.length() > 0:

                HitDirection = HitDirection.normalize()


            # Dot product determines whether the attack comes from the shield side.
            if HitDirection.dot(self.ShieldDirection) > 0.5:

                print("Blocked by shield")
                return


        # Takes damage normally if the shield does not block it.
        self.health -= damage



    def SelfStun(self, time):

        # Being stunned breaks the shield temporarily.
        super().SelfStun(time)

        self.ShieldBroken = True



    def Attack(self, player_pos):

        self.PreparingAttack = True
        self.PrepareTimer = 0

        self.CanMove = False
        self.IsAttacking = False

        self.AttackCoolDownTimer = self.AttackCoolDown



    def DetermineAction(self, dt, player_pos):

        # Handles the warning before the swing.
        if self.PreparingAttack:

            self.PrepareTimer += dt


            if self.PrepareTimer >= self.PrepareDuration:

                self.PreparingAttack = False
                self.IsAttacking = True


                if self.Sword != None:

                    # Starts the actual swing after the warning.
                    self.Sword.Swing(
                        self.pos,
                        player_pos
                    )

                    self.AttackDuration = self.Sword.SwingTimer

                else:

                    self.AttackDuration = 0.25


            return



        # Continuously faces the player so the shield blocks correctly.
        self.FacePlayer(player_pos)


        # Normal movement behaviour.
        if self.CanMove:

            self.Move(
                dt,
                player_pos,
                self.speed
            )



        # Starts attack when cooldown has finished.
        if (
            self.CanMove
            and not self.IsAttacking
            and self.AttackCoolDownTimer <= 0
        ):

            self.Attack(player_pos)



        # Handles attack duration.
        if self.IsAttacking:

            self.AttackDuration -= dt


            if self.AttackDuration <= 0:

                self.IsAttacking = False
                self.CanMove = True
                self.AttackCoolDownTimer = self.AttackCoolDown



    def update(self, dt, player_pos, playerbulletlist, screen, player=None):

        # Runs normal enemy updating first.
        super().update(
            dt,
            player_pos,
            playerbulletlist,
            screen,
            player
        )
        if self.Sword != None:
            self.Sword.update(
                dt,
                screen,
                None,
                self.pos,
                player_pos
            )

        # Restores the shield once the enemy is no longer stunned.
        if not self.stunned:

            self.ShieldBroken = False

class MeleeSlime(BaseEnemy):
    def __init__(self, health, speed, position, size, WhichGun, WhichSword):

        # Uses normal enemy setup.
        super().__init__(health, speed, position, size, WhichGun, WhichSword)

        # Basic slime combat values.
        self.damage = 20
        self.AttackCoolDown = 1
        self.AttackCoolDownTimer = self.AttackCoolDown
        self.AttackDuration = 0
        self.tag = "Enemy"

        # Slime takes reduced gun damage.
        self.melee_resistance = 1
        self.gun_resistance = 2

        # Prevents contact damage happening every frame.
        self.ContactDamageCooldown = 1
        self.ContactDamageTimer = 0

        # Loads the slime animation.
        self.animations = {
            "MeleeSlime": SpriteSheetLoader.LoadSpriteSheet(
                "SpriteSheets/Slime/MeleeSlime.png",
                32,
                32
            ),
        }

    def GetAnimation(self):

        # Slimes only have one animation.
        return "MeleeSlime"

    def DetermineAction(self, dt, player_pos):

        # Slimes constantly chase the player.
        if not self.stunned:
            self.Move(dt, player_pos, self.speed)
    def update(self, dt, player_pos, playerbulletlist, screen, player=None):
        # Updates damage text timers and removes expired text.
        for text in self.damage_texts[:]:
                text.update(dt)
                if text.timer >= text.duration:
                    self.damage_texts.remove(text)

        # Removes enemy when health reaches zero.
        if self.health <= 0:
            self.Die()

        # Updates attack timers.
        self.AttackDuration -= dt
        self.AttackCoolDownTimer -= dt

        # Checks collisions with player bullets.
        for i in range(len(playerbulletlist)):
            if(self.Collision(playerbulletlist[i])):
                self.ResolveCollision(playerbulletlist[i])

        # Checks again after taking damage in case the bullet killed the enemy.
        if self.health <= 0:
            self.Die()

        # Handles stun duration.
        if(self.stunned):
            self.stunTime -= dt

            if(self.stunTime <= 0):
                self.stunned = False

        # Handles knockback movement separately from normal movement.
        if self.KnockedBack:
            self.pos += self.KnockbackDirection * self.KnockbackSpeed * dt
            self.KnockbackTimer -= dt

            if self.KnockbackTimer <= 0:
                self.KnockedBack = False    

        # Enemy cannot act while stunned or being knocked back.
        if(not self.stunned and not self.KnockedBack):
            self.DetermineAction(dt, player_pos)

        # Removes bullets that have already hit something.
        if(self.UsesGun):
            self.bulletList = [b for b in self.bulletList if not getattr(b, "dead", False)]

        # Updates collision rectangle to match the current position.
        self.Rect = pygame.Rect(
            self.pos.x,
            self.pos.y,
            self.size[0],
            self.size[1]
        )

        # Updates the current animation frame.
        self.UpdateAnimation(dt)
class GunSlime(MeleeSlime):
    def __init__(self, health, speed, position, size, WhichGun, WhichSword):

        # Uses the MeleeSlime setup but changes the combat properties.
        super().__init__(health, speed, position, size, WhichGun, WhichSword)

        # Gun slime is resistant to gun damage but weaker to melee.
        self.melee_resistance = 0
        self.gun_resistance = 5

        # Loads the gun slime specific animation.
        self.animations = {
            "GunSlime": SpriteSheetLoader.LoadSpriteSheet(
                "SpriteSheets/Slime/GunSlime.png",
                32,
                32
            ),
        }

    def GetAnimation(self):

        # Gun slimes only use their single animation.
        return "GunSlime"


WhichEnemy = {
    cls.__name__: cls
    for cls in BaseEnemy.__subclasses__()
}