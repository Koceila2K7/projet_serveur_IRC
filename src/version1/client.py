import socket
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Cet appel est bloquant tant que la connexion ne s’est pas etablie.
s.connect(('127.0.0.1', 4321))

# send nickname to server


def receive_message():
    for i in range(3):
        data = s.recv(1024).decode()
        print("msg reçu du serveur :", data)


def send_message():
    for i in range(3):
        message = input("entrez un msg à envoyer au serveur : ")
        s.send(message.encode())


thread_recv = threading.Thread(target=receive_message)
thread_recv.start()

thread_send = threading.Thread(target=send_message)
thread_send.start()

thread_recv.join()
thread_send.join()

s.close()
