from heppy.framework.analyzer import Analyzer
from heppy.particles.tlv.particle import Particle
from ROOT import TLorentzVector

class CheckParticleNumberForJetClustering(Analyzer):
    '''
    from analyzers.CheckParticleNumberForJetClustering import CheckParticleNumberForJetClustering
    checker = cfg.Analyzer(
      CheckParticleNumberForJetClustering,
      input = 'particles_not_iso_lep',
      n_min = 4
    )
    '''

    def process(self, event):
        input_collection = getattr(event, self.cfg_ana.input)
        n_min = self.cfg_ana.n_min


        if len(input_collection) < n_min:
            return False

        # if len(input_collection) < n_min:
        #     event.number_jets = len(input_collection)
        # else:
        #     event.number_jets = n_min
        #
        # while len(input_collection) < n_min:
        #     input_collection.append( Particle( 22, 0, TLorentzVector(1e-5, 0, 0, 1e-5), 1) )
