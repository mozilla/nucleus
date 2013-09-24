from .base import *
try:
    from .local import *
except ImportError:
    pass  # settings.local not needed for stackato deploy
