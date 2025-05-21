import utils.session
import random
import time 
import os 
import sys
import platform


time_ = 5
patternlength = 5
name = None
last_guessed_pattern = ""
score = 0

def clear_console():
    system_platform = platform.system()
    if system_platform == 'Windows':
        os.system('cls')
    else:
        os.system('clear')
    print()


def homepage():

    while True:
        print("============================================================".center(100))
        print("|                                                          |".center(100))
        print("|                       Welcome to                         |".center(100))
        print("|                                                          |".center(100))
        print("|                    TYPE THE PATTERN                      |".center(100))
        print("|                Are you ready to battle?                  |".center(100))
        print("|                                                          |".center(100))
        print("|                     (1) PLAY                             |".center(100))
        print("|                     (2) LEADERBOARD                      |".center(100))
        print("|                     (3) QUIT                             |".center(100))
        print("|                                                          |".center(100))
        print("============================================================".center(100))

        choice = input("Enter choice (number only): ".rjust(60))

        if choice.isdigit():
                choice = int(choice)
                if 1 <= choice <= 3:
                    clear_console()
                    return choice
                elif choice == 3:
                    saveleaderboard(scores, name, score, last_guessed_pattern)
                    print("============================================================".center(100))
                    print(" ")
                    print(" ")
                    print(" ")
                    print("Thanks for playing!".center(100))
                    print(" ")
                    print(" ")
                    print(" ")
                    print("============================================================".center(100))
                    sys.exit()
                
        print("Invalid choice. Please enter a valid option (1-3).")

        clear_console()

def countdown(t, width=100): 
    while t: 
        mins, secs = divmod(t, 60) 
        timer = '{:02d}:{:02d}'.format(mins, secs) 
        print(timer.center(width), end='\r')
        time.sleep(1) 
        t -= 1
    
    print("\nTime's up!".center(width))

def patterneasy(length):
    
    characters = "abcdefghijklmnopqrstuvwxyz"

    return ''.join(random.choice(characters) for _ in range(length))

def patternmedium(length):
    characters = "abcdefghijklmnopqrstuvwxyz"
    characters += "0123456789"

    return ''.join(random.choice(characters) for _ in range(length))

def patternhard(length):
    characters = "abcdefghijklmnopqrstuvwxyz"
    characters += "0123456789"
    characters += "!@#$%^&*()_+[]{}|;:,.<>?"

    return ''.join(random.choice(characters) for _ in range(length))

def play(choice):

    global name
    global score
    global last_guessed_pattern
    
    if choice == 1:
        print("============================================================".center(100))
        print("|                                                          |".center(100))
        print("|                        >> PLAY                           |".center(100))
        print("|                                                          |".center(100))
        print("|                Choose Difficulty Level:                  |".center(100))
        print("|                                                          |".center(100))
        print("|                       (1) EASY                           |".center(100))
        print("|                       (2) MEDIUM                         |".center(100))
        print("|                       (3) HARD                           |".center(100))
        print("|                                                          |".center(100))
        print("============================================================".center(100))


        difficultylevel = input("Enter choice (number only): ".rjust(60))

        if difficultylevel.isdigit():
                difficultylevel = int(difficultylevel)
                if 1 <= difficultylevel <= 3:
                    return difficultylevel
                
        print("Invalid choice. Please enter a valid option (1-3).".rjust(60))

        os.system('cls')

        if choice == 1:
            difficultylevel = play(choice)
            clear_console()

            if difficultylevel == 1:
                round_score, last_guessed_pattern = easydifficulty(scores)
            elif difficultylevel == 2:
                round_score, last_guessed_pattern = mediumdifficulty(scores)
            elif difficultylevel == 3:
                round_score, last_guessed_pattern = harddifficulty(scores)

            if round_score is not None:
                score += round_score
                saveleaderboard(scores, name, round_score, last_guessed_pattern)
                clear_console()

        elif choice == 2:
            viewleaderboard(scores)

    return difficultylevel

