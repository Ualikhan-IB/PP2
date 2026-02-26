from datetime import datetime

date1 = datetime(2024, 1, 1, 0, 0, 0)
date2 = datetime(2024, 3, 15, 12, 30, 0)

difference = date2 - date1
seconds = difference.total_seconds()

print("Date 1:", date1)
print("Date 2:", date2)
print("Difference in seconds:", seconds)
