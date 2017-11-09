# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""La funció d'aquest script és rebre els missatges que es reben del xat
de Telegram i actuar-ne en conseqüència. És la capa invisible que fa que
actua entre la base de dades, el mail i l'usuari."""

# IMPORTACIÓ DELS MÓDULS NECESSARIS PER AL CORRECTE FUNCIONAMENT DEL CODI.
import pymssql
import re
import time
import telepot
import RPi.GPIO as GPIO
import os
import sys
import Adafruit_DHT
import evdev
from evdev import InputDevice, categorize
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ForceReply

# CONNEXIÓ A LA BASE DE DADES, INICIALITZACIÓ DEL BOT DE TELEGRAM, CONNEXIÓ I IMPORTACIÓ DICCIONARI ASCII PER AL BON FUNCIONAMENT DEL LECTOR DEL CODI DE BARRES.
conn = pymssql.connect(server='SERVIDOR SQL', user='USUARI SQL', password='CONTRASENYA SQL', database='DDBB SQL')
cursor = conn.cursor()
splitter = re.compile(r'\d+')
bot = telepot.Bot('TOKEN BOT TELEGRAM')
chat_id = 'ID CONVERSA TELEGRAM'
GPIO.setmode(GPIO.BOARD)
dev = InputDevice("/dev/input/by-id/usb-USB_Adapter_USB_Device-event-kbd")
scancodes = {
    0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
    10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
    20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
    30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u';',
    40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
    50: u'M', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 100: u'RALT'
}

