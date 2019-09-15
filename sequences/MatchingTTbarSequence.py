import heppy.framework.config as cfg


# Obsolete, this job is included into MCQuarkJetFinder
from heppy.analyzers.MCbQuarks import MCbQuarks
mc_b_quarks = cfg.Analyzer(
    MCbQuarks,
    output = 'mc_b_quarks',
    jets = 'jets',
)

from heppy.analyzers.MCtQuarks import MCtQuarks
mc_t_quarks = cfg.Analyzer(
    MCtQuarks,
    output = 'mc_t_quarks',
)

from heppy.analyzers.MCwBosons import MCwBosons
mc_w_bosons = cfg.Analyzer(
    MCwBosons,
    output = 'mc_w_bosons',
)

from heppy.analyzers.MCQuarkJetFinder import MCQuarkJetFinder
mc_quarkjets = cfg.Analyzer(
    MCQuarkJetFinder,
    output1 = 'mc_b_quarks',
    output2 = 'mc_quark_jets',
    jets = 'jets',
)

from heppy.analyzers.MCLeptonFinder import MCLeptonFinder
mc_lepton_and_neutrino = cfg.Analyzer(
    MCLeptonFinder,
    sel_leptons = 'sel_iso_leptons',
    output1 = 'mc_lepton',
    output2 = 'mc_neutrino',
)

matching_ttbar_sequence = [
    mc_lepton_and_neutrino,
    #mc_b_quarks,
    mc_t_quarks,
    mc_w_bosons,
    mc_quarkjets
]
