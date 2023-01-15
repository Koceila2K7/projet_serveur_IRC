# Description des fonctionalités comment les utiliser :

## Envoi de message :

```bash
/msg [canal|nick] message
```

Dans le cas d'un nickname, faire suivre le message à la personne, si le serveur à une connexion qui correspond.
Dans le cas d'un canal, l'expéditeur est dans le canal, faire suivre le message à tout les users du groupe.

## Message d'absence :

```bash
/away [message]
```

Dès que on essaie de nous joindre le serveur répond par ce message
**le serveur ne répond pas dans le cas d'un message de groupe**

## Gestion de groupes (channels) :

Un utilisateur peut joindre pleusieurs groupes.

### Inviter un user :

```bash
/invite <nick>
```

Permet t'ajouter un user au dernier groupe **actif** de l'utilisateur courant.

### Liste des utilisateur du chanel :

```bash
/names <nick>
```

Retourne la liste des utilisateur, si l'utilisateur qui la demande fait parti du groupe.

## Gestion de l'affection des users names :

Nous avons mis en place une commande qui est setmynickname

```bash
/setmynickname <nick>
```

le serveur répond par une confirmation si le nom n'est pas déja utilisé, dans le cas contraire un message d'erreur est retourné
