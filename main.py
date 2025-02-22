import pygame
import json
import os

# Inicializar o Pygame
pygame.init()

# Definir a largura e a altura da tela
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jogo de Animação")

# Caminho da pasta onde estão as imagens
IMAGE_FOLDER = 'char/'
BACKGROUND_IMAGE = 'back/spring-forest-landscape.jpg'  # Caminho da imagem de fundo

# Carregar o arquivo JSON de animações
with open('animations.json', 'r') as f:
    animation_data = json.load(f)

# Carregar imagens de fundo
background = pygame.image.load(BACKGROUND_IMAGE)

# Carregar imagens (substitua com seus próprios arquivos de imagem)
def load_images(animation):
    try:
        return [pygame.image.load(os.path.join(IMAGE_FOLDER, image)) for image in animation_data["states"][animation]]
    except Exception as e:
        print(f"Erro ao carregar imagens de {animation}: {e}")
        return []

# Personagem
class Character(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 100
        self.speed = 5
        self.health = 6  # Inicialmente 6 vidas
        self.state = "parado"  # Estado inicial
        self.image_list = load_images(self.state)
        self.current_frame = 0
        self.image = self.image_list[self.current_frame]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
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
            return  # O personagem não faz nada mais, ele fica parado no estado morto

        if self.state != "morrendo":  # Só processa o movimento se não estiver morrendo
            # Movimento horizontal
            if keys[pygame.K_a]:  # Tecla 'A' ou 's'
                self.x -= self.speed
                self.state = "andando"
                self.flip_image(False)  # Virar para a esquerda
            elif keys[pygame.K_d]:  # Tecla 'D' ou 'd'
                self.x += self.speed
                self.state = "andando"
                self.flip_image(True)  # Virar para a direita
            elif keys[pygame.K_LSHIFT] and (keys[pygame.K_a] or keys[pygame.K_d]):  # Correndo
                self.speed = 8
                self.state = "correndo"
                if keys[pygame.K_d]: 
                    self.flip_image(True)  # Virar para a direita ao correr
                elif keys[pygame.K_a]:
                    self.flip_image(False)  # Virar para a esquerda ao correr
            else:
                self.state = "parado"
                self.speed = 5  # Volta a velocidade normal
                self.flip_image(False)  # Deixar voltado para a esquerda
                
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

            # Atualizar animação
            self.image_list = load_images(self.state)
            if self.image_list:
                self.current_frame = (self.current_frame + 1) % len(self.image_list)
                self.image = self.image_list[self.current_frame]
                self.rect = self.image.get_rect(center=(self.x, self.y))

        # Verificar se os hits chegaram a 0
        if hits == 0 and self.state != "morrendo":
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
        """Função para inverter a imagem do personagem dependendo da direção"""
        if flip:
            self.image = pygame.transform.flip(self.image, True, False)  # Inverte horizontalmente
        else:
            self.image = pygame.transform.flip(self.image, False, False)  # Deixa a imagem normal (não invertida)

# Função para mostrar o contador de hits
def show_hits(hits):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Hits: {hits}", True, (255, 0, 0))
    screen.blit(text, (10, 10))

# Função para mostrar a tela de morte
def game_over():
    font_large = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)
    
    # Texto "GAME OVER"
    text_large = font_large.render("GAME OVER", True, (255, 0, 0))
    screen.blit(text_large, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50))
    
    # Texto "Pressione R para reiniciar"
    text_small = font_small.render("Pressione R para reiniciar", True, (128, 0, 0))
    screen.blit(text_small, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 20))

# Adicionar lógica para reiniciar o jogo
def reset_game():
    global hits, character
    hits = 6
    character = Character()
    all_sprites.empty()
    all_sprites.add(character)

# Configurações do jogo
clock = pygame.time.Clock()
running = True

# Criar o personagem
character = Character()
all_sprites = pygame.sprite.Group(character)

# Contador de hits
hits = 6

# Loop principal
while running:
    screen.fill((0, 0, 0))  # Limpar tela

    # Exibir o fundo
    screen.blit(background, (0, -100))
    
    # Gerenciar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h and hits > 0:
                hits -= 1
            # Verifica se 'R' foi pressionado para reiniciar o jogo
            if event.key == pygame.K_r and character.state == "morto":
                reset_game()

    keys = pygame.key.get_pressed()
    all_sprites.update(keys)
    
    # Desenhar na tela
    all_sprites.draw(screen)
    
    # Mostrar contador de hits
    show_hits(hits)
    
    # Verificar se o personagem está morto
    if character.state == "morto":
        game_over()
    
    pygame.display.flip()
    clock.tick(30)  # Controla a taxa de atualização da tela (FPS)


pygame.quit()
