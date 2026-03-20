from config.models import MODELS
from config.variables import VARIABLES_PLOT
from data.selection_data import selection_data
from data.selection_data_pv import selection_donnees_PV


class DataLoader:

    def __init__(self):
        self.cache_series = {}

    def load_series(self, start, end):
        key = (start, end)

        if key not in self.cache_series:
            data = selection_data(start, end)

            self.cache_series[key] = {
                "base": data,
                #"meso": lecture_mesoNH.mesoNH(start, end, MODELS, VARIABLES_PLOT),
                #"surfex": lecture_surfex.surfex(start, end, MODELS, VARIABLES_PLOT),
            }

        return self.cache_series[key]


class DataLoaderPV:

    def __init__(self):
        self._cache = {}

    def load(self, start_day, end_day):
        key = (start_day, end_day)

        if key not in self._cache:
            self._cache[key] = selection_donnees_PV(start_day, end_day)

        return self._cache[key]



data_loader = DataLoader()
data_loader_pv = DataLoaderPV()