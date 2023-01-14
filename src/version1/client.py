import socket
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Cet appel est bloquant tant que la connexion ne s’est pas etablie.
s.connect(('127.0.0.1', 4321))

# send nickname to server
nickname = input("enter your nickname : ")
s.send(("/set_nickname "+nickname.strip()).encode())


def receive_message():
    while (True):
        data = s.recv(1024).decode()
        print("=>", data)


def send_message():
    while (True):
        message = input(">")
        s.send(message.encode())
        if message == "/exit":
            s.close()
            break


thread_recv = threading.Thread(target=receive_message)
thread_recv.start()

thread_send = threading.Thread(target=send_message)
thread_send.start()

thread_recv.join()
thread_send.join()

s.close()
