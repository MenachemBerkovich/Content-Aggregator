"""General operations needed by non-specific modules or classes.
"""
import functools
from enum import Enum

class ObjectResetOperationClassifier(Enum):
    """Enum class contains possible setter's object operations, like:
    +=, -=, etc.
    """
    ADDITION = 1
    SUBTRACTION = 2
