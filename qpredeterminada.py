# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""La funció d'aquest script és modificar la
quantitat a demanar d'un producte, és a dir,
la comanda."""

# IMPORTACIÓ DELS MÓDULS NECESSARIS PER AL CORRECTE FUNCIONAMENT DEL CODI.
import pymssql
import re
import time
import telepot
import RPi.GPIO as GPIO
import os
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ForceReply

# CONNEXIÓ A LA BASE DE DADES, INICIALITZACIÓ DEL BOT DE TELEGRAM, I DEFINICIÓ DE VARIABLES NECESSÀRIES PER UNA CORERECTA ESTRUCTURACIÓ DEL CODI.
conn = pymssql.connect(server='SERVIDOR SQL', user='USUARI SQL', password='CONTRASENYA SQL', database='DDBB SQL')
cursor = conn.cursor()
splitter = re.compile(r'\d+')
bot = telepot.Bot('TOKEN BOT TELEGRAM')
chat_id = 'ID CONVERSA TELEGRAM'
GPIO.setmode(GPIO.BOARD)
global b
b = 0
global c
c = 0

# DEFINICIÓ DEL BOT DE TELEGRAM.
def handle(msg):
    command = msg['text']
    print 'Got command: %s' % command
    # QUAN b == 0 (ÉS A DIR, UNA SOLA VEGADA), S'EXECUTARÀ AQUEST CODI.
    if b == 0:
        # DEFINIM LA VARIABLE producteamodificar, QUE SERÀ EL MISSATGE QUE HA REBUT.
        global producteamodificar
        producteamodificar = str(command)
        # DEFINIM b = 1, PER TAL QUE NO ES TORNI A EXECUTAR AQUEST CODI.
        global b
        b = 1
        # ENVIEM UN MISSATGE A L'USUARI PER A QUE ENS DIGUI QUANTES UNITATS VOL REBRE.
        bot.sendMessage(chat_id, "Digui'ns quantes unitats vol rebre de " + str(producteamodificar) +".")
    
    # QUAN b =! 0 i c == 0 (ÉS A DIR, UNA SOLA VEGADA), S'EXECUTARÀ AQUEST CODI.
    elif c == 0:
        # DEFINIM LA VARIABLE quantitat, QUE SERÀ EL MISSATGE QUE HA REBUT.
        global quantitat
        quantitat = str(command)
        # DEFINIM c = 1, PER TAL QUE NO ES TORNI A EXECUTAR AQUEST CODI.
        global c
        c = 1
        # ACTUALITZA LA BASE DE DADES: CANVIA LA QUANTITAT A ENVIAR DE L'ARTICLE SOL·LICITAT.
        cursor.execute("UPDATE productes SET qpredeterminada = " + str(quantitat) + " WHERE nom = '" + str(producteamodificar) + "'")
        conn.commit()
        # ENVIEM UN MISSATGE A L'USUARI CONFORME S'HA ACTUALITZAT.
        resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Inici')]], one_time_keyboard=True)
        bot.sendMessage(chat_id, "S'ha actualitzat la comanda correctament.", reply_markup=resposta)
        # TORNEM A OBRIR EL SCRIPT PRINCIPAL I TANQUEM AQUEST.
        os.popen('python menuprincipal.py').read()
        os._exit(0)

# INICIA EL BOT DE TELEGRAM I EL MANTÉ EN EXECUCIÓ.       
bot.message_loop(handle)
while True:
    time.sleep(10)