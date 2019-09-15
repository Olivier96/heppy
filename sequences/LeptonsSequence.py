import heppy.framework.config as cfg

from heppy.analyzers.Selector import Selector
leptons = cfg.Analyzer(
    Selector,
    'sel_leptons',
    output = 'leptons',
    input_objects = 'rec_particles',
    filter_func = lambda ptc: ptc.e()>10. and abs(ptc.pdgid()) in [11, 13]
)


from heppy.analyzers.IsolationAnalyzer_mod import IsolationAnalyzer
from heppy.particles.isolation_mod import Cone
iso_leptons = cfg.Analyzer(
    IsolationAnalyzer,
    candidates = 'leptons',
    particles = 'rec_particles',
    iso_area = Cone(0.3)
)


sel_iso_leptons = cfg.Analyzer(
    Selector,
    'sel_iso_leptons',
    output = 'sel_iso_leptons',
    input_objects = 'leptons',
    filter_func = lambda lep: lep.iso.sume < 15.
)


# from heppy.analyzers.CheckLeptons import CheckLeptons
# check_leptons = cfg.Analyzer(
#   CheckLeptons,
#   objects = 'sel_iso_leptons',
# )


leptons_sequence = [
    leptons,
    iso_leptons,
    sel_iso_leptons,
    # check_leptons
    ]
