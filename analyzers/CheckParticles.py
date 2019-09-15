from heppy.framework.analyzer import Analyzer
from heppy.statistics.counter import Counter, Counters

class CheckParticles(Analyzer):
    '''
    Example:
    from analyzers.CheckParticles import CheckParticles
    check_particles = cfg.Analyzer(
      CheckParticles,
      leptons = 'sel_iso_leptons',
      other_particles = 'particles_not_iso_lep',
      n_lep = 1,
      n_min = 4
    )
    '''

    def beginLoop(self, setup):
        super(CheckParticles, self).beginLoop(setup)

        self.counters.addCounter('events')
        self.counters.counter('events').register('All events')
        self.counters.counter('events').register('1 lepton')
        self.counters.counter('events').register('4 particles')
        self.counters.counter('events').register('1 lepton && 4 particles')

    def process(self, event):

        leptons = getattr(event, self.cfg_ana.leptons)
        other_particles = getattr(event, self.cfg_ana.other_particles)

        n_lep = self.cfg_ana.n_lep
        n_min = self.cfg_ana.n_min

        self.counters.counter('events').inc('All events')

        if len(leptons) == n_lep:
            self.counters.counter('events').inc('1 lepton')
        if len(other_particles) >= n_min:
            self.counters.counter('events').inc('4 particles')

        if len(leptons) == n_lep and len(other_particles) >= n_min:
            self.counters.counter('events').inc('1 lepton && 4 particles')
        else:
            return False
