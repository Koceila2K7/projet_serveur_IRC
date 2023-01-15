from distutils.util import change_root
import socket
import threading
import sys
from contants import CMD, HELP_MSG, MESSAGE_TYPES,\
    est_ce_que_j_ai_signer_ce_message, NB_MIN_DE_VOISINS
from typing import List, Dict
import uuid
import json
import random

class Connex:
    """
    class qui décrit une connexion 
    """

    def __init__(self, conn: socket.socket, addr: tuple):
        self.conn = conn
        self.addr = addr  # ('127.0.0.1', 35260)
        self.id = addr[0] + ':' + str(addr[1])  # 127.0.0.1:35260
        self.thread_recv = threading.Thread(target=receive_message,
                                            args=(self.conn, self.id,
                                                  1024, True))
        self.thread_recv.start()


def accept_connexions(s: socket.socket):
    """
    fonction principale du serveur pour gérer toute nouvelle connexion
    """
    while (True):
        conn, addr = s.accept()  # attendre des connexions sur une prise
        # Un appel a cette methode bloque le programme en attendant qu’un
        #  client se connecte a la prise
        c = Connex(conn, addr)
        connex_map[c.id] = c  # a verifier
        print("connexion de ", c.id)

        
#voisins: Dict = {}  # {KEY_NAME: id} # nickname_map
# or  {(nickname, id), (nickname, id), ...} ???

connex_map = {}  # {id: Connex, id: Connex, ...}
connex_lock = threading.Lock()

#nickname_map = {}  # {nickname: id, ...} # nickname_map des voisins !
#nickname_lock = threading.Lock()

#channels_map: Dict[str, list] = {}  # {chan_id: [nickname, nickname...], ...}
#channels_lock = threading.RLock()

#channels_keys: Dict[str, str] = {}  # {chan_id: key, ...}
# if channel dont have key or dont exist, channels_keys.get(channel) returns None

away_messages = {}  # {nickname: msg, nickname: msg,...}
away_messages_lock = threading.Lock()

_my_listening_socket = socket.socket()

# ipv4 AF_INET
# a SOCK STREAM (pour un mode connecte, soit ´ TCP) ou
# SOCK DGRAM (pour un non connecte, soit ´ UDP).
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP_ADDRESS = '127.0.0.1'
PORT_NUM = 4321


# Lire une varibale dans les arguements de lancement.
# si l'argument n'existe pas ou est != de 1 donc ce n'est pas le client de fondation
# Dans le cas ou arg1 = 1 dans c'est le noed de fondation

# try to connect to another node
args = sys.argv
first_node: bool = len(args) > 1 and args[1] == "1"


MY_KEY_NAME = str(uuid.uuid4()) # nickname
MY_SIGNATURE_KEY = str(uuid.uuid4())

if first_node:
    s.bind((IP_ADDRESS, PORT_NUM))
    s.listen()  # ??? reproduire les thread ouvrir une prise
    print("-- first node to be started --")
else:
    s.connect((IP_ADDRESS, PORT_NUM))
    message_id = str(uuid.uuid4())
    # demander au first_node ses voisins pour se connecter à l'un d'eux 
    message = {"type": MESSAGE_TYPES.VOISINS.value,
               "message_id": message_id,
               "id_exp": MY_KEY_NAME,
               "payload": "",
               "list_empreinte": [MY_SIGNATURE_KEY]}

    s.send(json.dumps(message).encode())
    # attente de la réponse du serveur de fondation
    # implémentation naive
    voisins_of_first_node = []
    while True:
        response = s.recv(1024)

        if not response:
            print("Connexion coupée")
            exit(1)

        response = json.loads(response.decode())
        if response['id_rec'] == MY_KEY_NAME\
                and est_ce_que_j_ai_signer_ce_message(MY_SIGNATURE_KEY,
                                                      response)\
                and response['type'] == MESSAGE_TYPES.VOISINS_RESPONSE.value:
            voisins_of_first_node = response['payload']
            break
        
    # dans ce cas je vais me connecter aux autres
    if len(voisins_of_first_node) > NB_MIN_DE_VOISINS:  # pour éviter de se retrouver seul sans amis
        # j'ai bien reçu les voisins du first_node
        s.close()  # fermer la connection avec le serveur de fondation
        # je vais en choisir NB_MIN_DE_VOISINS aléatoirement et me connecter dessus
        random.shuffle(voisins_of_first_node)
        for v in voisins_of_first_node[:NB_MIN_DE_VOISINS]:  # création des connexion
            s_voisin = socket.socket()
            s_voisin.connect()
            obj_conx_voisin = Connex(s_voisin, (str(v[0]), int(v[1]))) # la création de la classe lance un thread d'écoute de msgs
            connex_map[obj_conx_voisin.id] = obj_conx_voisin # je garde mes connexions
            #nickname_map[] # on ne gère pas les nicknames pour le moment
    
    else: # je reste connecté que au noeud principal donc je le garde comme voisin
        obj_conx_voisin = Connex(s, (IP_ADDRESS, PORT_NUM)) # la création de la classe lance un thread d'écoute de msgs
        connex_map[obj_conx_voisin.id] = obj_conx_voisin # je garde mes connexions
    
    # je vais aussi utiliser my_listening_socket pour écouter les nouvelles connexions
    thread_connex = threading.Thread(target=accept_connexions, args=(_my_listening_socket,))
    thread_connex.start()
    print("-- my_listening_socket started --\n")


# receive message function :
# est ce que j'ai signé le msg ? si oui je ne fais rien sinon je le traite
# est ce que je suis le destinataire ? si oui je le traite sinon je le broadcast à mes voisins


# first_node code
if first_node:
    voisins_to_send = []
    if len(connex_map) > NB_MIN_DE_VOISINS: # j'envoi une liste
        pass
    
    else : # j'envoi que mon adresse
        voisins_to_send.append([IP_ADDRESS, PORT_NUM]) # ?
    
    # envoyer un message de type voisins contenant les voisins_to_send ?        
        
######################


def receive_message(conn: socket.socket,
                    connexion_id: str,
                    msg_size: int = 1024,
                    verbose: bool = False,
                    ):
    """
    Fonction qui va gérer les messages pour chaque connexion
    """
    pass
