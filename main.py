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
LOGO_IMAGE = 'logo/main.png'  # Caminho do logo

# Carregar o arquivo JSON de animações
with open('animations.json', 'r') as f:
    animation_data = json.load(f)

# Carregar imagens de fundo
background = pygame.image.load(BACKGROUND_IMAGE)
logo = pygame.image.load(LOGO_IMAGE)

# Carregar imagens (substitua com seus próprios arquivos de imagem)
def load_images(animation):
    try:
        return [pygame.image.load(os.path.join(IMAGE_FOLDER, image)) for image in animation_data["states"][animation]]
    except Exception as e:
        print(f"Erro ao carregar imagens de {animation}: {e}")
        return []

# Função de fade-in e fade-out
def fade_in_out(duration, fade_out=False):
    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill((0, 0, 0))
    clock = pygame.time.Clock()
    
    if fade_out:
        alpha = 255
    else:
        alpha = 0

    while alpha >= 0 and alpha <= 255:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        if fade_out:
            alpha -= 5  # Desce a opacidade
        else:
            alpha += 5  # Aumenta a opacidade

        fade_surface.set_alpha(alpha)
        screen.fill((0, 0, 0))
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(30)

# Personagem
class Character(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 100
        self.speed = 5
        self.health = 6  # Inicialmente 6 vidas
        self.hits = 6  # A quantidade de hits começa com 6
        self.state = "parado"  # Estado inicial
        self.image_list = load_images(self.state)
        self.current_frame = 0
        self.image = self.image_list[self.current_frame]
        self.rect = self.image.get_rect(center=(self.x, self.y))

        # Inicializando a variável 'flipped' como True
        self.flipped = True  # A imagem começa invertida (virada para a esquerda)

        # Controle de pulo
        self.is_jumping = False
        self.jump_height = 10
        self.velocity_y = 0
        self.gravity = 1
        
        # Teclas de controle
        self.key_bindings = animation_data["teclas"]

    def update(self, keys):
        # Se o personagem estiver morto, ele não pode mais fazer nada
        if self.state == "morto":
            self.y = SCREEN_HEIGHT - 100  # Colocar o personagem no chão
            return  # O personagem não faz nada mais, ele fica parado no estado morto

        if self.state != "morrendo":  # Só processa o movimento se não estiver morrendo
            # Movimento horizontal
            if keys[pygame.K_a]:  # Tecla 'A' (esquerda)
                self.x -= self.speed
                self.state = "andando"
                self.flip_image('esquerda')  # Virar para a esquerda

            elif keys[pygame.K_d]:  # Tecla 'D' (direita)
                self.x += self.speed
                self.state = "andando"
                self.flip_image('direita')  # Virar para a direita

            # Correndo (se pressionado Shift)
            elif keys[pygame.K_LSHIFT] and (keys[pygame.K_a] or keys[pygame.K_d]):  # Correndo
                self.speed = 8
                self.state = "correndo"
                if keys[pygame.K_d]: 
                    self.flip_image('direita')  # Virar para a direita ao correr
                elif keys[pygame.K_a]:
                    self.flip_image('esquerda')  # Virar para a esquerda ao correr
            else:
                self.state = "parado"
                self.speed = 5  # Volta a velocidade normal
                # Não precisa mais inverter a imagem ao parar, o flip vai ser controlado pelos movimentos

        # Atualização da animação do personagem
        self.image_list = load_images(self.state)
        if self.image_list:
            self.current_frame = (self.current_frame + 1) % len(self.image_list)
            self.image = self.image_list[self.current_frame]
            self.rect = self.image.get_rect(center=(self.x, self.y))

            # Pulo
            if keys[pygame.K_w] and not self.is_jumping:  # Tecla 'W'
                self.is_jumping = True
                self.velocity_y = -self.jump_height  # Inicia o pulo para cima
            
            # Atualizar a física do pulo (gravidade)
            if self.is_jumping:
                self.velocity_y += self.gravity  # Aumenta a velocidade devido à gravidade
                self.y += self.velocity_y
                if self.y >= SCREEN_HEIGHT - 100:  # Quando o personagem voltar ao chão
                    self.y = SCREEN_HEIGHT - 100
                    self.is_jumping = False
                    self.velocity_y = 0

            # Atacando
            if keys[pygame.K_SPACE]:  # Barra de espaço
                self.state = "atacando"

            # Deitando
            if keys[pygame.K_s]:  # Tecla 'S'
                self.state = "deitando"

            # Mudando para a animação de "hit" quando 'h' for pressionado
            if keys[pygame.K_h]:  # Tecla 'H' para mudar a animação de hit
                self.state = "hit"
            
            # Atualizar animação
            self.image_list = load_images(self.state)
            if self.image_list:
                self.current_frame = (self.current_frame + 1) % len(self.image_list)
                self.image = self.image_list[self.current_frame]
                self.rect = self.image.get_rect(center=(self.x, self.y))

        # Verificar se os hits chegaram a 0
        if self.hits == 0 and self.state != "morrendo":
            print("Hits chegaram a 0! Iniciando animação de morte.")
            self.state = "morrendo"
            self.image_list = load_images(self.state)
            self.current_frame = 0  # Começar da primeira imagem da animação de morte
            self.image = self.image_list[self.current_frame]
            self.rect = self.image.get_rect(center=(self.x, self.y))

        # Quando a animação de morte acabar, o personagem fica morto
        if self.state == "morrendo":
            if self.current_frame == len(self.image_list) - 1:
                print("Animação de morte concluída. Personagem está morto.")
                self.state = "morto"  # Transita para o estado morto
                self.image_list = load_images(self.state)  # Carrega a imagem de morto
                self.current_frame = 0  # O personagem morto tem apenas uma imagem
                self.image = self.image_list[self.current_frame]
                self.rect = self.image.get_rect(center=(self.x, self.y))
            else:
                # Avança para o próximo quadro da animação de morte
                self.current_frame = (self.current_frame + 1) % len(self.image_list)
                self.image = self.image_list[self.current_frame]
                self.rect = self.image.get_rect(center=(self.x, self.y))

    def flip_image(self, flip):
        print(f"Flip: {flip}, Flipped: {self.flipped}")

        if flip == 'direita':  # Se a direção for para a direita
            if self.flipped:  # Se a imagem estiver virada para a esquerda
                self.image = pygame.transform.flip(self.image, True, False)  # Inverte apenas a imagem atual
                self.flipped = False  # Marca como não invertida (virada para a direita)
                print("Imagem virada para a direita")
            
        elif flip == 'esquerda':  # Se a direção for para a esquerda
            if not self.flipped:  # Se a imagem não estiver virada para a esquerda
                self.image = pygame.transform.flip(self.image, True, False)  # Inverte apenas a imagem atual
                self.flipped = True  # Marca como invertida (virada para a esquerda)
                print("Imagem virada para a esquerda")


# Função para mostrar o contador de hits
def show_hits(character):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Hits: {character.hits}", True, (255, 0, 0))
    screen.blit(text, (10, 10))

# Função para mostrar a tela de morte
def game_over():
    font_large = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)
    
    # Texto "GAME OVER"
    text_large = font_large.render("+ Aqui acaba a sua odisseia, ou não? +", True, (255, 0, 0))
    # Centralizando o texto "GAME OVER"
    text_large_rect = text_large.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 ))
    screen.blit(text_large, text_large_rect)

    # Texto "Pressione R para reiniciar"
    text_small = font_small.render("Pressione R para reiniciar", True, (128, 0, 0))
    # Centralizando o texto "Pressione R para reiniciar"
    text_small_rect = text_small.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40 ))
    screen.blit(text_small, text_small_rect)

