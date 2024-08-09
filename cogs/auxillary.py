# auxillary.py

""" Auxillary functions for cogs to use """

# Decorator for the [OK]'s when loading cogs
def try_wrap (func):
    async def wrapper(*args, **kwargs):
        try:
            await func(*args, **kwargs)
            print ("[OK]")
        except Exception as e:
            print ("[ERROR]", e)
    return wrapper

