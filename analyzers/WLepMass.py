from heppy.framework.analyzer import Analyzer
from heppy.particles.tlv.resonance import Resonance

class WLepMass(Analyzer):
    '''
    from heppy.analyzers.WLepMass import WLepMass
    w_lep_mass = cfg.Analyzer(
        WLepMass,
    )
    '''

    def process(self, event):
        leptons = getattr(event, "sel_iso_leptons")
        missing_rec = getattr(event, "missing_rec")

        w_lep = Resonance([leptons[0], missing_rec], 24)

        setattr(event, "w_lep", w_lep)
