import os
import copy
import heppy.framework.config as cfg

from heppy.framework.event import Event
Event.print_patterns=['sum*']

import logging
logging.shutdown()
reload(logging)
logging.basicConfig(level=logging.WARNING)

import random
random.seed(0xdeadbeef)

from heppy.configuration import Collider
Collider.BEAMS = 'ee'
Collider.SQRTS = 350.
Collider.DETECTOR = 'ILD'

#comp_zz = cfg.Component(
#    'zz',
#    files = [
#        os.path.abspath('./raw_ntuple/pythia/ee_ZZ_350GeV.root')
#    ]
#)
#
#comp_ww = cfg.Component(
#    'ww',
#    files = [
#        os.path.abspath('./raw_ntuple/pythia/ee_WW_350GeV.root')
#    ]
#)
#
#comp_hz = cfg.Component(
#    'hz',
#    files = [
#        os.path.abspath('./raw_ntuple/pythia/ee_HZ_350GeV.root')
#    ]
#)
#
#comp_tt_allhad = cfg.Component(
#    'tt_allhad',
#    files = [
#        os.path.abspath('./raw_ntuple/pythia/ee_tthad_350GeV.root')
#    ]
#)
#
#comp_tt_dilep = cfg.Component(
#    'tt_dilep',
#    files = [
#        os.path.abspath('./raw_ntuple/pythia/ee_ttlep_350GeV.root')
#    ]
#)
#
#selectedComponents = [
#                        comp_zz,
#                        comp_ww,
#                        comp_hz,
#                        comp_tt_allhad,
#                        comp_tt_dilep,
#                     ]

#for component in selectedComponents:
#    component.splitFactor = len(component.files)

#import heppy.ttbar_analysis.ANALYSIS.PYTHIA.python_samplers.splitmtop.ee_ttbar_splitmtop_1718_0_sampler as samples
from heppy.ttbar_analysis.ANALYSIS.PYTHIA.python_samplers.tthad_lep_sampler import selectedComponents

n_cores = 4
number_jets = 4
for comp in selectedComponents:
    comp.splitFactor = n_cores
#selectedComponents = [samples.ttbar]


from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader,
    gen_particles = 'GenParticle',
    gen_vertices = 'GenVertex'
)

from heppy.sequences.GenParticlesSequence import gen_particles_sequence
#from heppy.sequences.GenParticlesSequence import gen_leptons,gen_particles_stable

from heppy.sequences.PapasSequence import papas_sequence

from heppy.sequences.MatchingMCSequence import matching_mc_sequence

from heppy.sequences.LeptonsSequence import leptons_sequence

from heppy.sequences.JetsSequence import jets_sequence

from heppy.sequences.MissingEnergySequence import missing_energy_sequence

from heppy.sequences.TopConstrainerSequence import top_constrainer_sequence

# Test if this solves the problems
from heppy.sequences.MatchingTTbarSequence import matching_ttbar_sequence

#from heppy.analyzers.tree.TreeTTSemilep import TreeTTSemilep
#tree = cfg.Analyzer(
#    TreeTTSemilep,
#    mc_lepton = 'mc_lepton',
#    mc_neutrino = 'mc_neutrino',
#    leptons = 'sel_iso_leptons',
#    jets = 'jets',
#    mc_b_quarks = 'mc_b_quarks',
#)

from heppy.analyzers.tree.TreeTTSemilep import TreeTTSemilep
tree = cfg.Analyzer(
    TreeTTSemilep,
    mc_lepton = 'mc_lepton',
    mc_neutrino = 'mc_neutrino',
    leptons = 'sel_iso_leptons',
    jets = 'jets',
    mc_b_quarks = 'mc_b_quarks',
    mc_quark_jets = 'mc_quark_jets',
    mc_t_quarks = 'mc_t_quarks',
    mc_w_bosons = 'mc_w_bosons'
)


sequence = cfg.Sequence(
                        source,
                        gen_particles_sequence,
                        #gen_leptons,
                        #check_gen_leptons,
                        #gen_particles_stable,
                        # gen_particles_stable_and_neutrinos,
                        papas_sequence(Collider.DETECTOR),
                        matching_mc_sequence,
                        leptons_sequence,
                        jets_sequence(number_jets, Collider.DETECTOR),
                        missing_energy_sequence(Collider.SQRTS),
                        top_constrainer_sequence(Collider.SQRTS),
                        matching_ttbar_sequence,
                        tree
                        )


from ROOT import gSystem
gSystem.Load("libdatamodelDict")
from EventStore import EventStore as Events

config = cfg.Config(
    components = selectedComponents,
    sequence = sequence,
    services = [],
    events_class = Events
)
