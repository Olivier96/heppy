import heppy.framework.config as cfg

def top_constrainer_sequence(cdm_energy):
    from heppy.analyzers.TopConstrainerAnalyzer import TopConstrainerAnalyzer
    top_constrainer = cfg.Analyzer(
        TopConstrainerAnalyzer,
        jets = 'jets',
        leptons = 'leptons',
        sqrts = 350.,
        top_mass = 173.,
        w_mass = 80.4,
        tophadRec_m = 167.99,
        tophadRec_w = 17.94,
        whadRec_m = 83.19,
        whadRec_w = 16.50,
        toplepRec_m = 173.81,
        toplepRec_w = 21.06,
        wlepRec_m = 98.20,
        wlepRec_w = 18.84,
    )


    return [
        top_constrainer
    ]
