from collections import defaultdict
from itertools import chain

import argparse
import random


def correct_positions_dict(correct_positions_str):
    """
    Converts correct positions string of format h_ll_ to dict of positions like
    {0: 'h', 2: 'l', 3: 'l'}.
    """
    return {pos: c
            for pos, c
            in enumerate(correct_positions_str)
            if c != '_'}


def invalid_positions_dict(incorrect_positions_list):
    """
    Convert a list of invalid position strings of the format ['_e__o', '_a__y']  into a dict of
    invalid positions like {1: {'e', 'a'}, 2: {'o', 'y'}}.
    """
    incorrect_positions = defaultdict(set)
    for incorrect_positions_str in incorrect_positions_list:
        for pos, c in enumerate(incorrect_positions_str):
            if c == '_': continue
            incorrect_positions[pos].add(c)
    return incorrect_positions


def main():
    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Helper tool for solving Wordle puzzles',
                                     epilog='E.g. python wordle_solver.py h_l__ -k hle -x _appy _o_es')
    parser.add_argument('correct_positions', default='',
                        help='Known letters in their correct positions. E.g. h_l__')
    parser.add_argument('-k', '--known_letters', type=set, default=set(),
                        help='Letters which are known to be contained in the word but their possition is unknown. E.g. hle')
    parser.add_argument('-i', '--invalid_positions', nargs='*', default=[],
                        help='Known incorrect letter positions. E.g. _appy _o_es')
                        
    args = parser.parse_args()

    # Load all possible words.
    with open('five_words.txt', 'r') as f:
        words = [w.strip() for w in f]

    # Remove all words which don't match the correct positions.
    correct_positions = correct_positions_dict(args.correct_positions)
    filtered_words = []
    if not correct_positions:  # Don't do this step if no positions are known
        filtered_words = words
    else:
        for word in words:
            if all(word[pos] == c for pos, c in correct_positions.items()):
                filtered_words.append(word)

    # Remove all words matching invalid positions
    invalid_positions = invalid_positions_dict(args.invalid_positions)
    if invalid_positions:
        new_filtered_words = []
        for word in filtered_words:
            if not any(word[pos] in c for pos, c in invalid_positions.items()):
                new_filtered_words.append(word)
        filtered_words = new_filtered_words

    # Remove all words which don't contain known letters
    if args.known_letters:
        filtered_words = [w for w in filtered_words if all(c in w for c in args.known_letters)]

    # Create a set of invalid letters based on all the letters in the invalid positions minus known letters
    invalid_letters = set(c for c in chain(*args.invalid_positions) if c != '_') - set(args.known_letters)

    # Remove all words which contain invalid letters
    if invalid_letters:
        filtered_words = [w for w in filtered_words if not invalid_letters.intersection(w)]

    # Count all the letters in the remaining words (per position) using a defaultdict
    # for each position
    letter_count = [defaultdict(int) for __ in range(5)]
    for word in filtered_words:
        for pos, c in enumerate(word):
            letter_count[pos][c] += 1

    # Find highest scoring word(s)
    # It is possible that multiple words could have the same score. This is
    # accounted for by keeping a list of all these words and selecting one
    # at random.
    max_score = 0
    best_words = []
    for word in filtered_words:
        # The score of a word is the sum of the character counts for each
        # position in the word
        score = sum(letter_count[pos][c] for pos, c in enumerate(word))
        # Weight used for prioritising words with entirely unique letters
        weight = 1
        if len(set(word)) == 5:
            # The weighting is stronger the less correct positions which are
            # currently known.
            weight += 1 / (len(correct_positions) + 1)
        score *= weight
        if score > max_score:
            max_score = score
            best_words = [word]
        elif score == max_score:
            best_words.append(word)

    # Print out the recommended word
    print(random.choice(best_words))


if __name__ == '__main__':
    main()
