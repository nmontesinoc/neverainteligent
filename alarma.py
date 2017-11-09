# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""La funció d'aquest script és detectar si la porta és oberta 
o no, i, si passa una quantitat de temps determinat, enviar un 
missatge de Telegram i fer que es reprodueixi un so d'alarma."""

# IMPORTACIÓ DELS MÓDULS NECESSARIS PER AL CORRECTE FUNCIONAMENT DEL CODI.
import time
import RPi.GPIO as GPIO
import telepot
import os

# INICIALITZACIÓ DEL GPIO NECESSARI I DEL BOT DE TELEGRAM I DEFINICIÓ D'UNA VARIABLE NECESSÀRIA PER A L'ESTRUCTURA DEL CODI.
GPIO.setmode(GPIO.BOARD)
GPIO.setup(40, GPIO.IN, GPIO.PUD_DOWN)
bot = telepot.Bot('TOKEN BOT TELEGRAM')
chat_id = 'ID CONVERSA TELEGRAM'
i = 0

# AQUEST SCRIPT ESTARÀ EN PERMANENT EXECUCIÓ.
while True:
    #  QUAN NO HI PASI CORRENT (ÉS A DIR, QUAN LA NEVERA ESTIGUI OBERTA) S'EXECUTARÀ AQUEST CODI.
    if GPIO.input(40) == False:
        # SI i < 61, ESPERARÀ UN SEGON I LI SUMARÀ UNA UNITAT A i.
        if i < 61:
            time.sleep(1)
            i = i + 1
        # QUAN i == 60, ES A DIR, QUAN HAGIN PASSAT 60 SEGONS, S'ENVIARÀ UN MISSATGE AL MOBIL, ES REPRODUIRÀ UN SO I ES DEFINIRÀ i = 0 PER A QUE LA TEMPORITZACIÓ PUGUI COMENÇAR DE NOU.
        if i == 60:
            bot.sendMessage(chat_id, "T'has deixat la nevera oberta!")
            os.system('mpg123 -q "soalarma.mp3"')
            i = 0
    # QUAN HI PASSI CORRENT (ÉS A DIR, QUAN LA NEVERA ESTIGUI TANCADA), ES DEFINIRÀ i = 0 PER TAL QUE QUAN S'OBRI COMENCI EL TEMPORITZADOR A 0.
    if GPIO.input(40) == True:
        i = 0