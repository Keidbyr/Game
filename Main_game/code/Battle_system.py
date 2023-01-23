import pygame
import sys
import random
from support import import_folder

# базовые настройки Pygame
pygame.font.init()
Pannel = 150
WIDTH, HEIGTH = 900, 528
Battlewindow = pygame.display.set_mode((WIDTH, HEIGTH))
pygame.display.set_caption("RPG Battle System")
clock = pygame.time.Clock()
# изображения для бекграунда, панели, кнопки, спелы, и другое
BG_image = pygame.image.load('../graphics/background.png').convert_alpha()
Pannel_image = pygame.image.load('../graphics/Panel.png').convert_alpha()
button1 = pygame.image.load('../graphics/buttons/arrow_next.png').convert_alpha()
button1 = pygame.transform.scale(button1, (40, 30))
attack_icon = pygame.image.load('../graphics/buttons/attack.png').convert_alpha()
attack_icon = pygame.transform.scale(attack_icon, (50, 50))
spells_icons = []
for i in range(0, 3):
    skill_img = pygame.image.load(f'../graphics/Spells_icon/spell{i}.png').convert_alpha()
    skill_img = pygame.transform.scale(skill_img, (50, 50))
    spells_icons.append(skill_img)
buttons = []
enemy_buttons = []
button_skill_press = False
button_enemy_press = False
Game_end = 0
buttonnsend = []
Player = None
EnemyList = None
mainloop = None
# Анимации персонажей
Playeranimations = {'Idle': [], 'Attack': [], 'Cast': [], 'Die': []}
Archeranimations = {'Idle': [], 'Attack': [], 'Die': []}
Minibossanimations = {}
Bossanimations = {}
# настройка шрифта для паналей
font = pygame.font.SysFont('Times New Roman', 26)
red = (255, 0, 0)
green = (0, 255, 0)
action = 0
action_time = 90
id_l = 0


class Mainloopp:
    def __init__(self):
        super().__init__()
        self.import_magic()
        self.turn = True
        self.turned = 1
        self.ally = 1
        self.speed = 0
        self.frame_animation = 0
        self.spell_speed = 0.13
        self.spell_status = 'nothing'
        self.enemy = len(EnemyList)
        self.skill_id = -1
        self.enemy_id = -1
        self.animation_pos = Player.pos

    # ход игрока
    def playerturn(self):
        if self.turned == 1:
            if self.skill_id != -1 and self.enemy_id != -1:
                self.turned += 1
                self.attack()
                Player.frame_index = 0
        else:
            self.enemyturn()

    # Спрайты для спелов
    def import_magic(self):
        character_path = f'../graphics/Spells/'
        self.animations = {'Holy_arrow': [], 'Holy_heal': [], 'Holy_impact': [], 'nothing': []}
        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    # анимация спелов
    def spell_animate(self):
        self.frame_animation += self.spell_speed
        animation = self.animations[self.spell_status]
        if self.frame_animation >= len(animation):
            self.frame_animation = 0
            self.speed = 0
            self.spell_status = 'nothing'
            self.animation_pos = Player.pos
        self.image = animation[int(self.frame_animation)]
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * 3, self.image.get_height() * 3))
        self.rect = self.image.get_rect()
        self.rect.center = self.animation_pos
        self.rect[0] += self.speed * (self.frame_animation * 0.6)
        if EnemyList[self.enemy_id].pos[0] - self.rect[0] < 100:
            self.animation_pos = EnemyList[self.enemy_id].pos
            if self.spell_status != 'Holy_impact':
                self.frame_animation = 0
                self.speed = 0
                EnemyList[self.enemy_id].hp -= 75
            self.spell_status = 'Holy_impact'
        Battlewindow.blit(self.image, self.rect)

    # атака игрока
    def attack(self):
        if self.skill_id == 0:
            Player.status = 'Attack'
            EnemyList[self.enemy_id].hp -= random.randint(50, 100)
        elif self.skill_id == 1:
            self.spell_status = 'Holy_arrow'
            self.speed = 100
            Player.status = 'Cast'
        else:
            Player.status = 'Cast'
            self.spell_status = 'Holy_heal'
            Player.hp = 100
        self.nachalozadershki = pygame.time.get_ticks()

    # ход опонента
    def enemyturn(self):
        zaderska = pygame.time.get_ticks()
        if zaderska - self.nachalozadershki > 1000:
            for i in EnemyList:
                if i.hp > 0:
                    i.status = 'Attack'
                    Player.hp -= random.randint(20, 30)
            self.skill_id = -1
            self.enemy_id = -1
            self.turned = 1

    # обновление боя
    def updateg(self):
        self.spell_animate()
        self.playerturn()


