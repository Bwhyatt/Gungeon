import pygame
import Player
import Bullet
import Wall
import Enemy
import Room
import Camera
import DungeonBuilder
import Gun
import Sword

pygame.init()

Width = 1280
Height = 720
screen = pygame.display.set_mode((Width, Height))
clock = pygame.time.Clock()
# Initialises pygame and creates the main game window.
# The clock is used to control frame timing and calculate delta time.
GAME_STATE = "title"
Theplayer = None
SelectedGun = None
SelectedSword = None
dt = 0
EnemyBullets = []
# Global variables that persist between menu screens and gameplay.
# The player is created only after weapon selection is confirmed.

def all_subclasses(cls):
    subclasses = set(cls.__subclasses__())
    for sub in cls.__subclasses__():
        subclasses |= all_subclasses(sub)
    return subclasses
# Recursively collects every enemy class that inherits from BaseEnemy.
# This allows new enemies to be added without manually updating the class map.

EnemyClassmap = {cls.__name__: cls for cls in all_subclasses(Enemy.BaseEnemy)}
EnemyClassmap["BaseEnemy"] = Enemy.BaseEnemy
# Creates a lookup table where the enemy name stored in Tiled
# can be converted into the correct Python class.
RoomRegistry, CurrentRoom = DungeonBuilder.build_dungeon(EnemyClassmap)
camera = Camera.Camera(Width, Height)

def change_state(state):
    global GAME_STATE
    GAME_STATE = state

class Button:
    def __init__(self, rect, text, action):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.font = pygame.font.Font(None, 40)

    def draw(self, surface):
        pygame.draw.rect(surface, (30, 30, 30), self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)
        text = self.font.render(self.text, True, "white")
        surface.blit(text, text.get_rect(center=self.rect.center))

    def click(self, pos):
        if self.rect.collidepoint(pos):
            self.action()

def draw_text(surface, text, pos, size=30):
    font = pygame.font.Font(None, size)
    image = font.render(text, True, "white")
    surface.blit(image, pos)

def draw_hud():#the game ui for when you're actually in the dungeon
    if Theplayer is None:
        return

    pygame.draw.rect(screen, (0, 0, 0), (0, 0, 250, 110))

    draw_text(
        screen,
        f"Health: {Theplayer.health}/{Theplayer.Maxhealth}",
        (20, 20)
    )

    if Theplayer.weapon_mode == "gun":
        draw_text(
            screen,
            f"Ammo: {Theplayer.gun.ammo}/{Theplayer.gun.capacity}",
            (20, 55)
        )
    else:
        draw_text(screen, "Sword equipped", (20, 55))

    weapon = Theplayer.GivenGun if Theplayer.weapon_mode == "gun" else Theplayer.GivenSword

    pygame.draw.rect(screen, (0, 0, 0), (1000, 550, 250, 150))
    draw_text(screen, weapon, (1020, 570))

# all weapons selectable, including base classes
gun_options = list(Gun.WhichGun.keys())
sword_options = list(Sword.WhichSword.keys())

gun_descriptions = {
    "GunParent": "The standard starting sidearm.",
    "BallGun": "A bouncing projectile weapon.",
    "Shotgun": "Fires multiple pellets with spread.",
    "Sniper": "A powerful charging rifle.",
    "Dynamite": "Explosive projectiles.",
    "ChargeGun": "Hold fire to charge damage."
}

sword_descriptions = {
    "RegularSword": "The standard starting blade.",
    "BaseballBat": "Charge attacks knock enemies back.",
    "VampireSword": "Restores health through parries.",
    "HeavyHitter": "Slow but powerful swings.",
    "ReturnToSender": "Punishes enemy attacks.",
    "ShielderSword": "Builds shields from parries."
}

gun_index = 0
sword_index = 0

def start_game():
    # Creates the player using the currently selected weapons
    # and transitions from the menu into gameplay.
    global Theplayer, SelectedGun, SelectedSword, GAME_STATE

    SelectedGun = gun_options[gun_index]
    SelectedSword = sword_options[sword_index]

    Theplayer = Player.Realplayer(
        300,
        (32, 32),
        (600, 600),
        100,
        SelectedGun,
        SelectedSword
    )

    GAME_STATE = "playing"

def next_gun():#will sort of scroll through the guns
    global gun_index
    gun_index += 1

    if gun_index >= len(gun_options):
        gun_index = 0

def next_sword():#will sort of scroll through the swords
    global sword_index
    sword_index += 1

    if sword_index >= len(sword_options):
        sword_index = 0

def quit_game():
    global running
    running = False

def open_weapon_select():
    global GAME_STATE
    GAME_STATE = "weapon_select"

def confirm_selection():
    start_game()

start_button = Button((500, 300, 280, 70), "START", open_weapon_select)
gun_button = Button((350, 500, 220, 60), "CHANGE GUN", next_gun)
sword_button = Button((710, 500, 220, 60), "CHANGE SWORD", next_sword)
confirm_button = Button((500, 600, 280, 70), "CONFIRM", confirm_selection)
quit_button = Button((500, 400, 280, 70), "QUIT", quit_game)

def draw_title():
    draw_text(screen, "DUNGEON CRAWLER", (450, 150), 60)
    start_button.draw(screen)

def draw_weapon_select():#creates the loadout selection ui
    draw_text(screen, "SELECT YOUR LOADOUT", (420, 150), 50)

    gun_name = gun_options[gun_index]
    sword_name = sword_options[sword_index]

    draw_text(screen, f"Gun: {gun_name}", (350, 400), 40)
    draw_text(screen, gun_descriptions[gun_name], (350, 440), 25)

    draw_text(screen, f"Sword: {sword_name}", (710, 400), 40)
    draw_text(screen, sword_descriptions[sword_name], (710, 440), 25)

    gun_button.draw(screen)
    sword_button.draw(screen)
    confirm_button.draw(screen)

