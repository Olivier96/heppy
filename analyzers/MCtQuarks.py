from heppy.framework.analyzer import Analyzer


class MCtQuarks(Analyzer):
    '''Find the Monte-Carlo top quarks

    Useful to recover the top mass distribution using reconstruction data
    '''
    
    def process(self, event):

        gen_particles = event.gen_particles
        
        # list containing all top quarks in one event
        mc_t_quarks = []
        for gen_ptc in gen_particles:
            if abs(gen_ptc.pdgid()) == 6:
                #gen_ptc_idlist = [x.pdgid() for x in gen_ptc.daughters]
                #if ((5 in gen_ptc_idlist) or (-5 in gen_ptc_idlist)) and ((24 in gen_ptc_idlist) or (-24 in gen_ptc_idlist)):
                mc_t_quarks.append(gen_ptc)
                
                
        setattr(event, self.cfg_ana.output, mc_t_quarks)