def easydifficulty(scores):
    global time_
    global patternlength
    global score
    global name
    global last_guessed_pattern
    

    score = 0
    guesspattern = patterneasy(patternlength)

    print("\n" * 2)
    print("PRESS ENTER TO START".center(100))
    input()
    clear_console()

    print("============================================================".center(100))
    print(" ".center(100))
    print("                  REMEMBER THE PATTERN!                   ".center(100))
    print(" ".center(100))
    print(f"{guesspattern}".center(100))
    print(" ".center(100))
    print("============================================================".center(100))
    print(" ".center(100))
    print(" ".center(100))
    countdown(int(time_))
    print(" ".center(100))

    clear_console()

    print(" ".center(100))
    print(" ".center(100))
    print(" ".center(100))
    user_input = input("ENTER THE PATTERN: ".rjust(53))
    print("\n")

    answer = user_input

    if answer == guesspattern:
        score += 10
        patternlength += 1
        last_guessed_pattern = guesspattern

        print("============================================================".center(100))
        print("|                                                          |".center(100))
        print("|                       CORRECT!                           |".center(100))
        print("|                                                          |".center(100))
        print("|           Do you want to continue playing?               |".center(100))
        print("|                                                          |".center(100))
        print("|                       (1) YES                            |".center(100))
        print("|                       (2) NO                             |".center(100))
        print("|                                                          |".center(100))
        print("============================================================".center(100))

        cont = input("Enter your choice (1 or 2): ".rjust(60))

        if cont == '1':
            scores = saveleaderboard(scores, name, score, last_guessed_pattern)
            clear_console()
            last_guessed_pattern = easydifficulty(scores)

        else:
            scores = saveleaderboard(scores, name, score, last_guessed_pattern)
            clear_console()
            viewleaderboard(scores)
            return score

        return score, last_guessed_pattern 

    else:
        while True:
            print("============================================================".center(100))
            print("|                                                          |".center(100))
            print("|                                                          |".center(100))
            print("|                      GAME OVER :(                        |".center(100))
            print("|               Do you want to try again?                  |".center(100))
            print("|                        (1) YES                           |".center(100))
            print("|                        (2) NO                            |".center(100))
            print("|                                                          |".center(100))
            print("|                                                          |".center(100))
            print("============================================================".center(100))

            cont_2 = input("Enter your choice (1 or 2): ".rjust(60))

            if cont_2.isdigit() and 1 <= int(cont_2) <= 2:
                cont_2 = int(cont_2)

                if cont_2 == 1:
                    clear_console()
                    scores = saveleaderboard(scores, name, score, last_guessed_pattern)
                    return easydifficulty(scores)

                elif cont_2 == 2:
                    scores = saveleaderboard(scores, name, score, last_guessed_pattern)
                    clear_console()
                    return score

            else:
                print("Invalid choice. Please enter a valid option (1-2).")

            return 0
            
        return 0, last_guessed_pattern

