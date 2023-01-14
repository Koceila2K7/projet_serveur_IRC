import socket
import threading
import time
from contants import CMD, HELP_MSG
from typing import List, Dict

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

s.bind((IP_ADDRESS, PORT_NUM))

NB_LISTEN = 3
s.listen(NB_LISTEN)  # ouvrir une prise
# Un appel lsof -n -i4TCP dans le terminal permet de voir ce nouveau service


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


def find_user_channel(user_nick_name: str,
                      channel_dict: Dict[str, List[str]]) -> str:
    """
    Cette fonction permet de trouver le channel d'un user par son nickname
    ** La fonction ne gère pas l'acquisition de verou
    """
    for channel_name in channel_dict.keys():
        if user_nick_name in channel_dict.get(channel_name):
            return channel_name

    return None


def find_user_nickname_by_conx_id(id: str,
                                  nickname_dict: Dict[str, str]) -> str:
    """
    cette fonction permet de retrouver le nickname d'une connexion
    *** Cette fonction ne gère pas l'acquisition de verou
    """
    for nickname in nickname_dict.keys():
        if nickname_dict.get(nickname) == id:
            return nickname

    return None


def get_conn_by_nickname(nickname: str) -> socket.socket:
    """
    retourne l'objet socket correspondant au user donné
    """
    id = None
    with nickname_lock:
        id = nickname_map.get(nickname)

    connex = None
    with connex_lock:
        connex = connex_map.get(id)

    conn = connex.conn if connex is not None else None
    return conn


def send_message_to_nickname(msg: str, my_nickname: str, to_nickname: str):
    """
    fonction à surpprimer ou a modifier si on l'utilise ?
    """
    # si user inactif, on reçoit son message d'absense
    away_msg = None
    with away_messages_lock:
        if to_nickname in away_messages:
            away_msg = away_messages.get(to_nickname)
    # je reçois son message d'absence
    if away_msg is not None:
        my_conn = get_conn_by_nickname(my_nickname)
        threading.Thread(target=lambda: my_conn.send(
            away_msg.encode())).start()

    # envoi du message au destinataire
    conn = get_conn_by_nickname(to_nickname)
    threading.Thread(target=lambda: conn.send(msg.encode())).start()


def send_message_to_channel(msg: str, my_nickname: str, to_channel: str):
    """
    envoyer un message à tous les users dans le channel donné
    """
    users_list = None
    with channels_lock:
        users_list = channels_map.get(to_channel)

    if users_list is not None and len(users_list) > 0:
        for user in users_list:
            send_message_to_nickname(msg, my_nickname, user)


