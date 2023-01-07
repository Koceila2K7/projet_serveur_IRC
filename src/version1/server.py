import socket
import threading
import time

from enum import Enum


HELP_MSG = """
/away [message] Signale son absence quand on nous envoie un message en priv´e
(en r´eponse un message peut ˆetre envoy´e).
Une nouvelle commande /away r´eactive l’utilisateur.

/help Affiche la liste des commandes disponibles

/invite <nick> Invite un utilisateur sur le canal o`u on se trouve

/join <canal> [cl´e] Permet de rejoindre un canal (prot´eg´e ´eventuellement par une cl´e).
Le canal est cr´e´e s’il n’existe pas.

/list Affiche la liste des canaux sur IRC

/msg [canal|nick] message Pour envoyer un message `a un utilisateur ou sur un canal (o`u on est
pr´esent ou pas). Les arguments canal ou nick sont optionnels.

/names [channel] Affiche les utilisateurs connect´es `a un canal. Si le canal n’est pas sp´ecifi´e,
affiche tous les utilisateurs de tous les canaux.
"""


class CMD(Enum):
    HELP = "/help"
    AWAY = "/away"
    INVITE = "/invite"
    JOIN = "/join"
    LIST = "/list"
    MSG = "/msg"
    NAMES = "/names"


connex_map = {}  # {id: Connex, id: Connex, ...}
connex_lock = threading.Lock()

nickname_map = {}  # {nickname: id, ...}
nickname_lock = threading.Lock()

channels_map = {}  # {chan_id: [nickname, nickname...], ...}
channels_lock = threading.Lock()

# ipv4 AF_INET
# a SOCK STREAM (pour un mode connecte, soit ´ TCP) ou
# SOCK DGRAM (pour un non connecte, soit ´ UDP).
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

IP_ADDRESS = '127.0.0.1'
PORT_NUM = 4321

s.bind((IP_ADDRESS, PORT_NUM))

NB_LISTEN = 3
s.listen(NB_LISTEN)  # ouvrir une prise
# Un appel lsof -n -i4TCP dans le terminal permet de voir ce nouveau service


def receive_message(conn: socket.socket,
                    msg_size: int = 1024, verbose: bool = False):
    data = conn.recv(msg_size).decode()
    split_data = data.split(" ")

    cmd = split_data[0]
    if verbose:
        print(f"cmd {cmd} received")

    if cmd == CMD.HELP.value:
        threading.Thread(target=lambda: conn.send(HELP_MSG.encode())).start()

    if cmd == CMD.NAMES.value:
        def send_names(split_data, conn):
            result = ""
            if len(split_data > 1):  # channel spécifié par le user
                channel = split_data[1]
                with channels_lock:
                    result = "channel users : "+str(channels_map.get(channel))
            else:
                with nickname_lock:
                    # affiche tous les utilisateurs de tous les canaux.
                    result = "all users : "+str(nickname_map.keys())
            conn.send(result.encode())
        threading.Thread(target=send_names, args=(split_data, conn)).start()

    if (verbose):
        print("msg reçu du client : ", data)


class Connex:
    def __init__(self, conn: socket.socket, addr: tuple(str, int)):
        self.conn = conn
        self.addr = addr  # ('127.0.0.1', 35260)
        self.id = addr[0] + ':' + str(addr[1])  # 127.0.0.1:35260
        self.thread_recv = threading.Thread(target=receive_message,
                                            args=(self.conn, 1024, False))
        self.thread_recv.start()


def accept_connexions(max_connexions: int = 10):
    while (True):
        if (len(connex_map) < max_connexions):  # accept the new connextion
            conn, addr = s.accept()  # attendre des connexions sur une prise
            # Un appel a cette methode bloque le programme en attendant qu’un client se connecte a la prise !
            c = Connex(conn, addr)
            connex_map[c.id] = c  # a verifier
            print("connexion de ", c.id)
        else:  # decline the new connexion
            # verification chaque 3 secondes si des places se sont libérées
            time.sleep(3)


def send_message(conn):
    for i in range(3):
        message = input("entrez un msg à envoyer au client : ")
        conn.send(message.encode())


thread_connex = threading.Thread(target=accept_connexions)
thread_connex.start()

# thread_recv = threading.Thread(target=cmd_router)
# thread_recv.start()

# thread_send = threading.Thread(target=send_message)
# thread_send.start()

# thread_recv.join()
# thread_send.join()

# conn.close()

# r, w, e = select(p,[],[],to)  ? voir cours
