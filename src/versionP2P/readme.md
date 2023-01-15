# Ce document décrit comment notre réseau P2P fonctionne

# Pour simplifier le projet et le rendre réalisable en quelques semaines :

On fixera en dur l'addresse d'un client de fondation, ce client servera d'un point d'entrée au réseau
Pour simuler un mécanisme de signature, à chaque passage d'un serveur le message sera augmenté de la signature du serveur.<br/>
Ceci permet d'éviter les cycle de broadcast.

# Strcuture des messages

```bash
{
    "uuid":"un_id_unique", [https://datatracker.ietf.org/doc/html/rfc4122.html]
    "type":"MESSAGE_CLIENT_TO_CLIENT | BROAD_CAST ....",
    "ID_EXP":"",
    "SELON LE TYPE on ajoutera les champs":""
    "list_empreinte":[], // Pour des raisons de simplicité on utilisera str(uuid.uuid4()) pour générer les empreintes.
}

```
