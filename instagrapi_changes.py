"""
mixins\private.py ==>line 539

======================================================
elif isinstance(e, ChallengeRequired):
    self.challenge_resolve(self.last_json)
else:
    raise e
======================================================
elif isinstance(e, ChallengeRequired):
    raise e
======================================================
"""

"""
mixins\private.py ==>line 57

======================================================
add : raise ChallengeRequired(f"Enter code (6 digits) for {username} ({choice}): ")
======================================================
"""
