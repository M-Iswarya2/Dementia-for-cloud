import random
import time

WORD_BANK = [
    # Nature
    "river", "cloud", "forest", "mountain", "ocean",
    "desert", "volcano", "glacier", "canyon", "jungle",
    "island", "meadow", "waterfall", "cave", "storm",

    # Animals
    "dolphin", "eagle", "tiger", "penguin", "giraffe",
    "elephant", "wolf", "parrot", "shark", "rabbit",
    "panther", "falcon", "tortoise", "buffalo", "cobra",

    # Objects / Household
    "mirror", "carpet", "ladder", "lantern", "compass",
    "candle", "kettle", "blanket", "pillow", "hammer",
    "anchor", "barrel", "helmet", "ribbon", "trophy",

    # Food & Drink
    "mango", "pepper", "lemon", "walnut", "mushroom",
    "ginger", "honey", "salmon", "pretzel", "avocado",

    # Places
    "castle", "harbour", "temple", "stadium", "lighthouse",
    "tunnel", "balcony", "rooftop", "library", "factory",

    # Abstract / Misc
    "shadow", "silence", "mystery", "memory", "balance",
    "courage", "fortune", "wisdom", "danger", "freedom",

    # Science & Tech
    "rocket", "magnet", "circuit", "laser", "prism",
    "oxygen", "atom", "radar", "fossil", "crystal",

    # Actions (noun form)
    "journey", "signal", "pattern", "mission", "puzzle",
    "legend", "chapter", "riddle", "summit", "echo",
]

WORDS_TO_MEMORIZE = 10
CORRECT_OPTIONS = 5
DISTRACTORS = 5


def generate_round(used_words):
    available_words = list(set(WORD_BANK) - set(used_words))

    memorized_words = random.sample(available_words, WORDS_TO_MEMORIZE)
    correct_choices = random.sample(memorized_words, CORRECT_OPTIONS)

    distractor_pool = list(set(available_words) - set(memorized_words))
    distractors = random.sample(distractor_pool, DISTRACTORS)

    options = correct_choices + distractors
    random.shuffle(options)

    return {
        "memorized_words": memorized_words,
        "correct_choices": correct_choices,
        "options": options,
        "start_time": time.time()
    }


def evaluate_round(selected_words, correct_choices, start_time):
    end_time = time.time()

    correct = len(set(selected_words) & set(correct_choices))
    wrong = len(set(selected_words) - set(correct_choices))
    missed = len(set(correct_choices) - set(selected_words))

    score = max(0, correct * 2 - wrong)/10  

    return {
        "correct": correct,
        "wrong": wrong,
        "missed": missed,
        "score": score,
        "response_time": round(end_time - start_time, 2)
    }
