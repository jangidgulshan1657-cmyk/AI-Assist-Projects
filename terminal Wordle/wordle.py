"""Terminal Wordle."""

import random
from pathlib import Path
import json

Words_Path = Path(__file__).parent/("words.json")


def load(path:Path)-> list|None:
    if path.exists():
        try:
            with open(path,'r') as f:
                words = json.load(f)
                if not isinstance(words,list) or not all(isinstance(k,str) and len(k) == 5 and k.isalpha() for k in words):
                    return None
                return words
        except json.JSONDecodeError:
            return None
    else:
        return None


WORDS = load(Words_Path)


GREEN = "\033[42m\033[30m"
YELLOW = "\033[43m\033[30m"
GREY = "\033[100m\033[97m"
RESET = "\033[0m"
COLORS = {"green": GREEN, "yellow": YELLOW, "grey": GREY}
MAX_GUESSES = 6


def score(guess: str, answer: str) -> list[str]:
    result = ["grey"] * 5
    remaining = list(answer)

    for i in range(5):                      # pass 1: exact matches
        if guess[i] == answer[i]:
            result[i] = "green"
            remaining[i] = None

    for i in range(5):                      # pass 2: right letter, wrong place
        if result[i] == "grey" and guess[i] in remaining:
            result[i] = "yellow"
            remaining[remaining.index(guess[i])] = None

    return result


def render(guess: str, result: list[str]) -> str:
    return "".join(f"{COLORS[r]} {ch.upper()} {RESET}" for ch, r in zip(guess, result))


def play() -> None:
    if not WORDS:
        print("ERROR In Loading FIle!!")
        return
    answer = random.choice(WORDS)
    for attempt in range(1, MAX_GUESSES + 1):
        while True:
            guess = input(f"Guess {attempt}/{MAX_GUESSES}: ").strip().lower()
            if len(guess) == 5 and guess.isalpha():
                break
            print("Five letters, a-z only.")
        print(render(guess, score(guess, answer)))
        if guess == answer:
            print(f"Got it in {attempt}.")
            return
    print(f"Out of guesses. The word was {answer.upper()}.")


if __name__ == "__main__":
    play()