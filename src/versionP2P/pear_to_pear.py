from distutils.util import change_root
import socket
import threading
import sys
from contants import CMD, HELP_MSG, MESSAGE_TYPES, est_ce_que_j_ai_signer_ce_message
from typing import List, Dict
import uuid
import json
voisins: Dict = {}  # {id:nickname, id:nickname}
# or  {(nickname, id), (nickname, id), ...} ???

connex_map = {}  # {id: Connex, id: Connex, ...}
connex_lock = threading.Lock()

nickname_map = {}  # {nickname: id, ...}
nickname_lock = threading.Lock()

channels_map: Dict[str, list] = {}  # {chan_id: [nickname, nickname...], ...}
channels_lock = threading.RLock()

channels_keys: Dict[str, str] = {}  # {chan_id: key, ...}
# if channel dont have key or dont exist, channels_keys.get(channel) returns None

away_messages = {}  # {nickname: msg, nickname: msg,...}
away_messages_lock = threading.Lock()

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


MY_KEY_NAME = str(uuid.uuid4())
MY_SIGNATURE_KEY = str(uuid.uuid4())

if first_node:
    print("-- first node to be started --")
else:
    s.connect((IP_ADDRESS, PORT_NUM))

_nickname = input("enter your nickname : ")


if first_node:
    s.bind((IP_ADDRESS, PORT_NUM))
    s.listen()  # ouvrir une prise

# a modifier : demander au first_node ses voisins pour se connecter à l'un d'eux ?
# mais il faut donc se déconnecter du first node
else:
    message_id = str(uuid.uuid4())

    message = {"type": MESSAGE_TYPES.VOISINS.value,
               "message_id": message_id,
               "id_exp": MY_KEY_NAME,
               "list_empreinte": [MY_SIGNATURE_KEY]}

    s.send(json.dumps(message).encode())
    # attente de la réponse du serveur de fondation
    # implémentation naive
    voisins = []
    while True:
        response = s.recv(1024)
        response = json.loads(response)
        if response['id_rec'] == MY_KEY_NAME\
                and est_ce_que_j_ai_signer_ce_message(MY_SIGNATURE_KEY,
                                                      response)\
                and response['type'] == MESSAGE_TYPES.VOISINS_RESPONSE.value:
            voisins = response['payload']
            break

    # il faut attendre la réponse du serveur de fondation.
    s.send()


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


def accept_connexions():
    """
    fonction principale du serveur pour gérer toute nouvelle connexion
    """
    while (True):
        conn, addr = s.accept()  # attendre des connexions sur une prise
        # Un appel a cette methode bloque le programme en attendant qu’un
        #  client se connecte a la prise
        c = Connex(conn, addr)
        connex_map[c.id] = c  # a verifier

        # p2p
        nickname = None  # to be sent soon ! using set_nicknanme ????????????????????????
        voisins.add[c.id] = nickname  # ?

        print("connexion de ", c.id)
