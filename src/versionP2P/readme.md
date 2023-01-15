# Ce document décrit comment notre réseau P2P fonctionne

# Pour simplifier le projet et le rendre réalisable en quelques semaines :

On fixera en dur l'addresse d'un client de fondation, ce client servera d'un point d'entrée au réseau
Pour simuler un mécanisme de signature, à chaque passage d'un serveur le message sera augmenté de la signature du serveur.<br/>
Ceci permet d'éviter les cycle de broadcast.
