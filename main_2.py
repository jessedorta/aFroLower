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
LIFE_FOLDER = 'life/'  # Pasta onde estão as imagens da vida
BACKGROUND_IMAGE = 'back/spring-forest-landscape_ok.jpg'  # Caminho da imagem de fundo

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

# Função para carregar as imagens de vida
def load_life_images():
    return [pygame.image.load(os.path.join(LIFE_FOLDER, f"life{i}.png")) for i in range(1, 7)]

# Definindo variáveis do personagem
character_state = "parado"
character_images = load_animation_images(character_state)
character_rect = pygame.Rect(SCREEN_WIDTH // 2 - character_images[0].get_width() // 2, SCREEN_HEIGHT // 2 - character_images[0].get_height() // 2 + 50, character_images[0].get_width(), character_images[0].get_height())

# Definindo variáveis de vida
life = 6
life_images = load_life_images()  # Sequência de imagens de vida
current_life_image = life_images[life - 1]  # A imagem de vida inicial
faleceu_message = ""

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

# Para controlar a diminuição da vida e animações de hit
last_h_pressed = False  # Variável para controlar se a tecla H foi pressionada na última iteração
hit_animation_frames = []  # Variáveis para armazenar os quadros da animação de hit
hit_frame_index = 0  # Controla qual quadro da animação está sendo exibido
hit_animating = False  # Flag para controlar se a animação de hit está em execução

# Função principal do jogo
def main():
    global character_state, character_images, character_rect, bg_offset_x, bg_offset_y, facing_right, life, current_life_image, faleceu_message, last_h_pressed, hit_animation_frames, hit_frame_index, hit_animating
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
                character_images = load_animation_images("andando", flip=facing_right)  # Estado "andando"
            character_state = "andando"  # Mudar para o estado "andando"
        elif keys[pygame.K_d]:  # Tecla "d" para mover o fundo para a direita
            bg_offset_x -= move_speed
            if not facing_right:  # Se estava virado para a esquerda, inverte a imagem
                facing_right = True
                character_images = load_animation_images("andando", flip=facing_right)  # Estado "andando"
            character_state = "andando"  # Mudar para o estado "andando"
        else:
            # Se não pressionar nenhuma tecla, o personagem fica parado
            character_state = "parado"
            character_images = load_animation_images(character_state, flip=facing_right)

        # Calcular o quadro atual da animação do personagem
        current_frame = pygame.time.get_ticks() // 100 % len(character_images)

        # Gerenciar a tecla H para diminuir a vida e mostrar animação de hit
        if keys[pygame.K_h] and not last_h_pressed and life > 0:
            life -= 1  # Diminuir a vida de 1 por vez
            if life > 0:
                current_life_image = life_images[life - 1]  # Atualiza a imagem da vida
            else:
                current_life_image = None  # Remove a imagem quando a vida chega a zero

            # Carregar a animação de hit (estou assumindo que você tem isso no JSON)
            hit_animation_frames = load_animation_images("hit")  # Carrega as imagens de "hit" do JSON
            hit_animating = True  # Iniciar a animação de hit
            hit_frame_index = 0  # Resetar a animação de hit para o primeiro quadro

            last_h_pressed = True  # Atualiza a flag para evitar múltiplas diminuições

        # Se a animação de hit estiver rodando, desenha os quadros da animação
        if hit_animating:
            # Desenhar a animação de hit primeiro (antes do personagem e das vidas)
            screen.blit(hit_animation_frames[hit_frame_index], character_rect)
            hit_frame_index += 1
            if hit_frame_index >= len(hit_animation_frames):  # Quando a animação acabar, voltar ao estado normal
                hit_animating = False
                hit_frame_index = 0

        # Agora desenhar o personagem e as vidas
        if not hit_animating:  # Se não estiver na animação de hit, desenha o personagem
            screen.blit(character_images[current_frame], character_rect)

        # Desenhar todas as imagens de vida na mesma posição
        if life > 0:
            screen.blit(life_images[life - 1], (20, 50))  # Alinha as imagens da vida no canto superior esquerdo

        # Se a vida chegou a zero, exibe "faleceu..." no centro da tela
        if life == 0:
            font = pygame.font.Font(None, 74)
            text = font.render("faleceu...", True, (255, 0, 0))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))

        # Se a tecla H não estiver mais pressionada, permite que ela seja pressionada novamente
        if not keys[pygame.K_h]:
            last_h_pressed = False

        pygame.display.flip()  # Atualiza a tela
        clock.tick(30)  # Controla a taxa de quadros

    pygame.quit()

if __name__ == "__main__":
    main()
