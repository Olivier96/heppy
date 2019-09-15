from heppy.framework.analyzer import Analyzer
from heppy.particles.tlv.particle import Particle
from heppy.utils.topConstrainer import topConstrainer

w_pdgid = 24
top_pdgid = 6

w_charge = 1
top_charge = 0.66

class TopConstrainerAnalyzer(Analyzer):

    '''Builds w and top resonances using kineamatic constraint.
    Example:
    from TopConstrainerAnalyzer import TopConstrainerAnalyzer
    top_constrainer = cfg.Analyzer(
      TopConstrainerAnalyzer,
      jets = 'jets',
      leptons = 'leptons',
      sqrts = 350.,
      top_mass = 173.,
      w_mass = 80.4,
      tophadRec_m = 164.59,
      tophadRec_w = 17.13,
      whadRec_m = 81.88,
      whadRec_w = 16.69,
      toplepRec_m = 177.37,
      toplepRec_w = 20.25,
      wlepRec_m = 105.43,
      wlepRec_w = 17.37,
    )
    '''

    def process(self, event):
        leptons = getattr(event, self.cfg_ana.leptons)
        jets = getattr(event, self.cfg_ana.jets)
        sqrts = self.cfg_ana.sqrts
        w_mass = self.cfg_ana.w_mass
        top_mass = self.cfg_ana.top_mass

        jets_p4 = []
        btags = []
        for jet in jets:
            jets_p4.append(jet.p4())
            btags.append(jet.logbtag)

        if len(leptons) == 0:
            event.success = -1
        else:
            myTopConstrainer = topConstrainer(jets_p4, btags, leptons[0].p4(), sqrts, w_mass, top_mass)
            succeded, chi2 = myTopConstrainer.rescale(1E-4)

            if succeded:
                pRec = myTopConstrainer.p_ini
                tophadRec = Particle(top_pdgid, top_charge, (pRec[0]+pRec[1]+pRec[2]) )
                whadRec = Particle(w_pdgid, w_charge, (pRec[0]+pRec[1]) )
                toplepRec = Particle(top_pdgid, top_charge, (pRec[3]+pRec[4]+pRec[5]) )
                wlepRec = Particle(w_pdgid, w_charge, (pRec[4]+pRec[5]) )
                missingMassRec = Particle( 0, 0, pRec[5] )

                pFit = myTopConstrainer.p_out
                tophadFit = Particle(top_pdgid, top_charge, (pFit[0]+pFit[1]+pFit[2]) )
                whadFit = Particle(w_pdgid, w_charge, (pFit[0]+pFit[1]) )
                toplepFit = Particle(top_pdgid, top_charge, (pFit[3]+pFit[4]+pFit[5]) )
                wlepFit = Particle(w_pdgid, w_charge, (pFit[4]+pFit[5]) )
                missingMassFit = Particle( 0, 0, pFit[5] )

                chi2_tophadRec = ( (tophadRec.m() - self.cfg_ana.tophadRec_m) / self.cfg_ana.tophadRec_w )**2
                chi2_whadRec = ( (whadRec.m() - self.cfg_ana.whadRec_m) / self.cfg_ana.whadRec_w )**2
                chi2_toplepRec = ( (toplepRec.m() - self.cfg_ana.toplepRec_m) / self.cfg_ana.toplepRec_w )**2
                chi2_wlepRec = ( (wlepRec.m() - self.cfg_ana.wlepRec_m) / self.cfg_ana.wlepRec_w )**2
                chi2_top_constrainer = chi2_tophadRec + chi2_whadRec + chi2_toplepRec + chi2_wlepRec

                setattr(event, 'success', 1)
                setattr(event, 'chi2_algorithm', chi2)

                setattr(event, 'tophadRec', tophadRec)
                setattr(event, 'whadRec', whadRec)
                setattr(event, 'toplepRec', toplepRec)
                setattr(event, 'wlepRec', wlepRec)
                setattr(event, 'missingMassRec', missingMassRec)
                setattr(event, 'tophadFit', tophadFit)
                setattr(event, 'whadFit', whadFit)
                setattr(event, 'toplepFit', toplepFit)
                setattr(event, 'wlepFit', wlepFit)
                setattr(event, 'missingMassFit', missingMassFit)

                setattr(event, 'chi2_tophadRec', chi2_tophadRec)
                setattr(event, 'chi2_whadRec', chi2_whadRec)
                setattr(event, 'chi2_toplepRec', chi2_toplepRec)
                setattr(event, 'chi2_wlepRec', chi2_wlepRec)

                setattr(event, 'chi2_top_constrainer', chi2_top_constrainer)

            else:
                event.success = 0
