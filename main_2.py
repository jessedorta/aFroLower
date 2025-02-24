import pygame
import json
import os

# Inicializar o Pygame
pygame.init()

# Definir a largura e a altura da tela
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("aFroLower - spanks na geral")

# Caminho da pasta onde estão as imagens
IMAGE_FOLDER = 'char/'
LIFE_FOLDER = 'life/'
BACKGROUND_IMAGE = 'back/spring-forest-landscape_ok.jpg'

# Carregar o arquivo JSON de animações
with open('animations.json', 'r') as file:
    animations_data = json.load(file)

# Função para carregar as imagens das animações e redimensionar
def load_animation_images(state, flip=False):
    images = [pygame.image.load(os.path.join(IMAGE_FOLDER, img)) for img in animations_data["states"][state]]
    images = [pygame.transform.scale(img, (400, int(img.get_height() * (400 / img.get_width())))) for img in images]
    if flip:
        images = [pygame.transform.flip(img, True, False) for img in images]
    return images

# Função para carregar as imagens de vida
def load_life_images():
    return [pygame.image.load(os.path.join(LIFE_FOLDER, f"life{i}.png")) for i in range(1, 7)]

# Definindo variáveis do personagem
def reset_game():
    global character_state, character_images, character_rect, life, current_life_image, life_images, facing_right, dying, dead
    character_state = "parado"
    character_images = load_animation_images(character_state)
    character_rect = pygame.Rect(SCREEN_WIDTH // 2 - character_images[0].get_width() // 2, SCREEN_HEIGHT // 2 - character_images[0].get_height() // 2 + 50, character_images[0].get_width(), character_images[0].get_height())
    life_images = load_life_images()
    life = 6
    current_life_image = life_images[life - 1]
    facing_right = False
    dying = False
    dead = False

# Função para desenhar o fundo repetido
def draw_background(offset_x, offset_y):
    background = pygame.image.load(BACKGROUND_IMAGE)
    bg_width, bg_height = background.get_size()
    start_x = offset_x % bg_width
    for x in range(start_x - bg_width, SCREEN_WIDTH, bg_width):
        screen.blit(background, (x, 0))
    for x in range(start_x - bg_width, 0, -bg_width):
        screen.blit(background, (x, 0))

# Variáveis para controle do movimento do fundo
bg_offset_x = 0
bg_offset_y = 0
move_speed = 5
facing_right = False

# Variáveis para animações
last_h_pressed = False
hit_animation_frames = []
hit_frame_index = 0
hit_animating = False
dying_frame_index = 0
dying = False
dead = False

# Função principal do jogo
def main():
    global character_state, character_images, character_rect, bg_offset_x, bg_offset_y, facing_right, life, current_life_image, last_h_pressed, hit_animation_frames, hit_frame_index, hit_animating, dying, dying_frame_index, dead
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill((0, 0, 0))
        draw_background(bg_offset_x, bg_offset_y)

        # Gerenciar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Controlar teclas pressionadas
        keys = pygame.key.get_pressed()
        moving = False

        # Só permite movimento se o personagem não estiver morrendo ou morto
        if not dying and not dead:
            if keys[pygame.K_a]:
                bg_offset_x += move_speed
                if facing_right:
                    facing_right = False
                character_state = "andando"
                moving = True
            elif keys[pygame.K_d]:
                bg_offset_x -= move_speed
                if not facing_right:
                    facing_right = True
                character_state = "andando"
                moving = True

            # Atualizar as imagens do personagem com base no estado
            if moving:
                character_images = load_animation_images("andando", flip=facing_right)
            elif character_state != "parado":
                character_state = "parado"
                character_images = load_animation_images("parado", flip=facing_right)

        # Calcular o quadro atual da animação do personagem
        current_frame = pygame.time.get_ticks() // 100 % len(character_images)

        # Gerenciar a tecla H para diminuir a vida e mostrar animação de hit
        if keys[pygame.K_h] and not last_h_pressed and life > 0 and not dying and not dead:
            life -= 1
            if life > 0:
                current_life_image = life_images[life - 1]
                # Carregar a animação de hit com o flip baseado na direção atual
                hit_animation_frames = load_animation_images("hit", flip=facing_right)
                hit_animating = True
                hit_frame_index = 0
            else:
                current_life_image = None
                dying = True
                character_images = load_animation_images("morrendo", flip=facing_right)
                dying_frame_index = 0
            last_h_pressed = True

        # Gerenciar a animação de hit
        if hit_animating:
            screen.blit(hit_animation_frames[hit_frame_index], character_rect)
            hit_frame_index += 1
            if hit_frame_index >= len(hit_animation_frames):
                hit_animating = False
                hit_frame_index = 0

        # Gerenciar a animação "morrendo"
        elif dying:
            screen.blit(character_images[dying_frame_index], character_rect)
            dying_frame_index += 1
            if dying_frame_index >= len(character_images):
                dying = False
                dead = True
                character_images = load_animation_images("morto", flip=facing_right)

        # Se estiver morto, exibe a animação "morto"
        elif dead:
            screen.blit(character_images[0], character_rect)

        # Se não estiver em hit, morrendo ou morto, desenha a animação normal
        elif not hit_animating:
            screen.blit(character_images[current_frame], character_rect)

        # Desenhar a vida
        if life > 0:
            screen.blit(life_images[life - 1], (20, 50))

        # Se a vida chegou a zero e o personagem está morto
        if dead:
            font = pygame.font.Font(None, 74)
            text = font.render("+ Faleceu...", True, (255, 0, 0))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Aperte R para reiniciar", True, (255, 0, 0))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            if keys[pygame.K_r]:
                reset_game()

        if not keys[pygame.K_h]:
            last_h_pressed = False

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    reset_game()
    main()