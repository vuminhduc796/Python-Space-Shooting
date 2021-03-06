import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 1500, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")


# Load images
ENEMY_SHIP_1 = pygame.transform.scale(pygame.image.load(os.path.join("images", "enemy_ship_1.png")), (40, 40))
ENEMY_SHIP_2 = pygame.transform.scale(pygame.image.load(os.path.join("images", "enemy_ship_2.png")), (40, 40))
ENEMY_SHIP_3 = pygame.transform.scale(pygame.image.load(os.path.join("images", "enemy_ship_3.png")), (40, 40))
ENEMY_SHIP_4 = pygame.transform.scale(pygame.image.load(os.path.join("images", "enemy_ship_4.png")), (100, 100))

# Player player
PLAYER_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("images", "player_ship.png")), (50, 50))

# bullets
PLAYER_BULLET_1 = pygame.transform.scale(pygame.image.load(os.path.join("images", "player_bullet_1.png")), (40, 40))
PLAYER_BULLET_2 = pygame.transform.scale(pygame.image.load(os.path.join("images", "player_bullet_2.png")), (40, 40))
PLAYER_BULLET_3 = pygame.transform.scale(pygame.image.load(os.path.join("images", "player_bullet_3.png")), (40, 40))
PLAYER_BULLET_4 = pygame.transform.scale(pygame.image.load(os.path.join("images", "player_bullet_4.png")), (40, 40))

ENEMY_BULLET_1 = pygame.transform.scale(pygame.image.load(os.path.join("images", "enemy_bullet.png")), (50,50))
# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("images", "background.png")), (WIDTH, HEIGHT))

class Bullet:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.x += vel

    def off_screen(self, width):
        return not(self.x <= width and self.x >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Weapon:
    def __init__(self,damage,velocity,cool_down,image):
        self.damage = damage
        self.velocity = velocity
        self.image = image
        self.mask = pygame.mask.from_surface(self.image)
        self.cool_down = cool_down
        self.cool_down_counter = 0

    def cooldown(self):
        if self.cool_down_counter >= self.cool_down:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

class PlayerWeapon(Weapon):
    def __init__(self, damage, velocity,cooldown, image,  level):
        super().__init__(damage,velocity,cooldown,image)
        self.level = level

    def upgrade(self):
        self.level += 1


class Ship:

    def __init__(self, x, y, health=100):
        self.base_cooldown = 30
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.bullet_img = None
        self.bullets = []
        self.max_health = health
        self.weapons = {}
        self.current_weapon = 1

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 5))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 5))

    def move_bullets(self, vel, obj):
        for value in self.weapons.values():
            value.cooldown()
        for bullet in self.bullets:
            bullet.move(vel)
            if bullet.off_screen(WIDTH):
                self.bullets.remove(bullet)
            elif bullet.collision(obj):
                obj.health -= 10
                self.bullets.remove(bullet)

    def shoot(self):
        if self.weapons[self.current_weapon].cool_down_counter == 0:
            bullet = Bullet(self.x, self.y, self.bullet_img)
            self.bullets.append(bullet)
            self.weapons[self.current_weapon].cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.swap_weapon_countdown = 30
        self.ship_img = PLAYER_SHIP
        self.create_weapon()
        self.bullet_img = self.weapons[self.current_weapon].image
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.point = 0

    def create_weapon(self):
        weapon1 = PlayerWeapon(50, 10, 20, PLAYER_BULLET_1, 1)
        weapon2 = PlayerWeapon(30, 12, 15, PLAYER_BULLET_2, 1)
        weapon3 = PlayerWeapon(70, 8, 25, PLAYER_BULLET_3, 1)
        weapon4 = PlayerWeapon(55, 10, 30, PLAYER_BULLET_4, 1)
        self.weapons[1] = weapon1
        self.weapons[2] = weapon2
        self.weapons[3] = weapon3
        self.weapons[4] = weapon4

    def move_bullets(self, objs):
        for value in self.weapons.values():
            value.cooldown()
        for bullet in self.bullets:
            bullet.move(self.weapons[self.current_weapon].velocity)
            if bullet.off_screen(WIDTH):
                self.bullets.remove(bullet)
            else:
                for obj in objs:
                    if bullet.collision(obj):
                        obj.health -= self.weapons[self.current_weapon].damage
                        if obj.health <= 0:
                            objs.remove(obj)
                            self.point += 50
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)

    def shoot(self):
        if self.weapons[self.current_weapon].cool_down_counter == 0:
            bullet = Bullet(self.x, self.y, self.bullet_img)
            self.bullets.append(bullet)
            self.weapons[self.current_weapon].cool_down_counter = 1
            self.point -= 5

    def swap_weapon(self):
        if self.weapons[self.current_weapon].cool_down_counter == 0:
            if self.current_weapon == 4:
                self.current_weapon = 1
            else:
                self.current_weapon += 1
            self.bullet_img = self.weapons[self.current_weapon].image


class Enemy(Ship):
    COLOR_MAP = {
                "red": (ENEMY_SHIP_1, ENEMY_BULLET_1),
                "green": (ENEMY_SHIP_2, ENEMY_BULLET_1),
                "blue": (ENEMY_SHIP_3, ENEMY_BULLET_1)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.bullet_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.create_weapon()

    def create_weapon(self):
        weapon1 = PlayerWeapon(50, 10, 20, ENEMY_BULLET_1, 1)
        self.weapons[1] = weapon1
    def move(self, vel):
        self.x -= vel

def collide(object_1, object_2):
    offset_x = object_2.x - object_1.x
    offset_y = object_2.y - object_1.y
    return object_1.mask.overlap(object_2.mask, (offset_x, offset_y)) is not None


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    bullet_vel = -5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        score_label = main_font.render(f"Score: {player.point}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(score_label, ((WIDTH - level_label.get_width() - 10)/2, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(WIDTH + 100,WIDTH + 1500),random.randrange(50, HEIGHT-100), random.choice(["red", "blue", "green"]),random.randint(50,150))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_v]:
            player.swap_weapon()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_bullets(bullet_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.x <= 0:
                lives -= 1
                enemies.remove(enemy)

        player.move_bullets(enemies)

def mainmenu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

mainmenu()