from heppy.framework.analyzer import Analyzer


class MCwBosons(Analyzer):
    '''Find the Monte-Carlo W bosons from top quarks

    Useful to recover the top mass distribution using reconstruction data
    '''
    
    def process(self, event):

        gen_particles = event.gen_particles
        
        # list containing all top quarks in one event
        tops = []
        for gen_ptc in gen_particles:
            if abs(gen_ptc.pdgid()) == 6:
                tops.append(gen_ptc)
                
        # Make a list of the W bosons.
        mc_w_bosons = []
        for top in tops:
            for daughter in top.daughters:
                if abs(daughter.pdgid()) == 24:
                    # Decayed particle is a W:
                    # If W decays again to a W > l +W then save the second W!
                    w_daughter_idlist = [w_daughter.pdgid() for w_daughter in daughter.daughters]
                    if (24 in w_daughter_idlist) or (-24 in w_daughter_idlist):
                        for w_daughter in daughter.daughters:
                            if abs(w_daughter.pdgid()) == 24:
                                w_daughter_daughter_idlist = [w_daughter_daughter.pdgid() for w_daughter_daughter in w_daughter.daughters]
                                if (24 in w_daughter_daughter_idlist) or (-24 in w_daughter_daughter_idlist):
                                    for w_daughter_daughter in w_daughter.daughters:
                                        w_d3_idlist = [w_d3.pdgid() for w_d3 in w_daughter_daughter.daughters]
                                        if (24 in w_d3_idlist) or (-24 in w_d3_idlist):
                                            for w_d3 in w_daughter_daughter.daughters:
                                                w_d4_idlist = [w_d4.pdgid() for w_d4 in w_d3.daughters]
                                                if (24 in w_d4_idlist) or (-24 in w_d4_idlist):
                                                    for w_d4 in w_d3.daughters:
                                                        if abs(w_d4.pdgid()) == 24: 
                                                            mc_w_bosons.append(w_d4)
                                                else:
                                                    mc_w_bosons.append(w_d3)
                                        else:
                                            mc_w_bosons.append(w_daughter_daughter)
                                else:
                                    mc_w_bosons.append(w_daughter)
                    else:
                        mc_w_bosons.append(daughter)
                
        setattr(event, self.cfg_ana.output, mc_w_bosons)