def mediumdifficulty(scores):
    global time_
    global patternlength
    global score
    global name
    global last_guessed_pattern
    

    score = 0
    guesspattern = patternmedium(patternlength)

    print("\n" * 2)
    print("PRESS ENTER TO START".center(100))
    input()
    clear_console()

    print("============================================================".center(100))
    print(" ".center(100))
    print("                  REMEMBER THE PATTERN!                   ".center(100))
    print(" ".center(100))
    print(f"{guesspattern}".center(100))
    print(" ".center(100))
    print("============================================================".center(100))
    print(" ".center(100))
    print(" ".center(100))
    countdown(int(time_))
    print(" ".center(100))

    clear_console()

    print(" ".center(100))
    print(" ".center(100))
    print(" ".center(100))
    user_input = input("ENTER THE PATTERN: ".rjust(53))
    print("\n")

    answer = user_input

    if answer == guesspattern:
        score += 25
        patternlength += 1
        last_guessed_pattern = guesspattern

        print("============================================================".center(100))
        print("|                                                          |".center(100))
        print("|                       CORRECT!                           |".center(100))
        print("|                                                          |".center(100))
        print("|           Do you want to continue playing?               |".center(100))
        print("|                                                          |".center(100))
        print("|                       (1) YES                            |".center(100))
        print("|                       (2) NO                             |".center(100))
        print("|                                                          |".center(100))
        print("============================================================".center(100))

        cont = input("Enter your choice (1 or 2): ".rjust(60))

        if cont == '1':
            scores = saveleaderboard(scores, name, score, last_guessed_pattern)
            clear_console()
            last_guessed_pattern = mediumdifficulty(scores)

        else:
            scores = saveleaderboard(scores, name, score, last_guessed_pattern)
            clear_console()
            viewleaderboard(scores)
            return score

        return score, last_guessed_pattern 

    else:
        while True:
            print("============================================================".center(100))
            print("|                                                          |".center(100))
            print("|                                                          |".center(100))
            print("|                      GAME OVER :(                        |".center(100))
            print("|               Do you want to try again?                  |".center(100))
            print("|                        (1) YES                           |".center(100))
            print("|                        (2) NO                            |".center(100))
            print("|                                                          |".center(100))
            print("|                                                          |".center(100))
            print("============================================================".center(100))

            cont_2 = input("Enter your choice (1 or 2): ".rjust(60))

            if cont_2.isdigit() and 1 <= int(cont_2) <= 2:
                cont_2 = int(cont_2)

                if cont_2 == 1:
                    clear_console()
                    scores = saveleaderboard(scores, name, score, last_guessed_pattern)
                    return mediumdifficulty(scores)

                elif cont_2 == 2:
                    scores = saveleaderboard(scores, name, score, last_guessed_pattern)
                    clear_console()
                    return score

            else:
                print("Invalid choice. Please enter a valid option (1-2).")

            return 0
            

        return 0, last_guessed_pattern

def harddifficulty(scores):
    global time_
    global patternlength
    global score
    global name
    global last_guessed_pattern
    

    score = 0
    guesspattern = patternhard(patternlength)

    print("\n" * 2)
    print("PRESS ENTER TO START".center(100))
    input()
    clear_console()

    print("============================================================".center(100))
    print(" ".center(100))
    print("                  REMEMBER THE PATTERN!                   ".center(100))
    print(" ".center(100))
    print(f"{guesspattern}".center(100))
    print(" ".center(100))
    print("============================================================".center(100))
    print(" ".center(100))
    print(" ".center(100))
    countdown(int(time_))
    print(" ".center(100))

    clear_console()

    print(" ".center(100))
    print(" ".center(100))
    print(" ".center(100))
    user_input = input("ENTER THE PATTERN: ".rjust(53))
    print("\n")

    answer = user_input

    if answer == guesspattern:
        score += 50
        patternlength += 1
        last_guessed_pattern = guesspattern

        print("============================================================".center(100))
        print("|                                                          |".center(100))
        print("|                       CORRECT!                           |".center(100))
        print("|                                                          |".center(100))
        print("|           Do you want to continue playing?               |".center(100))
        print("|                                                          |".center(100))
        print("|                       (1) YES                            |".center(100))
        print("|                       (2) NO                             |".center(100))
        print("|                                                          |".center(100))
        print("============================================================".center(100))

        cont = input("Enter your choice (1 or 2): ".rjust(60))

        if cont == '1':
            scores = saveleaderboard(scores, name, score, last_guessed_pattern)
            clear_console()
            last_guessed_pattern = harddifficulty(scores)

        else:
            scores = saveleaderboard(scores, name, score, last_guessed_pattern)
            clear_console()
            viewleaderboard(scores)
            return score

        return score, last_guessed_pattern

    else:
        while True:
            print("============================================================".center(100))
            print("|                                                          |".center(100))
            print("|                                                          |".center(100))
            print("|                      GAME OVER :(                        |".center(100))
            print("|               Do you want to try again?                  |".center(100))
            print("|                        (1) YES                           |".center(100))
            print("|                        (2) NO                            |".center(100))
            print("|                                                          |".center(100))
            print("|                                                          |".center(100))
            print("============================================================".center(100))

            cont_2 = input("Enter your choice (1 or 2): ".rjust(60))

            if cont_2.isdigit() and 1 <= int(cont_2) <= 2:
                cont_2 = int(cont_2)

                if cont_2 == 1:
                    clear_console()
                    scores = saveleaderboard(scores, name, score, last_guessed_pattern)
                    return harddifficulty(scores)

                elif cont_2 == 2:
                    scores = saveleaderboard(scores, name, score, last_guessed_pattern)
                    clear_console()
                    return score

            else:
                print("Invalid choice. Please enter a valid option (1-2).")

            return 0
            

        return 0, last_guessed_pattern

