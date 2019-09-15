from heppy.framework.analyzer import Analyzer
from heppy.utils.delta_alpha import delta_alpha
from heppy.utils.second_smallest_number import second_smallest_number
# Delta alpha calculates the 


class MCQuarkJetFinder(Analyzer):
    ''' Find the quarks that leads to jets, including t > b and W > qq
    Store all the information about the quark E, px,py,pz, ... as for other particles and store the pdgid extra
    
    Also gives back the decay channel as output:
    DECAY CHANNEL:
    -1: default
    1: semileptonic
    2: dileptonic
    3: hadronic
    
    call in a sequence as:
    
    from heppy.analyzers.MCQuarkJetFinder import MCQuarkJetFinder
    mc_quarkjets = cfg.Analyzer(
        MCQuarkJetFinder,
        output1 = 'mc_b_quarks',
        output2 = 'mc_quark_jets',
        jets = 'jets',
    )
    
    '''
    
    def process(self, event):
        
        # define helper function (from Nicolo MCLeptonFinder)
        def match_lepton(lepton):

            if abs(lepton.pdgid()) in [11, 13]:
                if lepton.status() == 1:
                    #setattr(event, self.cfg_ana.output1, lepton)
                    return 1
                else:
                    for stable_lepton in event.genbrowser.descendants(w):
                        if stable_lepton.pdgid() == lepton.pdgid() and stable_lepton.status() == 1:
                            #setattr(event, self.cfg_ana.output1, stable_lepton)
                            return 1
                    print "error, didn't find any stable lepton among lepton.descendants"
                    import pdb; pdb.set_trace()
                    return False

            elif abs(lepton.pdgid()) == 15:
                if lepton.status() == 2:
                    #setattr(event, self.cfg_ana.output1, lepton)
                    return 1
                else:
                    for stable_lepton in event.genbrowser.descendants(w):
                        if stable_lepton.pdgid() == lepton.pdgid() and stable_lepton.status() == 2:
                            #setattr(event, self.cfg_ana.output1, stable_lepton)
                            #found = True
                            return 1
                    print "error, didn't find any stable tau among lepton.descendants"
                    import pdb; pdb.set_trace()
                    return False

            elif abs(lepton.pdgid()) in [12, 14, 16]:
                if lepton.status() == 1:
                    #setattr(event, self.cfg_ana.output2, lepton)
                    return 2
                else:
                    for stable_lepton in event.genbrowser.descendants(w):
                        if stable_lepton.pdgid() == lepton.pdgid() and stable_lepton.status() == 1:
                            #setattr(event, self.cfg_ana.output2, stable_lepton)
                            #found = True
                            return 2
                    print "error, didn't find any stable neutrino among lepton.descendants"
                    import pdb; pdb.set_trace()
                    return False

            elif abs(lepton.pdgid()) == 24:
                sum_lep = 0
                for ptc_daughter in lepton.daughters:
                    sum_lep += match_lepton(ptc_daughter)
                return sum_lep
            else:
                return 0
        
        
        
        
        gen_particles = event.gen_particles
        
        print "\n"
        #print dir(event)
        print "="*20,event
        
        # list containing all top quarks in one event
        tops = []
        for gen_ptc in gen_particles:
            if abs(gen_ptc.pdgid()) == 6:
                #gen_ptc_idlist = [x.pdgid() for x in gen_ptc.daughters]
                #if ((5 in gen_ptc_idlist) or (-5 in gen_ptc_idlist)) and ((24 in gen_ptc_idlist) or (-24 in gen_ptc_idlist)):
                tops.append(gen_ptc)
        
        print "tops: {}".format(len(tops))
        
                
        # list containing all b quarks 
        mc_b_quarks = []
        for top in tops:
            for daughter in top.daughters:
                if abs(daughter.pdgid()) == 5:
                    mc_b_quarks.append(daughter)
        
        print "b's : {}".format(len(mc_b_quarks))
          
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
        
        print "W's : {}".format(len(mc_w_bosons))
        
        # Count the leptons and neutrinos
        n_neutrinos = 0
        n_leptons = 0
        for w in mc_w_bosons:
            for w_daughter in w.daughters:
                if match_lepton(w_daughter) == 2:
                    n_neutrinos += 1
                elif match_lepton(w_daughter) == 1:
                    n_leptons += 1
                else:
                    print "no leptons found for this W boson!"
            
        
        # Make a list of the quarks decayed from the W
        quark_idlist = [-1, 1, -2, 2, 3, -3, 4, -4, 5, -5]    

        # Find the decays 
        n_quarks = 0
        for w in mc_w_bosons:
            w_daughter_idlist = [w_daughter.pdgid() for w_daughter in w.daughters]
            print w_daughter_idlist
            for w_daughter_id in w_daughter_idlist:
                print "w daughter id: {}".format(w_daughter_id)
                if w_daughter_id in quark_idlist:
                    n_quarks = n_quarks +1
        
        # Now we have have the number of quarks, leptons and neutrinos decayed from the W from the MC.
        # Store the decay channel in a variable with values:
        # DECAY CHANNEL:
        # -1: default
        # 1: semileptonic
        # 2: dileptonic
        # 3: hadronic
        
        decay_channel = -1
        
        print "-"*41
        print "Q\tL\tv\ttops\tb\tW"
        print "{}\t{}\t{}\t{}\t{}\t{}\n".format(n_quarks, n_leptons, n_neutrinos, len(tops), len(mc_b_quarks), len(mc_w_bosons))
        
        if (n_quarks == 0 and n_leptons == 2 and n_neutrinos == 2):
            decay_channel = 2
            print "/////"+"Dileptonic decay"+"/////"
        elif (n_quarks == 2 and n_leptons == 1 and n_neutrinos == 1):
            decay_channel = 1
            print "/////"+"Semileptonic decay"+"/////"
        elif (n_quarks == 4 and n_leptons == 0 and n_neutrinos == 0):
            decay_channel = 3
            print "/////"+"Hadronic decay"+"/////"
        else:
            print "\\\\\\"+"ERROR, didnt find any suitable decay channel"+"\\\\\\"
            
        
        #print "="*50
        #print "="*50
        #print "different approach"
        
        
        
        # Set decay channel as attribute to send back to cfg TODO: add to ntuple somehow, look at top constrainer how to add to ntuple arbitrary stuff
        # Store the variable
        event.decay_channel = decay_channel
        
        quarkjets = []
        for w in mc_w_bosons:
            #print "W id: {}".format(w.pdgid())
            for ptc in w.daughters:
                #print "W daughter id: {}".format(ptc.pdgid())
                if ptc.pdgid() in quark_idlist:
                    quarkjets.append(ptc)
        
        print "N quarks leading to jets: {}".format(len(quarkjets))
        print "N b quarks leading to jets: {}".format(len(mc_b_quarks))
        print "="*20+" end of ",event
        
        jets = getattr(event, self.cfg_ana.jets)
        # First let's assign the jets to the b quarks before the hadronic decays
        for b in mc_b_quarks:
            b.delta_alpha_wrt_jets = []
            for jet in jets:
                b.delta_alpha_wrt_jets.append(delta_alpha(b,jet))
        
        indices_jets_assigned = []
        if len(mc_b_quarks) == 2:
            index_nearest_jet1 = mc_b_quarks[0].delta_alpha_wrt_jets.index(min(mc_b_quarks[0].delta_alpha_wrt_jets))
            index_nearest_jet2 = mc_b_quarks[1].delta_alpha_wrt_jets.index(min(mc_b_quarks[1].delta_alpha_wrt_jets))
            
            # If they share the same closest jet chose the quark closest to the jet
            if index_nearest_jet1 == index_nearest_jet2:
                if min(mc_b_quarks[0].delta_alpha_wrt_jets) <= min(mc_b_quarks[1].delta_alpha_wrt_jets):
                    index_nearest_jet2 = second_smallest_number(mc_b_quarks[1].delta_alpha_wrt_jets)[1]
            # and match the second b quark the the other closest jet
                elif min(mc_b_quarks[0].delta_alpha_wrt_jets) > min(mc_b_quarks[1].delta_alpha_wrt_jets):
                    index_nearest_jet1 = second_smallest_number(mc_b_quarks[0].delta_alpha_wrt_jets)[1]
        
            indices_jets_assigned = [index_nearest_jet1, index_nearest_jet2]
        
        elif len(mc_b_quarks) == 1:
            index_nearest_jet1 = mc_b_quarks[0].delta_alpha_wrt_jets.index(min(mc_b_quarks[0].delta_alpha_wrt_jets))
            indices_jets_assigned = [index_nearest_jet1]
        
        if len(mc_b_quarks) > 0:
            mc_b_quarks[0].index_nearest_jet = index_nearest_jet1
            mc_b_quarks[0].nearest_jet = jets[index_nearest_jet1]
            mc_b_quarks[0].delta_alpha_wrt_nearest_jet = mc_b_quarks[0].delta_alpha_wrt_jets[index_nearest_jet1]
        if len(mc_b_quarks) > 1:
            mc_b_quarks[1].index_nearest_jet = index_nearest_jet2
            mc_b_quarks[1].nearest_jet = jets[index_nearest_jet2]
            mc_b_quarks[1].delta_alpha_wrt_nearest_jet = mc_b_quarks[1].delta_alpha_wrt_jets[index_nearest_jet2]
        
        setattr(event, self.cfg_ana.output1, mc_b_quarks)
        
        
        indices_jets_assigned.sort()
        
        # Repeat the same procedure for the other quarks for non assigned jets
        for q in quarkjets:
            q.delta_alpha_wrt_jets = []
            for ijet,jet in enumerate(jets):
                if ijet in indices_jets_assigned:
                    # Effectively we eliminate already assigned jets from selection by artificially setting a value out of bounds.
                    q.delta_alpha_wrt_jets.append(100)
                else:
                    q.delta_alpha_wrt_jets.append(delta_alpha(q,jet))

            
        if len(quarkjets) >= 2:
            index_nearest_jet1 = quarkjets[0].delta_alpha_wrt_jets.index(min(quarkjets[0].delta_alpha_wrt_jets))
            index_nearest_jet2 = quarkjets[1].delta_alpha_wrt_jets.index(min(quarkjets[1].delta_alpha_wrt_jets))
            
            # If they share the same closest jet chose the quark closest to the jet
            if index_nearest_jet1 == index_nearest_jet2:
                if min(quarkjets[0].delta_alpha_wrt_jets) <= min(quarkjets[1].delta_alpha_wrt_jets):
                    index_nearest_jet2 = second_smallest_number(quarkjets[1].delta_alpha_wrt_jets)[1]
            # and match the second jet quark the the other closest jet
                elif min(quarkjets[0].delta_alpha_wrt_jets) > min(quarkjets[1].delta_alpha_wrt_jets):
                    index_nearest_jet1 = second_smallest_number(quarkjets[0].delta_alpha_wrt_jets)[1]
        
            #indices_jets_assigned = [index_nearest_jet1, index_nearest_jet2]
        
        elif len(quarkjets) == 1:
            index_nearest_jet1 = quarkjets[0].delta_alpha_wrt_jets.index(min(quarkjets[0].delta_alpha_wrt_jets))
            #indices_jets_assigned = [index_nearest_jet1]
        
        if len(quarkjets) > 0:
            quarkjets[0].index_nearest_jet = index_nearest_jet1
            quarkjets[0].nearest_jet = jets[index_nearest_jet1]
            quarkjets[0].delta_alpha_wrt_nearest_jet = quarkjets[0].delta_alpha_wrt_jets[index_nearest_jet1]
        if len(quarkjets) > 1:
            quarkjets[1].index_nearest_jet = index_nearest_jet2
            quarkjets[1].nearest_jet = jets[index_nearest_jet2]
            quarkjets[1].delta_alpha_wrt_nearest_jet = quarkjets[1].delta_alpha_wrt_jets[index_nearest_jet2]
        
        setattr(event, self.cfg_ana.output2, quarkjets)
            
            
        
        
        
        







