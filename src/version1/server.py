import socket
import threading
import time
from contants import CMD, HELP_MSG

connex_map = {}  # {id: Connex, id: Connex, ...}
connex_lock = threading.Lock()

nickname_map = {}  # {nickname: id, ...}
nickname_lock = threading.Lock()

channels_map: dict[str, list] = {}  # {chan_id: [nickname, nickname...], ...}
channels_lock = threading.Lock()

channels_keys: dict[str, str] = {}  # {chan_id: key, ...}
# if channel dont have key or dont exist, channels_keys.get(channel) returns None

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


def find_user_channel(user_nick_name: str,
                      channel_dict: dict[str, list[str]]) -> str:
    """
    Cette fonction permet de trouver le channel d'un user par son nickname
    ** La fonction ne gère pas l'acquisition de verou
    """
    for channel_name in channel_dict.keys():
        if user_nick_name in channel_dict.get(channel_name):
            return channel_name

    return None


def find_user_nickname_by_conx_id(id: str,
                                  nickname_dict: dict[str, str]) -> str:
    """
    cette fonction permet de retrouver le nickname d'une connexion
    *** Cette fonction ne gère pas l'acquisition de verou
    """
    for nickname in nickname_dict.keys():
        if nickname_dict.get(nickname) == id:
            return nickname

    return None


def receive_message(conn: socket.socket,
                    connexion_id: str,
                    msg_size: int = 1024,
                    verbose: bool = False,
                    ):
    """
    Fonction qui va gérer les messages pour chaque connexion
    """
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
            if len(split_data) > 1:  # channel spécifié par le user
                channel = split_data[1]
                with channels_lock:
                    result = "channel users : "+str(channels_map.get(channel))
            else:
                with nickname_lock:
                    # affiche tous les utilisateurs de tous les canaux.
                    result = "all users : "+str(nickname_map.keys())
            conn.send(result.encode())
        threading.Thread(target=send_names, args=(split_data, conn)).start()

    if cmd == CMD.INVITE.value:
        def add_user_to_channel(splited_data: list[str], conn: socket.socket):
            # à voir si on renvoi une response à cette commande
            if len(splited_data) > 1:
                new_user_nick_name = splited_data[1]
                with nickname_lock:
                    my_nickname = find_user_nickname_by_conx_id(
                        id=connexion_id, nickname_dict=nickname_map)

                # On suppose qu'un user ne peut être  présent que dans un seul groupe

                with channels_lock:
                    if my_nickname is not None:
                        # trouver l'ancien channel
                        # s'il existe on supprime l'utilisateur de ce dernier
                        old_chanel = find_user_channel(
                            new_user_nick_name, channel_dict=channels_map)
                        if old_chanel is not None:
                            channels_map.get(old_chanel).remove(
                                new_user_nick_name)

                        my_channel_name = find_user_channel(
                            my_nickname, channel_dict=channels_map)

                        if my_channel_name is not None:
                            channels_map.get(my_channel_name).append(
                                new_user_nick_name)
        threading.Thread(target=add_user_to_channel,
                         args=(split_data, conn)).start()

    if cmd == CMD.JOIN.value:  # /join <canal> [clé]
        if len(split_data) >= 2:
            channel = split_data[1]
            cle = None  # par defaut si channel n'as pas de clé
            if len(split_data) >= 3:  # on ignore les autres arguments s'ils existent dans ce cas
                cle = split_data[2]

            with nickname_lock:  # nickname
                my_nickname = find_user_nickname_by_conx_id(
                    id=connexion_id, nickname_dict=nickname_map)

            with channels_lock:
                if channel not in channels_map:  # channel n'existe pas
                    # on le crée et on ajoute le user et on met à jour la clé
                    channels_map[channel] = [my_nickname]
                    if cle:
                        channels_keys[channel] = cle

                # si channel existe, on vérifie la clé, si elle correspond on ajoute le user.
                else:
                    if cle == channels_keys.get(channel):
                        channels_map[channel] = channels_map.get(
                            channel).append(my_nickname)
                    elif verbose:
                        print(f"invalid key for channel {channel}")

    if (verbose):
        print("msg reçu du client : ", data)


class Connex:
    """
    class qui décrit une connexion 
    """

    def __init__(self, conn: socket.socket, addr: tuple(str, int)):
        self.conn = conn
        self.addr = addr  # ('127.0.0.1', 35260)
        self.id = addr[0] + ':' + str(addr[1])  # 127.0.0.1:35260
        self.thread_recv = threading.Thread(target=receive_message,
                                            args=(self.conn, self.id, ))
        self.thread_recv.start()


def accept_connexions(max_connexions: int = 10):
    """
    fonction principale du serveur pour gérer toute nouvelle connexion
    """
    while (True):
        if (len(connex_map) < max_connexions):  # accept the new connextion
            conn, addr = s.accept()  # attendre des connexions sur une prise
            # Un appel a cette methode bloque le programme en attendant qu’un
            #  client se connecte a la prise !
            c = Connex(conn, addr)
            connex_map[c.id] = c  # a verifier
            print("connexion de ", c.id)
        else:  # decline the new connexion
            # verification chaque 3 secondes si des places se sont libérées
            time.sleep(3)


def send_message(conn):
    """
    fonction à surpprimer
    """
    for _ in range(3):
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
