import json
import os

def ensure_data_directory():
    """Ensure the data directory exists."""
    if not os.path.exists('./data'):
        os.makedirs('./data')

def save_backup(pp_scores, profiles):
    """Save a backup of pp_scores and profiles to a JSON file."""
    ensure_data_directory()
    backup_data = {
        'pp_scores': pp_scores,
        'profiles': profiles
    }
    try:
        with open('./data/backup.json', 'w') as f:
            json.dump(backup_data, f, indent=4)
    except IOError as e:
        print(f"Error saving backup: {e}")

def update_passes_log(pp_scores):
    """Update the passes log to a text file."""
    ensure_data_directory()
    try:
        with open('./data/passes_info.txt', 'w') as f:
            for pass_id, score in pp_scores.items():
                f.write(f"Pass ID: {pass_id}\n")
                f.write(f"User ID: {score.get('user_id', 'N/A')}\n")
                f.write(f"Score: {score.get('score', 'N/A')}\n")
                f.write(f"Verified: {score.get('verified', 'N/A')}\n\n")
    except IOError as e:
        print(f"Error updating passes log: {e}")

def calculate_pp(song_speed, accuracy, song_difficulty):
    """Calculate and return the PP value based on song speed, accuracy, and song difficulty."""
    try:
        song_speed = float(song_speed)
        accuracy = float(accuracy) / 100.0
        song_difficulty = float(song_difficulty)
        
        if not (70 <= song_speed <= 200):
            return "**Song speed must be between 70% and 200%**"
        
        if not (1 <= song_difficulty <= 50):
            return "**Song difficulty must be between 1 and 50**"
        
        if not (0.01 <= accuracy <= 100):
            return "**Song accuracy must be between 0.01 and 100**"
        
        base_pp = 300
        if song_speed < 100:
            if song_difficulty > 35:
                base_pp *= (1 - (100 - song_speed) / 200)
            else:
                base_pp *= (1 - (100 - song_speed) / 50)
        else:
            base_pp *= (1 + (song_speed - 100) / 100)
        
        base_pp *= accuracy
        
        if song_difficulty < 25:
            final_pp = base_pp * (song_difficulty / 30)
        else:
            final_pp = base_pp * (song_difficulty / 25)
        
        final_pp = min(final_pp, 1000)
        
        return final_pp
    except ValueError:
        return "**Please enter valid numbers.**"

def load_backup():
    """Load the backup data from a JSON file."""
    ensure_data_directory()
    try:
        with open('./data/backup.json', 'r') as f:
            data = json.load(f)
            return data.get('pp_scores', {}), data.get('profiles', {})
    except IOError as e:
        print(f"Error loading backup: {e}")
        return {}, {}
