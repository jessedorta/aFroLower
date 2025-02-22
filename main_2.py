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
BACKGROUND_IMAGE = 'back/spring-forest-landscape.jpg'  # Caminho da imagem de fundo

# Carregar o arquivo JSON de animações
with open('animations.json', 'r') as file:
    animations_data = json.load(file)

# Função para carregar as imagens das animações e redimensionar
def load_animation_images(state, flip=False):
    images = [pygame.image.load(os.path.join(IMAGE_FOLDER, img)) for img in animations_data["states"][state]]
    
    # Redimensionar as imagens para 400px de largura
    images = [pygame.transform.scale(img, (400, int(img.get_height() * (400 / img.get_width())))) for img in images]
    
    if flip:
        images = [pygame.transform.flip(img, True, False) for img in images]  # Inverter horizontalmente
    return images

# Definindo variáveis do personagem
character_state = "parado"
character_images = load_animation_images(character_state)
character_rect = pygame.Rect(SCREEN_WIDTH // 2 - character_images[0].get_width() // 2, SCREEN_HEIGHT // 2 - character_images[0].get_height() // 2 + 50, character_images[0].get_width(), character_images[0].get_height())

# Função para desenhar o fundo repetido
def draw_background(offset_x, offset_y):
    background = pygame.image.load(BACKGROUND_IMAGE)
    bg_width, bg_height = background.get_size()

    # Calcular as posições onde o fundo precisa ser desenhado
    start_x = offset_x % bg_width  # Posição inicial para desenhar o fundo

    # Desenhar o fundo repetido até cobrir toda a tela à direita
    for x in range(start_x - bg_width, SCREEN_WIDTH, bg_width):
        screen.blit(background, (x, 0))

    # Desenhar o fundo repetido à esquerda se necessário
    for x in range(start_x - bg_width, 0, -bg_width):
        screen.blit(background, (x, 0))






    
# Variáveis para controle do movimento do fundo
bg_offset_x = 0
bg_offset_y = 0
move_speed = 5
facing_right = False  # Flag para controlar o lado que o personagem está virado

# Função principal do jogo
def main():
    global character_state, character_images, character_rect, bg_offset_x, bg_offset_y, facing_right
    clock = pygame.time.Clock()

    running = True
    while running:
        screen.fill((0, 0, 0))  # Preenche a tela com cor preta

        # Desenhar o fundo repetido
        draw_background(bg_offset_x, bg_offset_y)

        # Gerenciar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Controlar teclas pressionadas
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:  # Tecla "a" para mover o fundo para a esquerda
            bg_offset_x += move_speed
            if facing_right:  # Se estava virado para a direita, inverte a imagem
                facing_right = False
                character_images = load_animation_images(character_state, flip=facing_right)
        elif keys[pygame.K_d]:  # Tecla "d" para mover o fundo para a direita
            bg_offset_x -= move_speed
            if not facing_right:  # Se estava virado para a esquerda, inverte a imagem
                facing_right = True
                character_images = load_animation_images(character_state, flip=facing_right)
        else:
            # Se não pressionar nenhuma tecla, o personagem fica parado
            character_state = "parado"
            character_images = load_animation_images(character_state, flip=facing_right)

        # Atualizar as imagens do personagem com base no estado
        current_frame = pygame.time.get_ticks() // 100 % len(character_images)

        # Desenhar o personagem no centro da tela, 100px abaixo
        screen.blit(character_images[current_frame], character_rect)

        pygame.display.flip()  # Atualiza a tela
        clock.tick(30)  # Controla a taxa de quadros

    pygame.quit()

if __name__ == "__main__":
    main()
