---
sidebar_position: 1
---

# Introduction

## Résumé

Le but de ce mini-projet est de réaliser un service de discussion en ligne (Internet Relay Chat ou IRC) en Python.
Il s’agit d’un système client/serveur permettant à des utilisateurs de discuter en direct en s’envoyant des messages.
Les utilisateurs peuvent discuter en groupe à travers des canaux de discussion, mais également deux-à-deux de
manière privée.

Le principe est assez simple : des utilisateurs se connectent à un serveur IRC en utilisant un programme client,
tapent des commandes et le serveur exécute ces commandes. Le réseau IRC est constitué de serveurs connectés entre
eux, sans topologie particulière. Chaque client se connecte à un des serveurs et les commandes (ou messages) qu’il
tape sont communiquées par son serveur de rattachement aux autres serveurs, jusqu’aux clients destinataires.

Les commandes acceptées par un serveur sont assez nombreuses et tout est décrit dans un protocole d´ecrit dans la RFC1459

## Context du projet

Le projet est réalisé dans le cadre du module Programmation concurrente et distribuée, assuré par [Mr Conchon](https://www.lri.fr/~conchon/).

Le projet représente également un point d'entrée au module Blockchain assuré par [Mr Conchon](https://www.lri.fr/~conchon/) également

## Unités d'enseignements :

- [Programmation concurrente et distribuée (2022-2023)](https://www.lri.fr/~conchon/progcd/).
- [Blockchain (2022-2023)](https://www.lri.fr/~conchon/blockchain/)
