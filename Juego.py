import pygame, sys
from pygame import mixer
from pygame.locals import *
import random

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
#Defino fps
clock = pygame.time.Clock()
fps = 60
screen_width = 600
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Space Invaders')

#Cargamos los sonidos

explosion_fx = pygame.mixer.Sound("Multimedia/explosion.wav")
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound("Multimedia/explosion2.wav")
explosion2_fx.set_volume(0.25)

explosion3_fx = pygame.mixer.Sound("Multimedia/laser.wav")
explosion3_fx.set_volume(0.25)

#Variables del juego
rows = 5
cols = 5
alien_cooldown = 800 #cooldown de los proyectiles
last_alien_shot = pygame.time.get_ticks()
#Colores
red = (255, 0 ,0)
green = (0, 255 ,0)

#Cargar imagen
bg = pygame.image.load('Multimedia/background.jpg')
def draw_bg():
    screen.blit(bg, (0,0))

#clase spaceship

class Spaceship(pygame.sprite.Sprite):
    def __init__(self,x , y, health):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('Multimedia/spaceship.jpg')
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()
    def update(self):
        #Ponemos la velocidad de movimiento
        speed = 8

        #Espera de disparo
        cooldown = 400 #milisegundos

        #Indicamos las teclas presionadas
        key=pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

        #Tiempo actual
        time_now = pygame.time.get_ticks()

        #Disparar
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            bullet = Bullets(self.rect.centerx,self.rect.top)
            bullet_group.add(bullet)
            self.last_shot = time_now

        #Actualizar MASK (imagen de cada pixel individual)
        self.mask = pygame.mask.from_surface(self.image)



        #Barra de vida
        pygame.draw.rect(screen, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15))
        elif self.health_remaining < 0:
            explosion = Explosion(self.rect.x, self.rect.centery, 3)
            explosion_group.add(explosion)
            self.kill()

#Clase Proyectiles
class Bullets(pygame.sprite.Sprite):
    def __init__(self,x , y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('Multimedia/bullet.jpg')
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            explosion_fx.play()
            explosion = Explosion(self.rect.x, self.rect.centery, 2)
            explosion_group.add(explosion)
#Clase aliens
class Aliens(pygame.sprite.Sprite):
    def __init__(self,x , y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("Multimedia/alien" + str(random.randint(1, 5))+".jpg")
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.move_counter = 0
        self.move_direction = 1
    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.move_direction *= -1
            self.move_counter *= self.move_direction

#Clase proyectiles de los aliens
#Clase Proyectiles
class Alien_bullets(pygame.sprite.Sprite):
    def __init__(self,x , y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('Multimedia/alien_bullet.jpg')
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]

    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self, spaceship_group, False, pygame.sprite.collide_mask):
            self.kill()
            #Reducimos la vida de la nave
            spaceship.health_remaining -= 1
            explosion = Explosion(self.rect.x, self.rect.centery, 1)
            explosion_group.add(explosion)


#Creamos la clase de Explosion

class Explosion(pygame.sprite.Sprite):
    def __init__(self,x , y, size):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"Multimedia/exp{num}.jpg")
            if size == 1:
                img = pygame.transform.scale(img, (20,20))
            if size == 2:
                img = pygame.transform.scale(img, (40,40))
            if size == 3:
                img = pygame.transform.scale(img, (160,160))
            #Agregamos la imagen a la list
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.counter = 0

    def update(self):
        explosion_speed = 3
        #Actualizamos la "animacion de la explosion"
        self.counter += 1
        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        #Cuando se completa la animacion borramos la explosion
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()

#Creamos el sprite de grupos
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

def create_aliens():
    #Generamos los aliens
    for row in range(rows):
        for item in range(cols):
            alien = Aliens(100 + item * 100, 100 + row * 70)
            alien_group.add(alien)
create_aliens()

#Creamos el jugador
spaceship = Spaceship(int(screen_width/2), screen_height - 100, 3)
spaceship_group.add(spaceship)

run = True
while run:
    clock.tick(fps)

    #Fondo
    draw_bg()

    #Crear proyectiles de los aliens
    time_now = pygame.time.get_ticks()
    if time_now - last_alien_shot > alien_cooldown and len(alien_bullet_group)< 5 and len(alien_group) > 0:
        attacking_alien = random.choice(alien_group.sprites())
        alien_bullet = Alien_bullets(attacking_alien.rect.centerx, attacking_alien.rect.bottom)
        alien_bullet_group.add(alien_bullet)
        last_alien_shot = time_now

    #Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    #Actualizar nave
    spaceship.update()

    #Actualizamos el grupo de sprites
    bullet_group.update()
    alien_group.update()
    alien_bullet_group.update()
    explosion_group.update()

    #Mostramos el grupo de sprites
    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    alien_group.draw(screen)
    alien_bullet_group.draw(screen)
    explosion_group.draw(screen)

    pygame.display.update()

pygame.quit()