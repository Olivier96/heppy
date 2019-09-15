from heppy.framework.analyzer import Analyzer
from heppy.statistics.counter import Counter, Counters

class CheckGenLeptons(Analyzer):
    '''
    Example:
    from heppy.analyzers.CheckGenLeptons import CheckGenLeptons
    check_gen_leptons = cfg.Analyzer(
      CheckGenLeptons,
      objects = 'gen_leptons',
      n_lep = 1,
      energy_cut = 8,
    )
    '''
 
    def beginLoop(self, setup):
        super(CheckGenLeptons, self).beginLoop(setup)

        self.counters.addCounter('events')
        self.counters.counter('events').register('All events')
        self.counters.counter('events').register('One Gen lepton')


    def process(self, event):
        input_collection = getattr(event, self.cfg_ana.objects)

        n_good_lepton = 0
        for lepton in input_collection:
            if lepton.e() > self.cfg_ana.energy_cut:
                n_good_lepton += 1
        self.counters.counter('events').inc('All events')
        if len(input_collection) >= self.cfg_ana.n_lep:
            self.counters.counter('events').inc('One Gen lepton')
        else:
            print "No MC leptons found with energy > energy_cut: {} GeV".format(self.cfg_ana.energy_cut)
            print "Disabled the return False statement in CheckGenLeptons.py analyzer for now"
            #return False
