import datetime
from datetime import timedelta, date

from config.models import RESEAUX

start = 7
end = 5

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

# Période par défaut
#end_day = today + timedelta(days=end)
#start_day = today - timedelta(days=start)

start_day = datetime.date(2025, 12, 31)
end_day = datetime.date(2026, 1, 3)


# Mapping

arome_mapping = {
        "Arome_J0_00h":  (RESEAUX[0], dict(color="#1f78b4")),
        "Arome_J0_12h":  (RESEAUX[1], dict(color="#1f78b4", dash="dot")),
        "Arome_J-1_00h": (RESEAUX[2], dict(color="#a6cee3")),
        "Arome_J-1_12h": (RESEAUX[3], dict(color="#a6cee3", dash="dot")),
    }

arpege_mapping = {
        "Arpège_J0_00h": (RESEAUX[0], dict(color="#33a02c")),
        "Arpège_J0_12h": (RESEAUX[1], dict(color="#33a02c", dash="dot")),
        "Arpège_J-1_00h": (RESEAUX[2], dict(color="#b2df8a")),
        "Arpège_J-1_12h": (RESEAUX[3], dict(color="#b2df8a", dash="dot")),
    }

surfex_arp_mapping = dict(color="darkorange")