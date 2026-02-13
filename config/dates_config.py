import datetime
from datetime import timedelta, date

start = 2
end = 2

today = datetime.date.today()

# Période par défaut
end_day = today + timedelta(days=end)
start_day = today - timedelta(days=start)
