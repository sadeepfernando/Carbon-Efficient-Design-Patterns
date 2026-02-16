import json
import random
import os

def generate_messages(count):
    """
    Generate synthetic messages for testing all design patterns.
    Matches the Java implementation structure.
    """
    messages = []
    for _ in range(count):
        messages.append({
            "id": random.randint(1, 1_000_000),
            "value": random.random(),
            "status": "OK"
        })
    return messages


def write_json(data, path):
    """
    Write data to a JSON file. 
    Optional, not required for your energy measurements.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)
