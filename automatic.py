# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""La funció d'aquest script és enviar un missatge de Telegram a l'usuari
quan sigui el dia i la hora on va configurar la compra automàtica, i fer 
la comanda al supermercat en cas que l'usuari vulgui."""

# IMPORTACIÓ DELS MÓDULS NECESSARIS PER AL CORRECTE FUNCIONAMENT DEL CODI.
import pymssql
import re
import time
import telepot
import RPi.GPIO as GPIO
import os
import sys
import Adafruit_DHT
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ForceReply

# CONNEXIÓ A LA BASE DE DADES, INICIALITZACIÓ DEL BOT DE TELEGRAM, CONNEXIÓ I IMPORTACIÓ DICCIONARI ASCII PER AL BON FUNCIONAMENT DEL LECTOR DEL CODI DE BARRES.
conn = pymssql.connect(server='SERVIDOR SQL', user='USUARI SQL', password='CONTRASENYA SQL', database='DDBB SQL')
cursor = conn.cursor()
splitter = re.compile(r'\d+')
bot = telepot.Bot('TOKEN BOT TELEGRAM')
chat_id = 'ID CONVERSA TELEGRAM'
GPIO.setmode(GPIO.BOARD)

# AQUEST SCRIPT ESTARÀ EN PERMANENT EXECUCIÓ.
while True:
    # OBTÉ EL DIA DE LA SETMANA CONFIGURAT AL SISTEMA.
    dia = time.strftime("%A",time.localtime())
    # FA UNA CONSULTA A LA BASE DE DADES PER SABER QUIN DIA DE LA SETMANA ESTÀ CONFIGURADA LA COMPRA AUTOMÀTICA.
    cursor.execute('SELECT diasetmana FROM diacompra')
    diasetmana = cursor.fetchall()
    diasetmana = diasetmana[0][0]
    # SI EL DIA CONFIGURAT A LA BASE DE DADES I EL DIA ACTUAL COINCIDEIXEN, CONTINUA AMB EL SCRIPT.
    if dia == diasetmana:
        # OBTÉ LA HORA ACTUAL CONFIGURADA AL SISTEMA.
        hora = time.strftime("%H:%M",time.localtime())
        # FA UNA CONSULTA A LA BASE DE DADES PER SABER PER A QUINA HORA ESTÀ CONFIGURADA LA COMPRA AUTOMÀTICA.
        cursor.execute('SELECT hora FROM diacompra')
        horacompra = cursor.fetchall()
        horacompra = horacompra[0][0]
        # SI LA HORA CONFIGURADA A LA BASE DE DADES I LA HORA ACTUAL COINCIDEIXEN, ENVIARÀ LA COMANDA ACTUAL.
        if horacompra == hora:
            # FA UNA CONSULTA A LA BASE DE DADES, VOL SABER EL NOM, LA QUANTITAT QUE NORMALMENT COMPRA I EL PREU PER UNITAT DE TOTS ELS ARTICLES DELS QUALS N'HI HAGI UN NOMBRE MENOR A LA QUANTITAT QUE NORMALMENT COMPRA.
            cursor.execute('SELECT nom FROM productes WHERE quantitat < qpredeterminada')
            producteslc = cursor.fetchall()
            cursor.execute('SELECT qpredeterminada FROM productes WHERE quantitat < qpredeterminada')
            productesqp = cursor.fetchall()
            cursor.execute('SELECT preu FROM productes WHERE quantitat < qpredeterminada')
            productespr = cursor.fetchall()
            # DEFINIM LES VARIABLES n, t, b I c, PEÇA CLAU PER A LA ESTRUCTURACIÓ DEL CODI. A MÉS, HEM DE DEFINIR TAMBÉ LA VARIABLE prtotal, QUE ENS INDICARÀ EL PREU FINAL DE LA COMPRA.
            n = 0
            t = 0
            b = 0
            c = 0
            prtotal = 0
            while True:
                # AQUEST CODI S'EXECUTARÀ FINS QUE DONI ERROR (FINS QUE L'ARTICLE NÚMERO n NO EXISTEIXI).
                try:
                     # EL COMANDAMENT cursor.execute RETORNA UN LISTAT. AIXÍ DONCS, PER A CADA MISSATGE AGAFAREM L'ARTICLE QUE CORRESPONGUI EN FUNCIÓ DEL NUMERO DE MISSATGE QUE SIGUI (DETERMINAT PER LA VARIABLE n).
                    nom = producteslc[n][0]
                    qpredeterminada = productesqp[n][0]
                    preupu = productespr[n][0]
                    # QUAN c == 0 (ÉS A DIR, NOMÉS UNA VEGADA) ENVIARÀ UN PRIMER MISSATGE.
                    if c == 0:
                        bot.sendMessage(chat_id, "Li recordem quins productes té actualment per demanar a la propera comanda.")
                        c = 1
                    # DEFINIM LA VARIABLE b = 1, QUE ENS INDICARÀ SI N'HI HAN PRODUCTES A LA NEVERA O NO. AIXÍ DONCS, SI NO HI HAGUÉS CAP PRODUCTE A LA NEVERA, EL COMANDAMENT ANTERIOR DONARIA ERROR I PER TANT b == 1 NO SERIA POSSIBLE.
                    b = 1
                    # SUMEM UNA UNITAT A LA VARIABLE n, COSA LA QUAL ENS DONARÀ PAS A AGAFAR EL SEGÜENT ARTICLE QUAN TORNI A EXECUTAR-SE EL COMANDAMENT.
                    n = n + 1
                    # MULTIPLIQUEM EL PREU PER UNITAT PER LES QUANTITATS DEL ARTICLE QUE COMPRAREM, I HO SUMEM AL PREU TOTAL DE LA COMPRA.
                    preutu = float(qpredeterminada) * float(preupu)
                    prtotal = float(prtotal) + float(preutu)
                    # ENVIAREM EL NOM DE L'ARTICLE, LA QUANTITAT I EL PREU FINAL DELS ARTICLES. HO FAREM EN PLURAL, JA QUE HI HA MÉS D'UN.
                    if float(qpredeterminada) > 1:
                        bot.sendMessage(chat_id, str(nom) + ", " + str(qpredeterminada) + " articles. Preu de " + str(preutu) + " €")
                    # ENVIAREM EL NOM DE L'ARTICLE, LA QUANTITAT I EL PREU DE L'ARTICLE. HO FAREM EN SINGULAR, JA QUE NOMÉS HI HA UN.
                    if float (qpredeterminada) == 1:
                        bot.sendMessage(chat_id, str(nom) + ", " + str(qpredeterminada) + " artícle. Preu de " + str(preutu) + " €")
                # QUAN HI HAGI CAP ERROR AL CODI ANTERIOR, ÉS A DIR, QUAN L'ARTICLE NÚMERO n NO EXISTEIXI, PASSA A EXECUTAR AQUEST CODI DIRECTAMENT.
                except:
                    # SEMPRE QUE t == 0, EXECUTARÀ EL CODI (ÉS A DIR, NOMÉS UNA VEGADA).
                    while t == 0:
                        # QUAN b == 1 (ÉS A DIR, HI HAN ARTICLES A LA COMANDA) ENVIARÀ UN MISSATGE AMB EL PREU TOTAL DE LA COMANDA I UN ALTRE PREGUNTANT SI VOL FER LA COMANDA O SI BÉ VOL CANVIAR-LA. QUAN CONTESTI A AQUESTA PREGUNTA, SERÀ EL SCRIPT menuprincipal.py QUI AGAFI LA RESPOSTA I ACTUÏ EN CONSEQÜÈNCIA.
                        if b == 1:
                            bot.sendMessage(chat_id, "El preu total de la compra es de " + str(prtotal) + " €")
                            resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Fer comanda')], [KeyboardButton(text='Modificar')], [KeyboardButton(text='Inici')]], one_time_keyboard=True)
                            bot.sendMessage(chat_id, "Quina acció desitja realitzar?", reply_markup=resposta)
                            t = 1
                            a()
                        # QUAN b == 0 (ÉS A DIR, NO HI HA CAP ARTICLE A LA COMANDA) ENVIARÀ UN MISSATGE INFORMANT-HO.
                        if b == 0:
                            resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Inici')]], one_time_keyboard=True)
                            bot.sendMessage(chat_id, "No té cap producte per demanar.", reply_markup=resposta)
                            a()