def calculate_questionnaire_score(answers):
    """
    Calculate questionnaire score from user answers
    
    Answers are on a scale of 1-4:
    1 = Never (GOOD - no symptoms)
    2 = Rarely (OK)
    3 = Sometimes (CONCERNING)
    4 = Often (BAD - frequent symptoms)
    
    We need to convert to 0-1 scale where:
    - 1.0 = healthy (all answers are 1 - never have symptoms)
    - 0.0 = high risk (all answers are 4 - often have symptoms)
    """
    
    # Convert dict values to list of integers
    if isinstance(answers, dict):
        numeric_values = [int(v) for k, v in answers.items()]
    else:
        # If it's already a list
        numeric_values = [int(v) for v in answers]
    
    if len(numeric_values) == 0:
        return 0.0
    
    print(f"Questionnaire answers: {numeric_values}")
    
    # Calculate average (1-4 scale)
    avg_answer = sum(numeric_values) / len(numeric_values)
    
    # INVERT the score!
    # Higher symptoms (4) should give LOWER score (0)
    # Lower symptoms (1) should give HIGHER score (1)
    # Formula: (max - avg) / (max - min) = (4 - avg) / 3
    score = (4.0 - avg_answer) / 3.0
    
    # Ensure between 0 and 1
    score = max(0.0, min(1.0, score))
    
    print(f"Average answer: {avg_answer:.2f}, Calculated score: {score:.2f}")
    
    return score