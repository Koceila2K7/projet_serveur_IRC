---
sidebar_position: 3
---

# Version Peer To Peer

## Introduction

Dans cette version chaque client est un serveur en même temps

![peer to peer](./img/p2p.png)

## Explication de notre implémentation :

Nous avons défini un Nœud de fondation, ce dernier sera le point d'entré au réseau.

Au lancement tout les Nœud se connectent au noued de fondation, et ils demandent les voisins de ce dernier, à la reception des voisins, si le nombre est inferieur à une constantes défini, on garde la connexion au serveur, dans le cas contraire on prend les voisins (serveur de fondation inclu) on prend deux au hasard et on se connecte à eux.

![peer to peer](./img/diagramme_de_sequence.png)

Pour éviter des cycle de broad cast nous avons met en place un système d'empreinte ce qui permet de savoir si nous avons déja traiter le message dont il est question