# Adicionar lógica para reiniciar o jogo
def reset_game():
    global character
    character = Character()
    all_sprites.empty()
    all_sprites.add(character)

# Configurações do jogo
clock = pygame.time.Clock()
running = True

# Tela inicial (Splash Screen)
# Exibir o logo por 3 segundos
screen.fill((255, 255, 255))  # Limpa a tela
screen.blit(logo, (SCREEN_WIDTH // 2 - logo.get_width() // 2, SCREEN_HEIGHT // 2 - logo.get_height() // 2))  # Centraliza o logo
pygame.display.flip()
pygame.time.delay(3000)  # Exibe o logo por 3 segundos

# Fade-out após logo
fade_in_out(30, fade_out=True)

# Exibir o título por 4 segundos
screen.fill((0, 0, 0))  # Limpa a tela
font = pygame.font.Font(None, 72)
title_text = font.render("Spanks na geral, Vol I -  floresta", True, (255, 255, 255))
screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2.5))  # Centraliza o título
pygame.display.flip()
pygame.time.delay(4000)  # Exibe o título por 4 segundos

# Fade-out após o título
fade_in_out(30, fade_out=True)

# Criar o personagem
character = Character()
all_sprites = pygame.sprite.Group(character)

# Loop principal
while running:
    screen.fill((0, 0, 0))  # Limpar tela

    # Exibir o fundo
    screen.blit(background, (0, 0))
    
    # Gerenciar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h and character.hits > 0:
                character.hits -= 1
            # Verifica se 'R' foi pressionado para reiniciar o jogo
            if event.key == pygame.K_r and character.state == "morto":
                reset_game()

    keys = pygame.key.get_pressed()
    all_sprites.update(keys)
    
    # Desenhar na tela
    all_sprites.draw(screen)
    
    # Mostrar contador de hits
    show_hits(character)
    
    # Verificar se o personagem está morto
    if character.state == "morto":
        game_over()
    
    pygame.display.flip()
    clock.tick(30)  # Controla a taxa de atualização da tela (FPS)

pygame.quit()
