from hashlib import blake2b

# Unique key generator using Blake Algorithm 

def gen_ukey(*args: str) -> int:
    """Generate a unique key for the given arguments."""
    hash_obj = blake2b(digest_size=15)  # 15 bytes ensures the result fits within 38 digits
    
    for arg in args:
        hash_obj.update(str(arg).encode("utf-8"))  

    return int(hash_obj.hexdigest(), 16)  # Convert hex digest to an integer