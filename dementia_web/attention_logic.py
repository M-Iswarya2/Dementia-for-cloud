import random

STIMULI = ["🔵", "🔴", "🟡", "🟢"]
TOTAL_TRIALS = 30
TARGET_RATIO = 0.3  # probability that stimulus matches target

def generate_attention_sequence():
    sequence = []
    targets = []

    for _ in range(TOTAL_TRIALS):
        # Pick a random target for this trial
        trial_target = random.choice(STIMULI)
        targets.append(trial_target)

        # Decide stimulus: match target with probability TARGET_RATIO
        if random.random() < TARGET_RATIO:
            sequence.append(trial_target)
        else:
            sequence.append(random.choice([s for s in STIMULI if s != trial_target]))

    return {
        "sequence": sequence,
        "targets": targets,  # list of target for each trial
        "total_trials": TOTAL_TRIALS
    }


def evaluate_attention(responses, sequence, targets):
    hits = 0
    misses = 0
    false_alarms = 0
    reaction_times = []

    response_map = {r["index"]: r["reaction_time"] for r in responses}

    for i, stim in enumerate(sequence):
        target = targets[i]
        if stim == target:
            if i in response_map:
                hits += 1
                reaction_times.append(response_map[i])
            else:
                misses += 1
        else:
            if i in response_map:
                false_alarms += 1

    avg_rt = round(sum(reaction_times) / len(reaction_times), 3) if reaction_times else 0
    raw_score = (hits * 2) - false_alarms - misses

    return {
        "hits": hits,
        "misses": misses,
        "false_alarms": false_alarms,
        "avg_reaction_time": avg_rt,
        "raw_score": raw_score
    }