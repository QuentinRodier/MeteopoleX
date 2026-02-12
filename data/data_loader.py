from config.models import MODELS
from config.variables import VARIABLES_PLOT
import lecture_mesoNH
import lecture_surfex
from data.selection_data_brut_serieT import selection_data_brut_serieT


class DataLoader:

    def __init__(self):
        self.cache = {}

    def load_base(self, start, end):
        key = (start, end)

        if key not in self.cache:
            data, chart, graph = selection_data_brut_serieT(start, end)

            self.cache[key] = {
                "base": data,
                "meso": lecture_mesoNH.mesoNH(start, end, MODELS, VARIABLES_PLOT),
                "surfex": lecture_surfex.surfex(start, end, MODELS, VARIABLES_PLOT),
            }

        return self.cache[key]


data_loader = DataLoader()

