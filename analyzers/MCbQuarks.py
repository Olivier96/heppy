from heppy.framework.analyzer import Analyzer
from heppy.utils.delta_alpha import delta_alpha
from heppy.utils.second_smallest_number import second_smallest_number

class MCbQuarks(Analyzer):
    '''Find the montecarlo b-quarks and match them with the reconstructed jets.

    Useful for ttbar analysis.

    Jets collection order must not be modified because jets are sorted by btag
    (this could be changed in  the future).

    Algorithm steps:
    - looping on gen_ptc searching for tops, and on tops daughters searching
    for b quarks
    - b quarks get as attribute the list of the delta_alpha wrt to the jets
    - the matching is done looking at the closest jet (with delta_alpha) to
    the b quark
    - if the closest jet to the first quark is the same as the closest one to
    the second quark:
        - consider the closest quark to the jet of the two quarks
        - match it with the jet
        - the remaining quark is then matched to its next to closest jet

    Each b-quark get the following attributes:
    - index_nearest_jet: index of the matched jet
    - nearest_jet: the matched jet
    - delta_alpha_wrt_nearest_jet: delta alpha wrt the matched jet
    - delta_alpha_wrtJets: list of delta alpha wrt all the jets

    Then each jet get the attribute mc_b_quark_index =:
    - 0 if it has no matching with a b-quark
    - 1 if it is matched with the first b-quark
    - 2 it it is matched with the second b-quark

    here is an example:
    from heppy.analyzers.MCbQuarks import MCbQuarks
    mc_b_quarks = cfg.Analyzer(
      MCbQuarks,
      output = 'mc_b_quarks',
      jets = 'jets',
    )
    '''

    def process(self, event):

        gen_particles = event.gen_particles
        
        # list containing all top quarks in one event
        tops = []
        for gen_ptc in gen_particles:
            if abs(gen_ptc.pdgid()) == 6:
                tops.append(gen_ptc)
                
        
        # list containing all b quarks 
        mc_b_quarks = []

        for top in tops:
            for daughter in top.daughters:
                if abs(daughter.pdgid()) == 5:
                    mc_b_quarks.append(daughter)


        jets = getattr(event, self.cfg_ana.jets)
        for quark in mc_b_quarks:
            quark.delta_alpha_wrtJets = []
            for jet in jets:
                quark.delta_alpha_wrtJets.append(delta_alpha(quark, jet))

        # protect from not bW decay! also 0 bquarks, set index to FLAG value to identify problem later if necessary
        if len(mc_b_quarks) == 2:
            index_nearest_jet1 = mc_b_quarks[0].delta_alpha_wrtJets.index(min(mc_b_quarks[0].delta_alpha_wrtJets))
            index_nearest_jet2 = mc_b_quarks[1].delta_alpha_wrtJets.index(min(mc_b_quarks[1].delta_alpha_wrtJets))
            
            # Only makes sense in case 2 quarks are identified!
            # if both quarks share the same closest jet: tag the jet to the bquark closest to the jet
            if index_nearest_jet1 == index_nearest_jet2:
                if min(mc_b_quarks[0].delta_alpha_wrtJets) <= min(mc_b_quarks[1].delta_alpha_wrtJets):
                    index_nearest_jet2 = second_smallest_number(mc_b_quarks[1].delta_alpha_wrtJets)[1]
            # and match the second b quark the the other closest jet
                elif min(mc_b_quarks[0].delta_alpha_wrtJets) > min(mc_b_quarks[1].delta_alpha_wrtJets):
                    index_nearest_jet1 = second_smallest_number(mc_b_quarks[0].delta_alpha_wrtJets)[1]
        
        
        elif len(mc_b_quarks) == 1:
            print "Warning in MCbQuark.py: only 1 b quark produced in the event\n"
            index_nearest_jet1 = mc_b_quarks[0].delta_alpha_wrtJets.index(min(mc_b_quarks[0].delta_alpha_wrtJets))
            index_nearest_jet2 = -10
        else:
            print "Warning in MCbQuark.py: Zero b quarks produced in the event\n"
            index_nearest_jet1 = -10
            index_nearest_jet2 = -10


        if len(mc_b_quarks) > 0:
            mc_b_quarks[0].index_nearest_jet = index_nearest_jet1
            mc_b_quarks[0].nearest_jet = jets[index_nearest_jet1]
            mc_b_quarks[0].delta_alpha_wrt_nearest_jet = mc_b_quarks[0].delta_alpha_wrtJets[index_nearest_jet1]
        if len(mc_b_quarks) > 1:
            mc_b_quarks[1].index_nearest_jet = index_nearest_jet2
            mc_b_quarks[1].nearest_jet = jets[index_nearest_jet2]
            mc_b_quarks[1].delta_alpha_wrt_nearest_jet = mc_b_quarks[1].delta_alpha_wrtJets[index_nearest_jet2]

        for i, jet in enumerate(jets):
            if i == index_nearest_jet1:
                jet.mc_b_quark_index = 1
            elif i == index_nearest_jet2:
                jet.mc_b_quark_index = 2
            else:
                jet.mc_b_quark_index = 0

        setattr(event, self.cfg_ana.output, mc_b_quarks)
