from config.models import MODELS, MODELS_BIAIS
from config.variables import VARIABLES_PLOT
import lecture_mesoNH
import lecture_surfex
from data.selection_data_brut_serieT import selection_data_brut_serieT


class DataLoader:

    def __init__(self):
        self.cache_series = {}
        self.cache_biais = {}

    def load_series(self, start, end):
        key = (start, end)

        if key not in self.cache_series:
            data, chart, graph = selection_data_brut_serieT(start, end)

            self.cache_series[key] = {
                "base": data,
                #"chart": chart,
                #"graph": graph,
                #"meso": lecture_mesoNH.mesoNH(start, end, MODELS, VARIABLES_PLOT),
                #"surfex": lecture_surfex.surfex(start, end, MODELS, VARIABLES_PLOT),
            }

        return self.cache_series[key]

    def load_biais(self, start, end):
        key = (start, end)

        if key not in self.cache_biais:

            self.cache_biais[key] = {
                "meso": lecture_mesoNH.mesoNH(start, end, MODELS_BIAIS, VARIABLES_PLOT),
                #"surfex": lecture_surfex.surfex(start, end, MODELS, VARIABLES_PLOT),
            }

        return self.cache_biais[key]

data_loader = DataLoader()