# app/auth/token_blacklist.py

# In-memory blacklist (works for single instance / testing)
blacklist = set()

def blacklist_token(token: str):
    """Add a token to the blacklist"""
    blacklist.add(token)

def is_blacklisted(token: str) -> bool:
    """Check if a token is blacklisted"""
    return token in blacklist
