from datetime import datetime

now = datetime.now()
print("With microseconds:   ", now)
print("Without microseconds:", now.replace(microsecond=0))
