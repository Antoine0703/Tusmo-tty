##
#####################################
## Tusmo
## BEAL Antoine  // EPITECH
## client.py
## Code pour rejoindre une partie(client)
#####################################
##

import socket

def play_game():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('192.168.1.12', 9999))

    name = input("Enter your name: ")
    client.send(name.encode('utf-8'))

    while True:
        response = client.recv(4096).decode('utf-8')
        if not response:
            break
        print(response, end='')

        if "The game is starting!" in response:
            break

        if "Congratulations" in response or "Sorry" in response:
            print(response)
            break

        if "Waiting for the host to start the game" in response:
            continue

        if "Type 'start' to begin the game." in response:
            command = input()
            client.send(command.encode('utf-8'))
            continue
    while True:
        response = client.recv(4096).decode('utf-8')
        if not response:
            break
        print(response, end='')

        if "Guess the word: " in response:
            guess = input()
            client.send(guess.encode('utf-8'))

        if "Congratulations" in response or "Sorry" in response:
            print(response)
            break
    while True:
        response = client.recv(4096).decode('utf-8')
        if not response:
            break
        print(response, end='')

if __name__ == "__main__":
    play_game()