def loadleaderboard():
    scores = []
    try:
        with open('leaderboard.txt', 'r') as file:
            for line in file:
                components = line.strip().split('|')
                name = components[0]
                score = int(components[1])
                last_pattern = components[2] if len(components) > 2 else None
                scores.append({'name': name, 'score': score, 'last_pattern': last_pattern})
    except FileNotFoundError:
        print("Leaderboard file not found. Creating a new one.")
    except Exception as e:
        print(f"Error loading leaderboard: {e}")

    return scores

def viewleaderboard(scores):
    print("============================================================".center(100))
    print("|Rank | Name           | Score | Last Pattern              |".center(100))
    print("============================================================".center(100))

    for i, score in enumerate(scores, start=1):
        if isinstance(score, dict):  # Check if score is a dictionary
            rank = f"| {i:3} "
            name = f"| {score['name'][:15]:<15}"
            score_value = f"| {score['score']:>5} "
            last_pattern = f"| {score['last_pattern'][:25] if score['last_pattern'] is not None else '':<25} |"
            row = rank + name + score_value + last_pattern
            print(row.center(100))

    print("============================================================".center(100))


def saveleaderboard(scores, name, score, last_guessed_pattern):
    last_guessed_pattern = last_guessed_pattern or ""

    player_found = False

    for player in scores:
        if player['name'] == name:
            player['score'] += score
            player['last_pattern'] = last_guessed_pattern
            player_found = True
            break

    if not player_found:
        scores.append({'name': name, 'score': score, 'last_pattern': last_guessed_pattern})

    scores = sorted(scores, key=lambda x: x['score'], reverse=True)

    with open('leaderboard.txt', 'w') as file:
        for player in scores:
            line = f"{player['name']}|{player['score']}|{player['last_pattern']}\n"
            file.write(line)

    return scores

if __name__ == "__main__":
    scores = loadleaderboard()

    name = input("Enter your name: ".rjust(53))

    while True:
        choice = homepage()

        if choice == 1:
            difficultylevel = play(choice)
            clear_console()

            if difficultylevel == 1:
                round_score = easydifficulty(scores)
                if round_score:
                    round_score = int(round_score)
                    saveleaderboard(scores, name, round_score, last_guessed_pattern)
                    clear_console()

            if difficultylevel == 2:
                round_score = mediumdifficulty(scores)
                if round_score:
                    round_score = int(round_score)
                    saveleaderboard(scores, name, round_score, last_guessed_pattern)
                    clear_console()

            if difficultylevel == 3:
                round_score = int(harddifficulty(scores))
                if round_score:
                    round_score = int(round_score)
                    saveleaderboard(scores, name, round_score, last_guessed_pattern)
                    clear_console()

        elif choice == 2:
            viewleaderboard(scores)

        elif choice == 3:
            saveleaderboard(scores, name, score, last_guessed_pattern)
            print("============================================================".center(100))
            print("|                                                          |".center(100))
            print("|                                                          |".center(100))
            print("|                                                          |".center(100))
            print("|                  Thanks for playing!                     |".center(100))
            print("|                                                          |".center(100))
            print("|                                                          |".center(100))
            print("|                                                          |".center(100))
            print("============================================================".center(100))
            sys.exit()
