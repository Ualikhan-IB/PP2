from datetime import date, timedelta

current = date.today()
five_days_ago = current - timedelta(days=5)
print("Current date:", current)
print("5 days ago:", five_days_ago)