def draw_win():
    draw_text(screen, "YOU WIN", (550, 300), 70)
    quit_button.draw(screen)

def draw_game_over():
    draw_text(screen, "GAME OVER", (500, 300), 70)
    quit_button.draw(screen)

running = True

while running:#main game loop
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if GAME_STATE == "title":
                start_button.click(event.pos)
            elif GAME_STATE == "weapon_select":
                gun_button.click(event.pos)
                sword_button.click(event.pos)
                confirm_button.click(event.pos)

            elif GAME_STATE in ("game_over", "win"):
                quit_button.click(event.pos)
    screen.fill((20, 20, 20))
    if GAME_STATE == "title":
        draw_title()
    elif GAME_STATE == "weapon_select":
        draw_weapon_select()

    elif GAME_STATE == "playing":
        Enemies = CurrentRoom.EnemyList
        EnemyBullets = []
        for enemy in Enemies:
            for bullet in enemy.bulletList:
                EnemyBullets.append(bullet)
            
        Theplayer.update(screen, keys, dt, pygame.mouse.get_pos())
        camera.update(Theplayer)
        mouse_world = camera.reverse(pygame.mouse.get_pos())

        if Theplayer.weapon_mode == "gun":
            Theplayer.gun.update(dt, screen, keys, pygame.Vector2(Theplayer.pos[0] + Theplayer.size[0]/2,Theplayer.pos[1] + Theplayer.size[1]/2),  mouse_world)
        if Theplayer.weapon_mode == "sword":
            Theplayer.Sword.update(dt, screen, keys, pygame.Vector2(Theplayer.pos[0] + Theplayer.size[0]/2,Theplayer.pos[1] + Theplayer.size[1]/2), mouse_world)
        new_room = CurrentRoom.CheckChange(dt, Theplayer)
        if Theplayer.GivenGun == "Sniper":
            if Theplayer.gun.Charging:
                Theplayer.gun.TheChargeRay = Theplayer.gun.MakeChargeRay(CurrentRoom.WallList, screen)
            else:
                Theplayer.gun.TheChargeRay = None
        WallList = CurrentRoom.WallList
        for room in RoomRegistry.values():
            room.UpdateClear()
        for wall in WallList:
            wall.WallCollision(Theplayer)
        if new_room:
            CurrentRoom = new_room
            Theplayer.Room = CurrentRoom
        
        CurrentRoom.draw(screen, camera)
        for enemy in Enemies:
            if enemy.dead:
                continue
            for bullet in Theplayer.gun.bulletList:
                if enemy.Collision(bullet):
                    enemy.ResolveCollision(bullet)
            enemy.update(dt, Theplayer.pos, Theplayer.gun.bulletList, screen, Theplayer)
            for wall in WallList:
                wall.WallCollision(enemy)
                if enemy.Collision(wall):
                    enemy.ResolveCollision(wall)
            if enemy.UsesGun:
                enemy.gun.update(dt, screen, keys, pygame.Vector2(enemy.pos[0] + enemy.size[0]/2, enemy.pos[1] + enemy.size[1]/2), Theplayer.pos)
                enemy.bulletList = enemy.gun.bulletList
                enemy.gun.draw(screen, camera, enemy.gun.size, enemy.pos)
            if enemy.UsesSword:
                enemy.Sword.draw(screen, camera, enemy.Sword.size, enemy.pos)

                if enemy.Sword.Collision(Theplayer):
                    enemy.Sword.ResolveCollision(
                        Theplayer,
                        enemy.Sword.damage
                    )

            if Theplayer.weapon_mode == "sword":
                if Theplayer.Sword.Collision(enemy):
                    Theplayer.Sword.ResolveCollision(
                        enemy,
                        Theplayer.Sword.damage
                    )
                if enemy.Parryable and Theplayer.Sword.Parrying:
                    if Theplayer.Sword.ParryCollision(enemy):
                        Theplayer.Sword.ResolveParryCollision(enemy)

        Theplayer.gun.bulletList = [b for b in Theplayer.gun.bulletList if not getattr(b, "dead", False)]
        # Removes bullets marked as dead after collisions.

        for bullet in Theplayer.gun.bulletList:
            bullet.update(dt, screen)
            bullet.draw(screen, camera)
            for wall in WallList:
                if bullet.Collision(wall):
                    bullet.ResolveCollision(wall)
        for bullet in EnemyBullets:
            bullet.update(dt, screen)
            bullet.draw(screen, camera)
            if bullet.Collision(Theplayer):
                bullet.ResolveCollision(Theplayer)
            for wall in WallList:
                if bullet.Collision(wall):
                    bullet.ResolveCollision(wall)

        Theplayer.draw(screen, camera)
        if Theplayer.weapon_mode == "gun":
            Theplayer.gun.draw(screen, camera, Theplayer.gun.size, Theplayer.pos)
        if Theplayer.weapon_mode == "sword":
            Theplayer.Sword.draw(screen, camera, Theplayer.Sword.size, Theplayer.pos)
        draw_hud()

        if Theplayer.dead:
            GAME_STATE = "game_over"
        if all(room.Cleared for room in RoomRegistry.values()):
            GAME_STATE = "win"

    elif GAME_STATE == "win":
        draw_win()

    elif GAME_STATE == "game_over":
        draw_game_over()

    pygame.display.flip()

    dt = clock.tick(60) / 1000 # Converts frame time into seconds so movement and animations are frame-rate independent.

pygame.quit()