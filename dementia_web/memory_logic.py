import random
import time

WORD_BANK = [
    "apple", "river", "chair", "music", "clock",
    "doctor", "yellow", "garden", "phone", "mirror",
    "train", "bread", "cloud", "pencil", "window",
    "carpet", "forest", "bottle", "flower", "camera",
    "school", "beach", "coffee", "mountain", "shirt",
    "paper", "laptop", "rain", "book", "shoe"
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
