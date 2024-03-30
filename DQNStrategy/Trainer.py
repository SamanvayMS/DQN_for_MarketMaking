import sqlite3
import numpy as np

def deserialize_state(state_str):
    """Converts the serialized state string back into a numpy array."""
    return np.array([float(x) for x in state_str.split(',') if x])

def fetch_random_experiences(db_path, num_samples=32):
    """Fetches a random sample of experiences from the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = "SELECT * FROM experience ORDER BY RANDOM() LIMIT ?;"
    cursor.execute(query, (num_samples,))
    
    experiences = []
    for row in cursor.fetchall():
        state = deserialize_state(row[1])
        action = row[2]
        reward = row[3]
        next_state = deserialize_state(row[4])
        done = bool(row[5])
        experiences.append((state, action, reward, next_state, done))
    
    conn.close()
    return experiences

# Example usage
db_path = 'dqn_experience.db'
experiences = fetch_random_experiences(db_path)
for experience in experiences:
    print(experience)