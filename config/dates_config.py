import datetime
from datetime import timedelta, date

start = 7
end = 1

today = datetime.date.today()

# Période par défaut
end_day = today + timedelta(days=end)
start_day = today - timedelta(days=start)
