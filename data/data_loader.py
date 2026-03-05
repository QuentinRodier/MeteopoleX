from config.models import MODELS
from config.variables import VARIABLES_PLOT
from data.selection_data_brut_serieT import selection_data_brut_serieT


class DataLoader:

    def __init__(self):
        self.cache_series = {}

    def load_series(self, start, end):
        key = (start, end)

        if key not in self.cache_series:
            data = selection_data_brut_serieT(start, end)

            self.cache_series[key] = {
                "base": data,
                #"meso": lecture_mesoNH.mesoNH(start, end, MODELS, VARIABLES_PLOT),
                #"surfex": lecture_surfex.surfex(start, end, MODELS, VARIABLES_PLOT),
            }

        return self.cache_series[key]

data_loader = DataLoader()