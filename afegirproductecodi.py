# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""La funció d'aquest script es rebre el codi de barres
teclejat a Telegram, per tal d'afegir un nombre determinat
d'unitats a la base de dades."""

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
        # DEFINIM LA VARIABLE codibarres, QUE SERÀ EL MISSATGE QUE HA REBUT.
        global codibarres
        codibarres = str(command)
        # DEFINIM b = 1, PER TAL QUE NO ES TORNI A EXECUTAR AQUEST CODI.
        global b
        b = 1
        # FEM UNA CONSULTA A LA BASE DE DADES PER SABER EL NOM DEL PRODUCTE QUE CORRESPON A AQUEST CODI DE BARRES.
        cursor.execute("SELECT nom FROM productes WHERE codibarres = '" + str(codibarres) + "'")
        nomproducte = cursor.fetchall()
        # ENVIEM UN MISSATGE A L'USUARI PER A QUE ENS DIGUI QUANTES UNITATS VOL AFEGIR-NE.
        bot.sendMessage(chat_id, "Digui'ns quantes unitats vol afegir de " + str(nomproducte[0][0]) +".")
    
    # QUAN b =! 0 i c == 0 (ÉS A DIR, UNA SOLA VEGADA), S'EXECUTARÀ AQUEST CODI.
    elif c == 0:
        # DEFINIM LA VARIABLE quantitat, QUE SERÀ EL MISSATGE QUE HA REBUT.
        global quantitat
        quantitat = str(command)
        # DEFINIM c = 1, PER TAL QUE NO ES TORNI A EXECUTAR AQUEST CODI.
        global c
        c = 1
        # ACTUALITZEM LA BASE DE DADES, SUMANT LA QUANTITAT SOL·LICITADA AL PRODUCTE.
        cursor.execute("UPDATE productes SET quantitat = quantitat + " + str(quantitat) + " WHERE codibarres = '" + str(codibarres) + "'")
        conn.commit()
        # ENVIEM UN MISSATGE A L'USUARI CONFORME S'HA ACTUALITZAT.
        resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Inici')]], one_time_keyboard=True)
        bot.sendMessage(chat_id, "S'ha actualitzat la base de dades.", reply_markup=resposta)
        # TORNEM A OBRIR EL SCRIPT PRINCIPAL I TANQUEM AQUEST.
        os.popen('python menuprincipal.py').read()
        os._exit(0)
        
# INICIA EL BOT DE TELEGRAM I EL MANTÉ EN EXECUCIÓ.
bot.message_loop(handle)
while True:
    time.sleep(10)