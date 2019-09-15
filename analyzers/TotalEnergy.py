from heppy.framework.analyzer import Analyzer
from heppy.particles.tlv.resonance import Resonance

class TotalEnergy(Analyzer):
    '''
    from analyzers.TotalEnergy import TotalEnergy
    total_energy = cfg.Analyzer(
      TotalEnergy,
      gen_particles_stable_and_neutrinos = 'gen_particles_stable_and_neutrinos',
      gen_particles_stable = 'gen_particles_stable',
      rec_particles = 'rec_particles',
    )
    '''

    def process(self, event):
        gen_particles_stable_and_neutrinos = getattr(event, self.cfg_ana.gen_particles_stable_and_neutrinos)
        gen_particles_stable = getattr(event, self.cfg_ana.gen_particles_stable)
        rec_particles = getattr(event, self.cfg_ana.rec_particles)


        event.total_gen = Resonance(gen_particles_stable_and_neutrinos, 0)
        event.total_gen_visible = Resonance(gen_particles_stable, 0)
        event.total_rec = Resonance(rec_particles, 0)