def receive_message(conn: socket.socket,
                    connexion_id: str,
                    msg_size: int = 1024,
                    verbose: bool = False,
                    ):
    """
    Fonction qui va gérer les messages pour chaque connexion
    """
    while (True):
        data = conn.recv(msg_size).decode()  # doit etre bloquant

        if data == "/exit":
            conn.close
            # user inactif ??
            break

        split_data = data.split(" ")

        cmd = split_data[0]
        if verbose:
            print(f"cmd {cmd} received")

        # si première connexion de l'utilisateur (envoyée automatiquement)
        if cmd == "/add_user" and len(split_data) == 2:
            nickname = split_data[1]
            with nickname_lock:
                nickname_map[nickname] = connexion_id
                print(f"nickname_map[{nickname}] = {connexion_id}")

        # DEBUT FUNCTION
        if cmd == "/debug":
            print("connex_map: ", connex_map, end="\n\n")
            print("nickname_map: ", nickname_map, end="\n\n")
            print("channels_map: ", channels_map, end="\n\n")
            print("channels_keys: ", channels_keys, end="\n\n")
            print("away_messages: ", away_messages, end="\n\n")

        if cmd == CMD.HELP.value:
            threading.Thread(target=lambda: conn.send(
                HELP_MSG.encode())).start()

        if cmd == CMD.NAMES.value:
            def send_names(split_data, conn):
                result = ""
                if len(split_data) > 1:  # channel spécifié par le user
                    channel = split_data[1]
                    with channels_lock:
                        result = "channel users : " + \
                            str(channels_map.get(channel))
                else:
                    with nickname_lock:
                        # affiche tous les utilisateurs de tous les canaux.
                        result = "all users : "+str(nickname_map.keys())
                conn.send(result.encode())
            threading.Thread(target=send_names, args=(
                split_data, conn)).start()

        if cmd == CMD.INVITE.value:
            def add_user_to_channel(splited_data: List[str], conn: socket.socket):
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
            def join_channel(split_data: list, marche: str = ""):
                my_nickname = None
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
                            # on le retire s'il existe dans d'autres channels
                            my_channel_name = find_user_channel(
                                my_nickname, channel_dict=channels_map)
                            if my_channel_name is not None:
                                channels_map.get(my_channel_name).remove(
                                    my_nickname)

                            # on le crée et on ajoute le user et on met à jour la clé
                            channels_map[channel] = [my_nickname]

                            # cle du channel si doonnée
                            if cle:
                                channels_keys[channel] = cle

                        # si channel existe, on vérifie la clé
                        # si elle correspond on ajoute le user, on le retire aussi des autres channels #
                        else:
                            print()
                            if cle == channels_keys.get(channel):
                                # on le retire s'il existe dans d'autres channels
                                my_channel_name = find_user_channel(
                                    my_nickname, channel_dict=channels_map)
                                if my_channel_name is not None:
                                    channels_map.get(my_channel_name).remove(
                                        my_nickname)

                                with nickname_lock:  # nickname
                                    my_nickname = find_user_nickname_by_conx_id(
                                        id=connexion_id,
                                        nickname_dict=nickname_map)
                                # on l'ajoute dans tous les cas au channel
                                channels_map[channel].append(my_nickname)
                                print("channels_map.get(channel)=",
                                      channels_map.get(channel))
                                print("-- channel=", channel,
                                      "my_nickname=", my_nickname)

                            elif verbose:
                                print(f"invalid key for channel {channel}")
                    if verbose:
                        print(
                            f"user {my_nickname} \
                            added to channel {channel}")
                    print("-- channels_lock fin")

            print("split data = ", split_data)
            threading.Thread(target=join_channel,
                             args=(split_data, "")).start()

        if cmd == CMD.LIST.value:
            def list_channels(channels_map, channels_lock):
                with channels_lock:
                    msg = str(channels_map.keys())
                    conn.send(msg.encode())
            # vérifier si le thread a accès aux variables
            threading.Thread(target=list_channels, args=(
                channels_map, channels_lock)).start()

        if cmd == CMD.AWAY.value:
            # Signale son absence quand on nous envoie un message en privé
            def away_msg(splited_data: List[str], join_char=" "):
                # à voir si on renvoi une response à cette commande
                if len(splited_data) > 1:
                    msg = " ".join(splited_data[1:])
                    with nickname_lock:
                        my_nickname = find_user_nickname_by_conx_id(
                            id=connexion_id, nickname_dict=nickname_map)
                    with away_messages_lock:
                        away_messages[my_nickname] = msg
                    if verbose:
                        print(
                            f"away message ''{msg}'' added to user {my_nickname}")

            threading.Thread(target=away_msg,
                             args=(split_data, " ")).start()

        if cmd == CMD.MSG.value:
            def msg_canal_or_nick(split_data: List[str], debug=""):
                """"
                /msg [canal|nick] message Pour envoyer un message à un user
                ou sur un canal (où on est pr esent ou pas).
                Les arguments canal ou nick sont optionnels !
                donc si j'envoi juste un msg sans préciser user/canal,
                le msg sera envoyé à mon canal
                - doit gérer aussi les away messages ? ou ce sera géré par send_message ?
                """
                if len(split_data) in [2, 3]:  # sinon on fait rien

                    msg = split_data[2] if len(
                        split_data) == 3 else split_data[1]
                    chan_or_nick = split_data[1] if len(
                        split_data) == 3 else None

                    with nickname_lock:
                        my_nickname = find_user_nickname_by_conx_id(
                            id=connexion_id, nickname_dict=nickname_map)

                    with channels_lock:
                        # si pas de canal/nickname specifié
                        if chan_or_nick is None:
                            my_channel = find_user_channel(
                                my_nickname, channel_dict=channels_map)
                            send_message_to_channel(
                                msg, my_nickname, my_channel)
                            if (verbose):
                                print(f"msg envoyé à mon canal {my_channel}")

                        # canal specifié
                        elif chan_or_nick in channels_map:
                            channel = chan_or_nick
                            send_message_to_channel(msg, my_nickname, channel)
                            if (verbose):
                                print(f"msg envoyé au canal externe {channel}")

                        # nickname specifié
                        elif chan_or_nick in nickname_map:
                            nickname = chan_or_nick
                            send_message_to_nickname(
                                msg, my_nickname, nickname)
                            if (verbose):
                                print(f"msg envoyé au user {nickname}")

            threading.Thread(target=msg_canal_or_nick,
                             args=(split_data, "")).start()


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


thread_connex = threading.Thread(target=accept_connexions)
thread_connex.start()
print("-- server started --\n")

# conn.close()

# r, w, e = select(p,[],[],to)  ? voir cours
