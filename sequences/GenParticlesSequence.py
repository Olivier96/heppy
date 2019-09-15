import heppy.framework.config as cfg


from heppy.analyzers.Selector import Selector
gen_leptons = cfg.Analyzer(
  Selector,
  output = 'gen_leptons',
  input_objects = 'gen_particles',
  filter_func = lambda x : x.status()==1 and abs(x.pdgid()) in [11, 13] and x.pt() > 1e-5
)

from heppy.analyzers.CheckGenLeptons import CheckGenLeptons
check_gen_leptons = cfg.Analyzer(
  CheckGenLeptons,
  objects = 'gen_leptons',
    n_lep = 1,
    energy_cut = 8,
)

gen_particles_stable = cfg.Analyzer(
  Selector,
  output = 'gen_particles_stable',
  input_objects = 'gen_particles',
  filter_func = lambda x : x.status()==1 and abs(x.pdgid()) not in [12, 14, 16] and x.pt() > 1e-5
)

def is_stable_also_neutrino(x):
  return x.status()==1
gen_particles_stable_and_neutrinos = cfg.Analyzer(
  Selector,
  output = 'gen_particles_stable_and_neutrinos',
  input_objects = 'gen_particles',
  filter_func = is_stable_also_neutrino
)

gen_particles_sequence = [
    gen_leptons,
    check_gen_leptons,
    gen_particles_stable,
    # gen_particles_stable_and_neutrinos,
]
