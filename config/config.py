import datetime
from datetime import timedelta, date

from config.models import RESEAUX

start = 7
end = 1

today = datetime.date.today()

# Période par défaut
end_day = today + timedelta(days=end)
start_day = today - timedelta(days=start)

# Mapping

arome_mapping = {
        "Arome_J-1_00h": (RESEAUX[0], dict(color="#33a02c")),
        "Arome_J-1_12h": (RESEAUX[1], dict(color="#33a02c", dash="dot")),
        "Arome_J0_00h":  (RESEAUX[2], dict(color="#1f78b4")),
        "Arome_J0_12h":  (RESEAUX[3], dict(color="#1f78b4", dash="dot")),
    }
