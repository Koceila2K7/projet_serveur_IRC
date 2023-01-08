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
