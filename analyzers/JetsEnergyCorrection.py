from heppy.framework.analyzer import Analyzer

class JetsEnergyCorrection(Analyzer):
    '''
    from analyzers.JetsEnergyCorrection import JetsEnergyCorrection
    jets_variables = cfg.Analyzer(
      JetsEnergyCorrection,
      jets = 'jets',
      corrective_factor = 91. / 97.89
    )
    '''

    def process(self, event):
        jets = getattr(event, self.cfg_ana.jets)
        corrective_factor = self.cfg_ana.corrective_factor

        for jet in jets:
            energy = jet.e()
            jet.p4().SetE(energy * corrective_factor)
