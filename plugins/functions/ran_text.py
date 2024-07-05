# ᴛʜᴀɴᴋs
import random
import string

def random_char(length: int = 5) -> str:
    """Generates a random string of the specified length."""
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

# ... (You can keep your `ran` variable if you are using it) 

ran = (random_char(5)) 

