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
#random.seed(0xdeadbeef)

from heppy.configuration import Collider
Collider.BEAMS = 'ee'
Collider.SQRTS = 350.
Collider.DETECTOR = 'ILD'

# Transfering this section to the python samplers inside the PYTHIA folder
# The next variable can be used when creating the heppy sampler
#name_outdir = 'tt_semilepton_ILD'


import heppy.ttbar_analysis.ANALYSIS.PYTHIA.python_samplers.splitmtop.ee_ttbar_splitmtop_1730_0_sampler as samples


n_cores = 4
number_jets = 4
for comp in selectedComponents:
    comp.splitFactor = n_cores



from heppy.analyzers.fcc.Reader import Reader
source = cfg.Analyzer(
    Reader,
    gen_particles = 'GenParticle',
    gen_vertices = 'GenVertex'
)

from heppy.sequences.GenParticlesSequence import gen_particles_sequence

from heppy.sequences.PapasSequence import papas_sequence

from heppy.sequences.MatchingMCSequence import matching_mc_sequence

from heppy.sequences.LeptonsSequence import leptons_sequence

from heppy.sequences.JetsSequence import jets_sequence

from heppy.sequences.MissingEnergySequence import missing_energy_sequence

from heppy.sequences.TopConstrainerSequence import top_constrainer_sequence

from heppy.sequences.MatchingTTbarSequence import matching_ttbar_sequence

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
