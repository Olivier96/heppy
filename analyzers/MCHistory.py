from heppy.framework.analyzer import Analyzer
from heppy.particles.genbrowser import GenBrowser

class MCHistory(Analyzer):
    '''
    from analyzers.MCHistory import MCHistory
    mc_history = cfg.Analyzer(
        MCHistory
    )
    '''

    def process(self, event):
        event.genbrowser = GenBrowser(event.gen_particles, event.gen_vertices)
