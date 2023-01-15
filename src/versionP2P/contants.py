from enum import Enum
import copy

HELP_MSG = """
/away [message] Signale son absence quand on nous envoie un message en privé
(en réponse un message peut etre envoye).
Une nouvelle commande /away reactive l’utilisateur.

/help Affiche la liste des commandes disponibles

/invite <nick> Invite un utilisateur sur le canal ou on se trouve

/join <canal> [cle] Permet de rejoindre un canal (protege eventuellement par une cle).
Le canal est cree s’il n’existe pas.

/list Affiche la liste des canaux sur IRC

/msg [canal|nick] : message Pour envoyer un message a un utilisateur ou sur un canal (ou on est
present ou pas). Ne pas oublier de mettre les ":" pour marquer le début du message.
Les arguments canal ou nick sont optionnels.

/names [channel] Affiche les utilisateurs connectes a un canal. Si le canal n’est pas specifie,
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


LIST_EMPREINTE_KEY = 'list_empreinte'


def signer_un_message(uuid: str, message: dict) -> dict:
    """
    Cette méthode permet de signer un message avec notre UUID
    Aucun effet de bord (le message initial est copier[deep_copie])
    """
    new_message = copy.deepcopy(message)
    new_message.get(LIST_EMPREINTE_KEY).append(uuid)
    return new_message
