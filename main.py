from collections import defaultdict

import argparse


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
    parser = argparse.ArgumentParser(description='Helper tool for solving Wordle puzzles')
    parser.add_argument('correct_positions', default='')  # TODO HELP
    parser.add_argument('-k', '--known_letters', type=set, default=set(),
                        help='Letters which are known to be contained in the word but their possition is unknown')
    parser.add_argument('-i', '--invalid_letters', type=set, default=set())  # TODO HELP
    parser.add_argument('-x', '--invalid_positions', nargs='*', default=[])  # TODO HELP
                        
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

    # Remove all words which contain invalid letters
    if args.invalid_letters:
        filtered_words = [w for w in filtered_words if not args.invalid_letters.intersection(w)]

    # Count all the letters in the remaining words (per position)
    # TODO LOL HORRIBLE
    letter_count = [
        defaultdict(int),
        defaultdict(int),
        defaultdict(int),
        defaultdict(int),
        defaultdict(int),
    ]
    for word in filtered_words:
        for pos, c in enumerate(word):
            letter_count[pos][c] += 1

    # Find highest scoring word
    # TODO TESTING prioritise unique letters
    max_score = 0
    best_word = None
    for word in filtered_words:
        score = sum(letter_count[pos][c] for pos, c in enumerate(word))
        # Weight used for prioritising words with entirely unique letters
        weight = 1
        if len(set(word)) == 5:
            weight += 1 / (len(correct_positions) + 1)
        score *= weight
        if score > max_score:
            max_score = score
            best_word = word

    print(best_word)


if __name__ == '__main__':
    main()
