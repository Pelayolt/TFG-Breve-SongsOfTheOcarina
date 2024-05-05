import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile
import sounddevice as sd
import pygame
import time
from collections import deque

# Configuración de notas
notas_ocarina = {
    pygame.K_a: 3, #RE - D
    pygame.K_s: 6, #FA - F
    pygame.K_d: 10, #LA - A
    pygame.K_f: 12, #SI - B
    pygame.K_g: 4 # RE#/MIb - D^
}

#Secuencia de todas las canciones
canciones = [
    [[12, 4, 10, 12, 4, 10], "Nana_de_Zelda_OoT.mp3"],
    [[4, 12, 10, 4, 12, 10], "Canción_de_Epona_OoT.mp3"],
    [[6, 10, 12, 6, 10, 12], "Canción_de_Saria.mp3"],
    [[10, 3, 6, 10, 3, 6], "Song_of_time.mp3"],
    [[10, 6, 4, 10, 6, 4], "Canción_del_sol.mp3"],
    [[3, 4, 12, 10, 12, 10], "Minueto_del_Bosque_OoT.mp3"],
    [[6, 3, 6, 3, 10, 6, 10, 6], "Bolero_de_fire.mp3"],
    [[3, 6, 10, 10, 12], "Serenata_del_Agua_OoT.mp3"],
    [[3, 6, 4, 3, 6, 4], "Canción_de_la_Tormenta.mp3"],
    [[3, 6, 3, 10, 6, 3], "Réquiem_del_Espíritu_OoT.mp3"],
    [[4, 10, 4, 10, 12, 4], "Preludio_Luz_OoT.mp3"],
]

# Inicializar Pygame
pygame.mixer.init()
pygame.init()

# Configuración de sonido
framerate = 44100
duración = 1.0
frecuencia = 440
stream = sd.OutputStream(channels=1, callback=None, dtype=np.float32, samplerate=framerate)

# Obtener las dimensiones de la pantalla
ancho, alto = pygame.display.Info().current_w, pygame.display.Info().current_h

# Configurar la ventana
ventana = pygame.display.set_mode((ancho, alto), pygame.FULLSCREEN)
pygame.display.set_caption("Ocarina Simulator")

# Cargar el fondo principal
fondo_principal = pygame.image.load("Imagenes/Fondo.jpg")
fondo_principal = pygame.transform.scale(fondo_principal, (ancho, alto))

# Cargar el manual de la ocarina
manual = pygame.image.load("Imagenes/manual.png")
ancho_manual, alto_manual = manual.get_size()

#Cargar toda la información de todas las canciones
canciones_info = []
for i in range(len(canciones)):
    imagen_boton = pygame.image.load(f"Botones/boton{i}.png")
    rectangulo_boton = imagen_boton.get_rect(topleft=(5, i*85 + 5))
    
    imagen_partitura = pygame.image.load(f"Partituras/partitura{i}.png")
    imagen_partitura = pygame.transform.scale(imagen_partitura, (1000, 300))
    
    canciones_info.append((imagen_boton, rectangulo_boton, imagen_partitura))
    
nombreNota = 0
imagen_onda = pygame.image.load(f"Ondas/onda{nombreNota}.png")
imagen_onda = pygame.transform.scale(imagen_onda, (300, 80))

#Inicializar la secuencia del jugador
secuencia_jugador = deque(maxlen=8)

#Inicializar una partitura
imagen_partitura_pantalla = canciones_info[0][2]
rectangulo_partitura = imagen_partitura_pantalla.get_rect(center=((ancho // 2), (alto // 1.2)))

# Diccionario para realizar un seguimiento de los sonidos en reproducción y sus tiempos de inicio
sonidos_en_reproduccion = deque(maxlen=2)

def nombre(nota: int):
    if(nota == 3): return "Re"
    elif(nota == 6): return "Fa"
    elif(nota == 10): return "La"
    elif(nota == 12): return "Si"
    else: return "Re#"

def frec(nota: int) -> int:
    if nota == 4:
        expo = 6 * 12 + (nota - 58)
    else:
        expo = 5 * 12 + (nota - 58)
    return int(frecuencia * ((2 ** (1 / 12)) ** expo))

def generar_nota(nota: int, duracion: int) -> None:
    tiempo = np.linspace(0, duracion / 1000, int(framerate * duracion / 1000))
    frecuencia = frec(nota)
    onda = np.sin(2 * np.pi * frecuencia * tiempo)
    return onda

def tocar_nota(nota: int) -> None:
    onda = generar_nota(nota, 2000)
    stream = sd.play(onda, framerate)
    sonidos_en_reproduccion.append(stream)
    time.sleep(0.1)
        
def pausar_nota() -> None:
    try:
        stream = sonidos_en_reproduccion[0]
        sd.stop(stream)
        del sonidos_en_reproduccion[0]
    except Exception as e:
        sd.stop()
    
# Bucle principal del programa
while True:
    for evento in pygame.event.get():
        
        ventana.blit(fondo_principal, (0,0))
        ventana.blit(manual, (ancho - ancho_manual - 5, 5))
        
        # Dibujar botones
        for indice, cancion_info in enumerate(canciones_info):
            ventana.blit(cancion_info[0], (5, indice*85 + 5))
        
        if evento.type == pygame.QUIT:
            pygame.quit()
            quit()
            
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            pygame.quit()
            quit()
            
        elif evento.type == pygame.KEYDOWN:
            tecla = evento.key
            if tecla in notas_ocarina:
                nota = notas_ocarina[evento.key]
                nombreNota = nombre(nota)
                tocar_nota(nota)
                secuencia_jugador.append(nota)
                
        elif evento.type == pygame.KEYUP:
            tecla = evento.key
            if tecla in notas_ocarina:
                pausar_nota()                

                for indice, cancion in enumerate(canciones):
                    s = list(secuencia_jugador)
                    if s[-8:] == cancion[0] or s[-7:] == cancion[0] or s[-6:] == cancion[0] or s[-5:] == cancion[0]:
                        time.sleep(0.5)
                        pygame.mixer.music.load("Canciones/" + cancion[1])
                        pygame.mixer.music.play()
                        imagen_partitura_pantalla = canciones_info[indice][2]
                        print(f"Está sonando {cancion[1]}")
                        secuencia_jugador = []
                        nombreNota = 0
                        time.sleep(0.5)
                        
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            for imagen_boton, rectangulo_boton, imagen_partitura in canciones_info:
                if rectangulo_boton.collidepoint(evento.pos):
                    imagen_partitura_pantalla = imagen_partitura
                    
        imagen_onda = pygame.image.load(f"Ondas/onda{nombreNota}.png")
        imagen_onda = pygame.transform.scale(imagen_onda, (300, 80))
        ventana.blit(imagen_partitura_pantalla, rectangulo_partitura)
        ventana.blit(imagen_onda, (ancho/2 + 150, 790))
        pygame.display.flip()
   
    pygame.time.delay(1) 