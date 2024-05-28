##
#####################################
## Tusmo
## BEAL Antoine // EPITECH
## serveur.py
## Code pour créer le serveur
#####################################
##

import socket
import threading
import random
import time

def generate_secret_word():
    words = ['angle', 'armoire', 'banc', 'bureau', 'cabinet', 'carreau', 'chaise', 'classe', 'coin', 'couloir', 'dossier', 'eau', 'escalier', 'lavabo', 'lecture', 'lit', 'marche', 'matelas', 'allumette', 'anniversaire', 'beurre', 'coquille', 'dessert', 'envie', 'faim', 'four', 'galette', 'invitation', 'liquide', 'louche', 'moule', 'odeur', 'part', 'recette', 'rouleau', 'sel', 'soif', 'tarte', 'tranche', 'fruit', 'haricot', 'huile', 'marchand', 'melon', 'monnaie', 'navet', 'noisette', 'noix', 'nourriture', 'oignon', 'orange', 'panier', 'persil', ' poire', 'poireau', 'pomme', 'prix', 'prune', 'raisin', 'riz', 'salade', 'sucre', 'tomate', 'viande']
    return random.choice(words)

def check_guess(guess, secret_word):
    correct_letters = [0] * len(secret_word)
    for i in range(len(secret_word)):
        if secret_word[i] == guess[i]:
            correct_letters[i] = 1

    result = []
    for i in range(len(secret_word)):
        if correct_letters[i] == 1:
            result.append(f'\033[31m{guess[i].upper()}\033[0m')
        elif guess[i] in secret_word:
            result.append(f'\033[33m{guess[i]}\033[0m')
        else:
            result.append("_")
    return ' '.join(result), guess == secret_word

def handle_client(client_socket, secret_word, players, player_name, game_started, results_lock, results, connections, finished_players):
    game_started.wait()
    attempts = 10
    client_socket.send(f"The word has {len(secret_word)} letters.\n".encode('utf-8'))

    start_time = time.time()

    while attempts > 0:
        client_socket.send("Guess the word: ".encode('utf-8'))
        try:
            guess = client_socket.recv(1024).decode('utf-8').strip()
        except ConnectionResetError:
            print(f"Connection with {player_name} lost.")
            break
        if not guess:
            continue
        if len(guess) != len(secret_word):
            client_socket.send(f"Please enter a word of length {len(secret_word)}.\n".encode('utf-8'))
            continue

        result, correct = check_guess(guess, secret_word)
        try:
            client_socket.send(f"{result}\n".encode('utf-8'))
        except OSError as e:
            print(f"Error sending result to {player_name}: {e}")
            break

        if correct:
            finish_time = time.time() - start_time
            with results_lock:
                if player_name not in results:
                    results[player_name] = (attempts, finish_time)
            client_socket.send("Congratulations! You've guessed the word.\n".encode('utf-8'))
            players[player_name] = True
            break
        else:
            attempts -= 1
            try:
                client_socket.send(f"Incorrect guess. You have {attempts} attempts left.\n".encode('utf-8'))
            except OSError as e:
                print(f"Error sending attempts left to {player_name}: {e}")
                break

    if not correct:
        client_socket.send(f"Sorry, you didn't guess the word. The word was {secret_word}.\n".encode('utf-8'))
        players[player_name] = True

    with results_lock:
        finished_players.append(player_name)
        if len(finished_players) == len(players):
            game_over = True

    while len(finished_players) < len(players):
        time.sleep(1)

    with results_lock:
        sorted_results = sorted(results.items(), key=lambda item: (item[1][0], -item[1][1]), reverse=True)
        result_message = "Game over! Here are the results:\n"
        for player, (attempts, _) in sorted_results:
            result_message += f"{player} won with {attempts} attempts remaining.\n"
        try:
            client_socket.send(result_message.encode('utf-8'))
        except OSError as e:
            print(f"Error sending results to {player_name}: {e}")

    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))
    server.listen(5)
    print("Server started on port 9999")

    players = {}
    connections = []
    secret_word = generate_secret_word()
    game_started = threading.Event()
    results = {}
    results_lock = threading.Lock()
    finished_players = []

    def wait_for_start():
        host_set = False
        while True:
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr}")

            client_socket.send("Enter your name: ".encode('utf-8'))
            player_name = client_socket.recv(1024).decode('utf-8').strip()
            players[player_name] = False

            connections.append((client_socket, player_name))
            print(f"Player {player_name} connected")

            if not host_set:
                host_set = True
                client_socket.send("You are the host. Type 'start' to begin the game.\n".encode('utf-8'))
                def host_wait_for_start():
                    while True:
                        command = client_socket.recv(1024).decode('utf-8').strip()
                        if command.lower() == 'start':
                            for conn, _ in connections:
                                conn.send("The game is starting!\n".encode('utf-8'))
                            game_started.set()
                            break
                threading.Thread(target=host_wait_for_start).start()
            else:
                client_socket.send("Waiting for the host to start the game...\n".encode('utf-8'))

    threading.Thread(target=wait_for_start).start()

    game_started.wait()
    
    client_threads = []
    for client_socket, player_name in connections:
        client_handler = threading.Thread(target=handle_client, args=(client_socket, secret_word, players, player_name, game_started, results_lock, results, connections, finished_players))
        client_threads.append(client_handler)
        client_handler.start()

    for thread in client_threads:
        thread.join()

    server.close()

if __name__ == "__main__":
    start_server()