# DEFINICIÓ DEL BOT DE TELEGRAM. VEUREM QUE LA ESTRUCTURA ES REPETEIX PER A CADA COMANDAMENT.
def handle(msg):
    command = msg['text']
    print 'Got command: %s' % command

    # QUAN REBI UN MISSATGE QUE POSI "/start", ENVIARÀ EL TECLAT I EL MISSATGE DEL MENU PRINCIPAL.
    if command == '/start':
        humitat, temperatura = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 16)
        resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Els meus productes')], [KeyboardButton(text='Comanda')], [KeyboardButton(text='Afegir o eliminar productes')]], one_time_keyboard=True)
        bot.sendMessage(chat_id, "Benvolgut al sistema de nevera intel·ligent, siusplau seleccioni una opció del menu de sota. La temperatura actuament és de " + str(temperatura) + " graus, i la humitat és del " + str(humitat) + "%.", reply_markup=resposta)

    # QUAN REBI UN MISSATGE QUE POSI "Inici", ENVIARÀ EL TECLAT I EL MISSATGE DEL MENU PRINCIPAL.
    if command == 'Inici':
        humitat, temperatura = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 16)
        resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Els meus productes')], [KeyboardButton(text='Comanda')], [KeyboardButton(text='Afegir o eliminar productes')]], one_time_keyboard=True)
        bot.sendMessage(chat_id, "Benvolgut al sistema de nevera intel·ligent, siusplau seleccioni una opció del menu de sota. La temperatura actuament és de " + str(temperatura) + " graus, i la humitat és del " + str(humitat) + "%.", reply_markup=resposta)
    
    # QUAN REBI UN MISSATGE QUE POSI "Els meus productes", ENVIARÀ ELS PRODUCTES QUE TÉ ARA A LA NEVERA.
    if command == 'Els meus productes':
        # FA UNA CONSULTA A LA BASE DE DADES, VOL SABER EL NOM DE L'ARTICLE I LA QUANTITAT ACTUAL DEL MATEIX DE TOTS ELS PRODUCTES QUE HI HAGI A LA NEVERA.
        cursor.execute('SELECT nom FROM productes WHERE quantitat > 0')
        productesac = cursor.fetchall()
        cursor.execute('SELECT quantitat FROM productes WHERE quantitat > 0')
        productesq = cursor.fetchall()
        # DEFINIM TRES VARIABLES: n, t I b. SERÀN PEÇA CLAU PER A LA CORRECTA ESTRUCTURACIÓ DELS MISSATGES.
        n = 0
        t = 0
        b = 0
        while True:
            # AQUEST CODI S'EXECUTARÀ FINS QUE DONI ERROR (FINS QUE L'ARTICLE NÚMERO n NO EXISTEIXI).
            try:
                # EL COMANDAMENT cursor.execute RETORNA UN LISTAT. AIXÍ DONCS, PER A CADA MISSATGE AGAFAREM L'ARTICLE QUE CORRESPONGUI EN FUNCIÓ DEL NUMERO DE MISSATGE QUE SIGUI (DETERMINAT PER LA VARIABLE n).
                nom = productesac[n][0]
                quantitat = productesq[n][0]
                # DEFINIM LA VARIABLE b = 1, QUE ENS INDICARÀ SI N'HI HAN PRODUCTES A LA NEVERA O NO. AIXÍ DONCS, SI NO HI HAGUÉS CAP PRODUCTE A LA NEVERA, EL COMANDAMENT ANTERIOR DONARIA ERROR I PER TANT b == 1 NO SERIA POSSIBLE.
                b = 1
                # SUMEM UNA UNITAT A LA VARIABLE n, COSA LA QUAL ENS DONARÀ PAS A AGAFAR EL SEGÜENT ARTICLE QUAN TORNI A EXECUTAR-SE EL COMANDAMENT.
                n = n + 1
                # SI LA QUANTITAT QUE TENIM DE L'ARTICLE ÉS MAJOR A 1, ENVIAREM EL MISSATGE EN PLURAL.
                if quantitat > 1:
                    bot.sendMessage(chat_id, str(nom) + ", " + str(quantitat)+ " articles.")
                # SI LA QUANTITAT QUE TENIM DE L'ARTICLE ÉS IGUAL A 1, ENVIAREM EL MISSATGE EN SINGULAR.
                if quantitat == 1:
                     bot.sendMessage(chat_id, str(nom) + ", " + str(quantitat)+ " artícle.")
            # QUAN HI HAGI CAP ERROR AL CODI ANTERIOR, ÉS A DIR, QUAN L'ARTICLE NÚMERO n NO EXISTEIXI, PASSA A EXECUTAR AQUEST CODI DIRECTAMENT.
            except:
                # SEMPRE QUE t == 0, EXECUTARÀ EL CODI (ÉS A DIR, NOMÉS UNA VEGADA).
                while t == 0:
                    # QUAN b == 1 (ÉS A DIR, LA NEVERA NO ÉS BUIDA) ENVIARÀ UN MISSATGE CONFORME JA S'HAN ENVIAT TOTS ELS ARTICLES.
                    if b == 1:
                        resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Inici')]], one_time_keyboard=True)
                        bot.sendMessage(chat_id, "A dalt pots veure els productes que tens a la nevera actualment.", reply_markup=resposta)
                        # DEFINIM LA VARIABLE t = 1 PER TAL QUE NO TORNI A EXECUTAR-SE AQUEST CODI.
                        t = 1
                        a()
                    # QUAN b == 0 (ÉS A DIR, LA NEVERA ÉS BUIDA) ENVIARÀ UN MISSATGE CONFORME NO HI HA CAP ARTICLE A LA NEVERA.
                    if b == 0:
                        resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Inici')]], one_time_keyboard=True)
                        bot.sendMessage(chat_id, "No té cap producte a la nevera.", reply_markup=resposta)
                        a()
    
    # QUAN REBI UN MISSATGE AMB EL TEXT "Comanda", ENVIARÀ ELS ARTICLES QUE ES VAGIN A DEMANAR AL SUPERMERCAT.
    if command == 'Comanda':
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
                    # QUAN b == 1 (ÉS A DIR, HI HAN ARTICLES A LA COMANDA) ENVIARÀ UN MISSATGE AMB EL PREU TOTAL DE LA COMANDA I UN ALTRE PREGUNTANT SI VOL FER LA COMANDA O SI BÉ VOL CANVIAR-LA.
                    if b == 1:
                        bot.sendMessage(chat_id, "El preu total de la compra es de " + str(prtotal) + " €")
                        resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Fer comanda')], [KeyboardButton(text='Modificar')], [KeyboardButton(text='Inici')]], one_time_keyboard=True)
                        bot.sendMessage(chat_id, "Quina acció desitja realitzar?", reply_markup=resposta)
                        # DEFINIM LA VARIABLE t = 1 PER TAL QUE NO TORNI A EXECUTAR-SE AQUEST CODI.
                        t = 1
                        a()
                    # QUAN b == 0 (ÉS A DIR, NO HI HA CAP ARTICLE A LA COMANDA) ENVIARÀ UN MISSATGE INFORMANT-HO.
                    if b == 0:
                        resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Inici')]], one_time_keyboard=True)
                        bot.sendMessage(chat_id, "No té cap producte per demanar.", reply_markup=resposta)
                        a()
    
    # QUAN REBI UN MISSATGE AMB EL TEXT "Fer comanda", SOL·LICITARÀ CONFIRMACIÓ PER FER-LA.
    if command == 'Fer comanda':
        resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Si, vull fer la comanda ara")], [KeyboardButton(text='Inici')]], one_time_keyboard=True)
        bot.sendMessage(chat_id, "Està vostè segur que vol realitzar la comanda ara?", reply_markup=resposta)
    
    # QUAN REBI UN MISSATGE AMB EL TEXT "Sí, vull fer la comanda ara", ENVIARÀ UN MISSATGE AMB LA COMANDA AL SUPERMERCAT.
    if command == "Si, vull fer la comanda ara":
        # FA UNA CONSULTA A LA BASE DE DADES, VOL SABER EL NOM, LA QUANTITAT QUE NORMALMENT COMPRA I EL PREU PER UNITAT DE TOTS ELS ARTICLES DELS QUALS N'HI HAGI UN NOMBRE MENOR A LA QUANTITAT QUE NORMALMENT COMPRA.
        cursor.execute('SELECT nom FROM productes WHERE quantitat < qpredeterminada')
        producteslc = cursor.fetchall()
        cursor.execute('SELECT qpredeterminada FROM productes WHERE quantitat < qpredeterminada')
        productesqp = cursor.fetchall()
        cursor.execute('SELECT preu FROM productes WHERE quantitat < qpredeterminada')
        productespr = cursor.fetchall()
        # DEFINIM LES VARIABLES n I t, NECESSÀRIES PER A LA CORRECTA ESTRUCTURACIÓ DEL CODI. A MÉS, HEM DE DEFINIR TAMBÉ LA VARIABLE prtotal, QUE ENS INDICARÀ EL PREU FINAL DE LA COMPRA.
        n = 0
        t = 0
        prtotal = 0
        # CREA UN ARXIU ANOMENAT listacompra.txt, QUE SERÀ EL CORREU QUE ENVIAREM AL SUPERMERCAT. AL PRINCIPI LI INFORMA LA DIRECCIÓ D'ENTREGAMENT.
        os.system('echo "Bon dia. \n\nEns agradaria fer una comanda amb els següents artícles. \n\nEls recordem que la direcció de comanda és Carrer Sant Joan Evangelista 22, a Badalona. Gracies.\n\n" >> listacompra.txt')
        while True:
            # EXECUTARÀ AQUEST CODI SEMPRE NO HI HAGI ERROR (ÉS A DIR, SEMPRE QUE L'ARTICLE NÚMERO n EXISTEIXI)
            try:
                # EL COMANDAMENT cursor.execute RETORNA UN LISTAT. AIXÍ DONCS, PER A CADA MISSATGE AGAFAREM L'ARTICLE QUE CORRESPONGUI EN FUNCIÓ DEL NUMERO DE MISSATGE QUE SIGUI (DETERMINAT PER LA VARIABLE n).
                nom = producteslc[n][0]
                qpredeterminada = productesqp[n][0]
                preupu = productespr[n][0]
                # MULTIPLIQUEM EL PREU PER UNITAT PER LES QUANTITATS DEL ARTICLE QUE COMPRAREM, I HO SUMEM AL PREU TOTAL DE LA COMPRA.
                prtotal = float(qpredeterminada) * float(preupu) + float(prtotal)
                # SUMEM UNA UNITAT A LA VARIABLE n, COSA LA QUAL ENS DONARÀ PAS A AGAFAR EL SEGÜENT ARTICLE QUAN TORNI A EXECUTAR-SE EL COMANDAMENT.
                n = n + 1
                # AFEGIM UNA LINIA AL ARXIU listacompra.txt AMB L'ARTICLE I LA QUANTITAT QUE VOLEM REBRE.
                os.system('echo "' + str(nom) + ', ' + str(qpredeterminada) + '" >> listacompra.txt')
            # QUAN HI HAGI CAP ERROR AL CODI ANTERIOR, ÉS A DIR, QUAN L'ARTICLE NÚMERO n NO EXISTEIXI, PASSA A EXECUTAR AQUEST CODI DIRECTAMENT.
            except:
                # SEMPRE QUE t == 0, EXECUTARÀ EL CODI (ÉS A DIR, NOMÉS UNA VEGADA).
                while t == 0:
                    # AFEGIM UNA LINIA AL ARXIU listacompra.txt AMB L'IMPORT DE LA COMANDA.
                    os.system('echo "\nA més, recordi que encara ha de rebre un altre de correu de PayPal amb la confirmació del pagament, que és de ' + str(prtotal) + ' €" >> listacompra.txt')
                    # ENVIEM EL CORREU, EN AQUEST CAS AMB L'ASSUMPTE Comanda AL MAIL INDICAT AL COMANDAMENT.
                    os.system('mutt -s "Comanda" mail@configurar.net < listacompra.txt')
                    # DEFINIM LA VARIABLE t = 1 PER TAL QUE NO TORNI A EXECUTAR-SE AQUEST CODI.
                    t = 1
                    # ELIMINEM L'ARXIU listacompra.txt, PER TAL QUE NO S'AJUNTI AMB LA PROPERA COMANDA
                    os.system('rm -rf listacompra.txt')
                    # ENVIEM UN MISSATGE AMB L'ENLLAÇ DEL PAGAMENT VÍA PAYPAL DIRECTAMENT AL COMPTE DEL SUPERMERCAT I UN ALTRE AMB UN RECORDATORI SALUDABLE
                    resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Inici')]], one_time_keyboard=True)
                    bot.sendMessage(chat_id, "Comanda realitzada correctament. Recordi que encara ha de fer el pagament a https://www.paypal.me/USUARIPAYPALME/" + str(prtotal))
                    bot.sendMessage(chat_id, "Recordi que per mantenir una bona salut és imprescindible mantenir una dieta equilibrada, fer esport i beure aigua amb regularitat.", reply_markup=resposta)
                    a()
    
    # QUAN REBI UN MISSATGE AMB EL TEXT "Modificar", MODIFICAREM LA QUANTITAT QUE NORMALMENT COMPRA D'UN ARTICLE.
    if command == 'Modificar':
        # ENVIAREM UN MISSATGE DEMANANT EL NOM DE L'ARTICLE QUE VOL MODIFICAR.
        bot.sendMessage(chat_id, "Si us plau, digui'ns quin producte vol modificar")
        # EXECUTAREM EL SCRIPT QUE S'ENCARREGA DE FER AIXÒ I TANCAREM AQUEST.
        os.popen('python qpredeterminada.py').read()
        os._exit(0)
    
    # QUAN REBI UN MISSATGE AMB EL TEXT "Afegir o eliminar productes", PREGUNTARÀ QUINA ÉS LA OPCIÓ ADEQUADA.
    if command == 'Afegir o eliminar productes':
        resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='He rebut la comanda')], [KeyboardButton(text='Vull afegir un producte')], [KeyboardButton(text='Vull eliminar un producte')], [KeyboardButton(text='Inici')]], one_time_keyboard=True)
        bot.sendMessage(chat_id, "Si us plau, seleccioni una de les següents opcions al menu de sota.", reply_markup=resposta)
    
    # QUAN REBI UN MISSATGE AMB EL TEXT "He rebut la comanda", VOL DIR QUE ELS ARTICLES ANTERIORMENT DEMANATS JA HAN SIGUT REBUTS.
    if command == 'He rebut la comanda':
        # ACTUALITZARÀ LA BASE DE DADES, ESTABLINT QUE LA QUANTITAT REAL D'ARTICLES ARA MATEIX ÉS LA QUANTITAT QUE TÉ ARA MÉS LA QUE ES VA DEMANAR, NOMÉS EN ELS ARTICLES QUE ES VAN DEMANAR.
        cursor.execute('UPDATE productes SET quantitat = quantitat + qpredeterminada WHERE quantitat < qpredeterminada')
        conn.commit()
        resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Inici')]], one_time_keyboard=True)
        bot.sendMessage(chat_id, "S'ha actualitzat la base de dades correctament amb la comanda rebuda.", reply_markup=resposta)
    
    # QUAN REBI UN MISSATGE AMB EL TEXT "Vull afegir un producte", PREGUNTARÀ SI VOL FER-HO AMB EL LECTOR O TECLEJANT EL CODI DE BARRES.
    if command == 'Vull afegir un producte':
        resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Vull afegir un producte amb el lector')], [KeyboardButton(text='Vull afegir un producte teclejant el codi')]], one_time_keyboard=True)
        bot.sendMessage(chat_id, "Com vol fer-ho?", reply_markup=resposta)
    
    # QUAN REBI UN MISSATGE AMB EL TEXT "Vull afegir un producte amb el lector", ES DEMANARÀ QUE L'ESCANEGI.
    if command == 'Vull afegir un producte amb el lector':
        bot.sendMessage(chat_id, "Escanegi el producte a afegir, si us plau.")
        # DEGUT A LA COMPLEXITAT D'AQUEST CODI, NECESSITAREM DUES VARIABLES PER PODER LLEGIR L'ENTRADA DEL LECTOR. DETECTARÀ UN PER UN ELS 13 DIGITS QUE FORMEN EL CODI DE BARRES. PER TANT, LA i L'UTILITZAREM PER SABER QUANTS EN PORTA I CONFIGURAREM LA VARIABLE codibarres JA QUE, ENCARA QUE ARA NO ENS FACI FALTA, HEM DE FER MENCIÓ A AQUESTA I NO ES POT REFERENCIAR UNA VARIABLE QUE NO EXISTEIX.
        i = 0
        codibarres = 0
        # QUAN DETECTI QUE EL LECTOR ESTÀ ENVIANT ENTRADA, EXECUTARÀ EL CODI.
        for event in dev.read_loop():
            # SI EL NÚMERO DE DIGITS DEL CODI DE BARRES QUE TENIM ÉS MENOR A 13 (ÉS INCOMPLERT), EXECUTARÀ EL CODI.
            if i < 13:
                # SI L'ENTRADA ES VALIDA, L'EMMAGATZEMARÀ A LA VARIABLE data.
                if event.type == evdev.ecodes.EV_KEY:
                    data = evdev.categorize(event)
                    # REALMENT EL SISTEMA REP DUES VEGADES LA MATEIXA "TECLA POLSADA". PER TANT, NOMÉS AGAFAREM LA SEGONDA VEGADA QUE LA POLSI.
                    if data.keystate == 1:
                        # GRÀCIES AL DICCIONARI ASCII QUE HEM DEFINIT AL PRINCIPI, POSEM EL DÍGIT REAL A LA VARIABLE key_lookup.
                        key_lookup = scancodes.get(data.scancode) or u'UNKNOWN:{}'.format(data.scancode)
                        # AFEGIM AQUEST DÍGIT A LA VARIABLE CODIBARRES (NO EL SUMEM, EL TRACTEM COM UNA CADENA DE CARÀCTERS)
                        codibarres = str(codibarres) + str(key_lookup)
                        # AFEGIM UNA UNITAT A LA VARIABLE i PER A DONAR PAS AL SEGÜENT DÍGIT QUAN EL CODI ES TORNI A EXECUTAR.
                        i = i + 1
            # SI EL NÚMERO DE DIGITS DEL CODI DE BARRES QUE TENIM ÉS 13 (ÉS COMPLERT), AFEGIREM UNA UNITAT DEL PRODUCTE A LA BASE DE DADES.
            if i == 13:
                # HEM DE TREURE EL DÍGIT "0" QUE VAM INCORPORAR A LA VARIABLE codibarres PER TAL QUE NO QUEDES BUIDA.
                codibarres = codibarres[1:]
                # FA UNA CONSULTA A LA BASE DE DADES PER SABER EL NOM DEL PRODUCTE DEL QUAL HI AFEGIREM LA UNITAT.
                cursor.execute("SELECT nom FROM productes WHERE codibarres = '" + str(codibarres) + "'")
                nomproducte = cursor.fetchall()
                # SUMA UNA UNITAT A LA QUANTITAT DEL PRODUCTE QUE PERTANYI EL CODI DE BARRES
                cursor.execute("UPDATE productes SET quantitat = quantitat + 1 WHERE codibarres = '" + str(codibarres) + "'")
                conn.commit()
                # ENVIA UN MISSATGE CONFIRMANT QUE S'HA ACTUALITZAT LA BASE DE DADES.
                resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Inici')]], one_time_keyboard=True)
                bot.sendMessage(chat_id, "S'ha actualitzat la base de dades, introduint-se una unitat de " + str(nomproducte[0][0]), reply_markup=resposta)
                # SURT DEL BUCLE for, JA QUE NO TENIM CAP ARTICLE MÉS PER ESCANEJAR.
                break
    
    # QUAN REBI UN MISSATGE AMB EL TEXT "Vull afegir un producte teclejant el codi", DEMANARÀ QUE ESCRIGUI EL CODI.
    if command == 'Vull afegir un producte teclejant el codi':
        bot.sendMessage(chat_id, "Si us plau, escrigui el codi del producte")
        # EXECUTAREM EL SCRIPT QUE S'ENCARREGA DE FER AIXÒ.
        os.popen('python afegirproductecodi.py').read()
        os._exit(0)

    # QUAN REBI UN MISSATGE AMB EL TEXT "Vull eliminar un producte", PREGUNTARÀ SI VOL FER-HO AMB EL LECTOR O TECLEJANT EL CODI DE BARRES.
    if command == 'Vull eliminar un producte':
        resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Vull eliminar un producte amb el lector')], [KeyboardButton(text='Vull eliminar un producte teclejant el codi')]], one_time_keyboard=True)
        bot.sendMessage(chat_id, "Com vol fer-ho?", reply_markup=resposta)
    
    # QUAN REBI UN MISSATGE AMB EL TEXT "Vull afegir un producte amb el lector", ES DEMANARÀ QUE L'ESCANEGI.
    if command == 'Vull eliminar un producte amb el lector':
        bot.sendMessage(chat_id, "Escanegi el producte a eliminar, si us plau.")
        # DEGUT A LA COMPLEXITAT D'AQUEST CODI, NECESSITAREM DUES VARIABLES PER PODER LLEGIR L'ENTRADA DEL LECTOR. DETECTARÀ UN PER UN ELS 13 DIGITS QUE FORMEN EL CODI DE BARRES. PER TANT, LA i L'UTILITZAREM PER SABER QUANTS EN PORTA I CONFIGURAREM LA VARIABLE codibarres JA QUE, ENCARA QUE ARA NO ENS FACI FALTA, HEM DE FER MENCIÓ A AQUESTA I NO ES POT REFERENCIAR UNA VARIABLE QUE NO EXISTEIX.
        i = 0
        codibarres = 0
        # QUAN DETECTI QUE EL LECTOR ESTÀ ENVIANT ENTRADA, EXECUTARÀ EL CODI.
        for event in dev.read_loop():
            # SI EL NÚMERO DE DIGITS DEL CODI DE BARRES QUE TENIM ÉS MENOR A 13 (ÉS INCOMPLERT), EXECUTARÀ EL CODI.
            if i < 13:
                # SI L'ENTRADA ES VALIDA, L'EMMAGATZEMARÀ A LA VARIABLE data.
                if event.type == evdev.ecodes.EV_KEY:
                    data = evdev.categorize(event)
                    # REALMENT EL SISTEMA REP DUES VEGADES LA MATEIXA "TECLA POLSADA". PER TANT, NOMÉS AGAFAREM LA SEGONDA VEGADA QUE LA POLSI.
                    if data.keystate == 1:
                        # GRÀCIES AL DICCIONARI ASCII QUE HEM DEFINIT AL PRINCIPI, POSEM EL DÍGIT REAL A LA VARIABLE key_lookup.
                        key_lookup = scancodes.get(data.scancode) or u'UNKNOWN:{}'.format(data.scancode)
                        # AFEGIM AQUEST DÍGIT A LA VARIABLE CODIBARRES (NO EL SUMEM, EL TRACTEM COM UNA CADENA DE CARÀCTERS)
                        codibarres = str(codibarres) + str(key_lookup)
                        # AFEGIM UNA UNITAT A LA VARIABLE i PER A DONAR PAS AL SEGÜENT DÍGIT QUAN EL CODI ES TORNI A EXECUTAR.
                        i = i + 1
            # SI EL NÚMERO DE DIGITS DEL CODI DE BARRES QUE TENIM ÉS 13 (ÉS COMPLERT), AFEGIREM UNA UNITAT DEL PRODUCTE A LA BASE DE DADES.
            if i == 13:
                # HEM DE TREURE EL DÍGIT "0" QUE VAM INCORPORAR A LA VARIABLE codibarres PER TAL QUE NO QUEDES BUIDA.
                codibarres = codibarres[1:]
                # FA UNA CONSULTA A LA BASE DE DADES PER SABER EL NOM DEL PRODUCTE DEL QUAL HI AFEGIREM LA UNITAT.
                cursor.execute("SELECT nom FROM productes WHERE codibarres = '" + str(codibarres) + "'")
                nomproducte = cursor.fetchall()
                cursor.execute("SELECT quantitat FROM productes WHERE codibarres = '" + str(codibarres) + "'")
                quantitat = cursor.fetchall()
                # SI NO HI HA CAP ARTICLE DEL PRODUCTE QUE HA ESCANEJAT, NO PODEM ELIMINAR-LO. S'ENVIARÀ UN MISSATGE INFORMANT-HO.
                if float(quantitat[0][0]) == 0:
                    resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Inici')]], one_time_keyboard=True)
                    bot.sendMessage(chat_id, "No té cap unitat de " + str(nomproducte[0][0]) + " a la nevera." , reply_markup=resposta)
                    # SURT DEL BUCLE for, JA QUE NO TENIM CAP ARTICLE MÉS PER ESCANEJAR.
                    break
                # SI HI HA AL MENYS UN ARTICLE DEL PRODUCTE QUE HA ESCANEJAT, LI RESTARÀ UN A LA BASE DE DADES I ENVIARÀ UN MISSATGE INFORMANT-HO.
                if float(quantitat[0][0]) > 0:
                    cursor.execute("UPDATE productes SET quantitat = quantitat - 1 WHERE codibarres = '" + str(codibarres) + "'")
                    conn.commit()
                    resposta = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Inici')]], one_time_keyboard=True)
                    bot.sendMessage(chat_id, "S'ha actualitzat la base de dades, eliminant-se una unitat de " + str(nomproducte[0][0]), reply_markup=resposta)
                    # SURT DEL BUCLE for, JA QUE NO TENIM CAP ARTICLE MÉS PER ESCANEJAR.
                    break

    # QUAN REBI UN MISSATGE AMB EL TEXT "Vull eliminar un producte teclejant el codi", DEMANARÀ QUE ESCRIGUI EL CODI.
    if command == 'Vull eliminar un producte teclejant el codi':
        bot.sendMessage(chat_id, "Si us plau, escrigui el codi del producte")
        # EXECUTAREM EL SCRIPT QUE S'ENCARREGA DE FER AIXÒ I TANCAREM AQUEST.
        os.popen('python eliminarproductecodi.py').read()
        os._exit(0)

# INICIA EL BOT DE TELEGRAM I EL MANTÉ EN EXECUCIÓ.
bot.message_loop(handle)
while True:
    time.sleep(100)