def _normalize_emotion(self, emotion):
    """
    Normalize emotion labels from models
    Handles CAPITAL emotion labels
    """

    if not emotion:
        return "neutral"

    # Convert emotion to uppercase
    emotion = str(emotion).strip().upper()

    emotion_map = {

        # Stress
        "STRESSED": "stress",
        "STRESS": "stress",

        # Sad
        "SADNESS": "sad",
        "SAD": "sad",

        # Anxiety
        "FEAR": "anxiety",
        "ANXIOUS": "anxiety",
        "ANXIETY": "anxiety",

        # Angry
        "ANGER": "angry",
        "ANGRY": "angry",

        # Happy
        "JOY": "happy",
        "HAPPY": "happy",

        # Excited
        "SURPRISE": "excited",
        "SURPRISED": "excited",
        "EXCITED": "excited",

        # Relaxed
        "CALM": "relaxed",
        "RELAXED": "relaxed",

        # Neutral
        "NEUTRAL": "neutral"
    }

    return emotion_map.get(emotion, "neutral")