# база для персонажей
class Charaptersys:
    def __init__(self, x, y, max_hp, hp, folder, animations, enemy):
        super().__init__()
        self.import_character_assets(folder, animations)
        self.frame_index = 0
        self.animation_speed = 0.13
        self.image = self.animations['Idle'][self.frame_index]
        self.rect = self.image.get_rect()
        # статус и ресурсы персонажа
        self.status = 'Idle'
        self.max_hp = max_hp
        self.hp = hp
        self.live = True
        self.pos = (x, y)
        self.y = 350
        self.enemy = enemy

    # хп
    def draw_hpbar(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        Battlewindow.blit(img, (x, y))

    # ассеты
    def import_character_assets(self, folder, animations):
        character_path = f'../graphics/{folder}/'
        self.animations = animations
        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    # анимация персонажа
    def animate(self):
        global Game_end
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation) and self.status == 'Die' and self.enemy != 1:
            self.frame_index = len(animation) - 1
        elif self.frame_index >= len(animation) and self.status == 'Die':
            Game_end = 2
        if self.frame_index >= len(animation) and self.status == 'Idle':
            self.frame_index = 0
        elif self.frame_index >= len(animation) and self.status != 'Idle':
            self.status = 'Idle'
            animation = self.animations[self.status]
            self.frame_index = 0
        self.image = animation[int(self.frame_index)]
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * 3, self.image.get_height() * 3))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        if self.enemy != 1:
            self.image = pygame.transform.flip(self.image, True, False)
        Battlewindow.blit(self.image, self.rect)

    # жизнь
    def alive_char(self):
        if self.hp <= 0:
            self.status = 'Die'

    # обновления
    def update(self):
        self.animate()
        self.alive_char()
        self.draw_hpbar(f'HP:{self.hp}', font, red, self.pos[0] - 50, self.y)


# Код кнопки
class Button:
    def __init__(self, x, y, image):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width), int(height)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action


# Бекграунд и Панель
def draw_back(BG_image, wight, height, pannel):
    BG_image = pygame.transform.scale(BG_image, (wight, height))
    Battlewindow.blit(BG_image, (0, - pannel))


def draw_panel(wight, height, pannel, Pannel_image):
    Pannel_image = pygame.transform.scale(Pannel_image, (wight, pannel))
    Battlewindow.blit(Pannel_image, (0, height - pannel))


# Эффекты заклинаний
def import_spells_animations():
    character_path = f'../graphics/Spells/'
    spell_animations = {'Holy_arrow': [], 'Holy_heal': [], 'Holy_impact': []}
    for animation in spell_animations.keys():
        full_path = character_path + animation
        spell_animations[animation] = import_folder(full_path)


# отрисовка кнопок
def draw_buttons():
    for id_button in range(len(spells_icons)):
        if id_button * 60 > 119:
            buttonn = Button(150 + 50, 400 + 60 * id_button - 120, spells_icons[id_button])
        else:
            buttonn = Button(150, 400 + 60 * id_button, spells_icons[id_button])
        buttons.append(buttonn)
    for id_button_enemy in range(len(EnemyList)):
        buttonnn = Button(470 + 200 * id_button_enemy, 400, attack_icon)
        enemy_buttons.append(buttonnn)


# окончание боя
def Game_ending(game):
    global Start_game, Game_end
    global Player, EnemyList
    if not buttonnsend:
        buttonns = Button(400, 125, button1)
        buttonnsend.append(buttonns)
    if game == 1:
        img = font.render('Win', True, 'green')
        Battlewindow.blit(img, (400, 100))
        for chose_but_end in range(len(buttonnsend)):
            if buttonnsend[chose_but_end].draw(Battlewindow):
                pygame.quit()
                sys.exit()

    else:
        img = font.render('Lose', True, 'red')
        Battlewindow.blit(img, (400, 100))
        for chose_but_end in range(len(buttonnsend)):
            if buttonnsend[chose_but_end].draw(Battlewindow):
                pygame.quit()
                sys.exit()


# запуск боя
def fight():
    global EnemyList, Game_end
    global Player
    Start_game = True
    Player = Charaptersys(200, 285, 100, 100, 'Main character', Playeranimations, 1)
    EnemyList = [Charaptersys(500, 273, 100, 100, 'Archer charapter', Archeranimations, 3),
                 Charaptersys(700, 273, 100, 100, 'Archer charapter', Archeranimations, 3)]
    draw_buttons()
    mainloops = Mainloopp()
    while Start_game:
        draw_back(BG_image, WIDTH, HEIGTH, Pannel)
        draw_panel(WIDTH, HEIGTH, Pannel, Pannel_image)
        id_l = 0
        for Enemy in EnemyList:
            Enemy.update()
            id_l += 1
        for skill_but in range(len(buttons)):
            if buttons[skill_but].draw(Battlewindow) and not button_skill_press:
                mainloops.skill_id = skill_but
        count = 0
        for chose_but in range(len(enemy_buttons)):
            if EnemyList[chose_but].hp > 0:
                if enemy_buttons[chose_but].draw(Battlewindow) and not button_enemy_press:
                    mainloops.enemy_id = chose_but
            else:
                count +=1
        if count == len(EnemyList):
            Game_end = 1
        if Game_end == 0:
            Player.update()
            mainloops.updateg()
        else:
            Game_ending(Game_end)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()
        clock.tick(60)

