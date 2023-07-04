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

# def catch_scheduled_job_exceptions(job_func):
#     @functools.wraps(job_func)
#     def wrapper(*args, **kwargs):
#         with open("file_report", "w") as f:
#             try:
#                 f.write("job_func")
#                 return job_func(*args, **kwargs)
#             except Exception as e:
#                 f.write(str(e))
#             # import traceback
#             # print(traceback.format_exc())
#             # if cancel_on_failure:
#             #     return schedule.CancelJob
#     return wrapper