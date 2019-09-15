from heppy.framework.analyzer import Analyzer
from ROOT import TVector3, TLorentzVector
from heppy.papas.path import Helix
import math
import random
from heppy.utils.computeIP import *

debug = False

class ImpactParameterWrtJetDir(Analyzer):
    '''
    def track_selection_function(track):
        return track.q() != 0 and \
        abs(track.path.smeared_impact_parameter) < 2.5e-3 and \
        track.path.ip_resolution < 7.5e-4 and \
        track.e() > 0.4 and \
        track.path.min_dist_to_jet.Mag() < 7e-4 and \
        track.path.min_dist_to_jet_significance < 10 and \
        track.path.jet_point_min_approach.Mag() < 1e-2

    import math
    def aleph_resolution(ptc):
        momentum = ptc.p3().Mag()
        return math.sqrt(25.**2 + 95.**2/ (momentum**2) )*1e-6
    def ild_resolution(ptc):
        momentum = ptc.p3().Mag()
        theta = ptc.p4().Theta()
        return math.sqrt(5.**2 + 10**2/ (momentum**2 * math.sin(theta)**3 ) )*1e-6

    from analyzers.ImpactParameterWrtJetDir import ImpactParameterWrtJetDir
    ip_wrt_jet_dir = cfg.Analyzer(
        ImpactParameterWrtJetDir,
        jets = 'jets',
        track_selection = track_selection_function,
        resolution = aleph_resolution
    )
    '''
    def dump(self, particle):
        print
        print "NEW track"
        print
        print "resolution", particle.path.ip_resolution
        print "smear_factor_x", particle.path.ip_smear_factor_x
        print "smear_factor_y", particle.path.ip_smear_factor_y

        print "vector_impact_parameter", particle.path.vector_impact_parameter.Mag()
        particle.path.vector_impact_parameter.Dump()
        print "vector_ip_rotated", particle.path.vector_ip_rotated.Mag()
        particle.path.vector_ip_rotated.Dump()
        print "vector_ip_rotated_smeared", particle.path.vector_ip_rotated_smeared.Mag()
        particle.path.vector_ip_rotated_smeared.Dump()
        print

    def m_inv_second_vertex(self, event, jet):
        jet_tracks = []
        for id, ptcs in jet.constituents.iteritems():
            for ptc in ptcs :
                if self.cfg_ana.track_selection(ptc) == True and \
                ptc.path.significance_impact_parameter > 0:
                    jet_tracks.append(ptc)

        if len(jet_tracks) == 0:
            if debug:
                print
                print "inside the jet there are no good charged particles"
                print
            return -1, -1, 0

        jet_tracks.sort(key = lambda ptc: -ptc.path.significance_impact_parameter)

        most_significant_ptc_rec = jet_tracks[0]
        if debug:
            print
            print
            print "most_significant_ptc_rec: ", most_significant_ptc_rec
            print
        if hasattr(most_significant_ptc_rec, 'match'):
            most_significant_ptc_gen = most_significant_ptc_rec.match
            if debug:
                print
                print "most_significant_ptc_gen: ", most_significant_ptc_gen
                print
        else:
            if debug:
                print
                print "most_significant_ptc_gen has no matching"
                print
            import pdb; pdb.set_trace()

        if debug:
            print
            print
            print
            print "msp mothers"
            for ptc in most_significant_ptc_gen.mothers:
                print ptc
            print
            if len(most_significant_ptc_gen.mothers) != 1:
                for i, mother in enumerate(most_significant_ptc_gen.mothers):
                    print "mother", i
                    print mother
                    print
                    print mother.mothers
                    print
                    # for mot in mother.mothers:
                    #     print mot.mothers
                    #     for p in mot.mother.mothers:
                    #         print mot.mothers
                    #     print
                    print
            print

        if len(most_significant_ptc_gen.mothers) != 1:
            if debug:
                print
                print "msp has no mother"
                print
            return -2, -2, 0
        else:
            msp_gen_mother = most_significant_ptc_gen.mothers[0]

        jet_tracks_second_vertex = []


        for daughter in event.genbrowser.descendants(msp_gen_mother):
            if debug:
                print
                print "gen_daughter", daughter
            if daughter.status() == 1 and daughter.q() != 0:

                if hasattr(daughter, 'match'):
                    rec_daughter = daughter.match
                    if debug:
                        print
                        print rec_daughter
                    if rec_daughter != None:
                        if rec_daughter in jet_tracks:
                            jet_tracks_second_vertex.append(rec_daughter)
                            if debug:
                                print "it's in the jet_tracks"
                else:
                    import pdb; pdb.set_trace()

        # for daughter in msp_gen_mother.daughters:
        #     # pdb.set_trace()
        #
        #     print
        #     print daughter
        #     if hasattr(daughter, 'match'):
        #         print daughter.match
        #         rec_daughter = daughter.match
        #         if rec_daughter != None:
        #             if rec_daughter in jet_tracks:
        #                 jet_tracks_second_vertex.append(rec_daughter)
        #     else:
        #         print "no attribute match for daughter"
        #         continue


        def invariant_mass(ptc_list):
            totalp4 = TLorentzVector(0,0,0,0)
            for ptc in ptc_list:
                totalp4 += ptc.p4()
            return totalp4.M()

        pdgid_msp_mother = msp_gen_mother.pdgid()
        return len(jet_tracks_second_vertex), invariant_mass(jet_tracks_second_vertex), pdgid_msp_mother

    def jet_tag(self, jet):

        logtag = 0.
        n_track = 0
        log_prob_product = 0.

        for id, ptcs in jet.constituents.iteritems():
            for ptc in ptcs :
                if self.cfg_ana.track_selection(ptc) == True and \
                ptc.path.significance_impact_parameter > 0:
                    n_track += 1
                    log_prob_product += 0.5 * ptc.path.significance_impact_parameter**2

        if n_track == 0:
            jet.btag = 1
            jet.logbtag = 0
            jet.log10btag = 0
        else:
            sum_tr = 0
            for j in range(n_track):
                sum_tr += (log_prob_product)**j/math.factorial(j)

            logtag = log_prob_product - math.log(sum_tr)

            jet.btag = math.exp(-logtag)
            jet.logbtag = logtag
            jet.log10btag = - logtag * math.log10(math.exp(1))

    def track_multiplicty(self, jet, significance, sign):
        track_list = []

        for id, ptcs in jet.constituents.iteritems():
            for ptc in ptcs :
                if self.cfg_ana.track_selection(ptc) == True:
                    if sign == 1:
                        if ptc.path.significance_impact_parameter > significance:
                            track_list.append(ptc)
                    elif sign == -1:
                        if ptc.path.significance_impact_parameter < significance:
                            track_list.append(ptc)
                    elif sign == 0:
                        track_list.append(ptc)

        def invariant_mass(ptc_list):
            totalp4 = TLorentzVector(0,0,0,0)
            for ptc in ptc_list:
                totalp4 += ptc.p4()
            return totalp4.M()

        return len(track_list), invariant_mass(track_list)

    def track_probability(self, particle):

        def gaussian(x):
            return math.exp((-0.5)*x**2)

        track_prob = 0
        track_prob = gaussian(particle.path.significance_impact_parameter)
        if particle.path.significance_impact_parameter < 0:
            return (-1)*track_prob
        else:
            return track_prob

    def smearing_significance_IP(self, ptc):

        resolution = self.cfg_ana.resolution(ptc)
        ptc.path.ip_resolution = resolution

        ptc.path.x_prime = ptc.path.vector_impact_parameter.Mag()*math.cos(ptc.path.vector_impact_parameter.Phi())
        ptc.path.y_prime = ptc.path.vector_impact_parameter.Mag()*math.sin(ptc.path.vector_impact_parameter.Phi())
        ptc.path.z_prime = 0

        ptc.path.vector_ip_rotated = TVector3(ptc.path.x_prime, ptc.path.y_prime, ptc.path.z_prime)

        ptc.path.ip_smear_factor_x = random.gauss(0, ptc.path.ip_resolution)
        ptc.path.ip_smear_factor_y = random.gauss(0, ptc.path.ip_resolution)
        ptc.path.x_prime_smeared = ptc.path.x_prime + ptc.path.ip_smear_factor_x
        ptc.path.y_prime_smeared = ptc.path.y_prime + ptc.path.ip_smear_factor_y
        ptc.path.z_prime_smeared = 0

        ptc.path.vector_ip_rotated_smeared = TVector3(ptc.path.x_prime_smeared, ptc.path.y_prime_smeared, ptc.path.z_prime_smeared)

        ptc.path.smeared_impact_parameter = ptc.path.vector_ip_rotated_smeared.Mag() * ptc.path.sign_impact_parameter

        ptc.path.significance_impact_parameter = ptc.path.smeared_impact_parameter / ptc.path.ip_resolution

        ptc.path.track_probability = self.track_probability(ptc)

        ptc.path.min_dist_to_jet_significance = ptc.path.sign_impact_parameter* ptc.path.min_dist_to_jet.Mag() / ptc.path.ip_resolution

    def process(self, event):

        if debug:
            print event.iEv

        primary_vertex = TVector3(0, 0, 0)
        jets = getattr(event, self.cfg_ana.jets)

        for i, jet in enumerate(jets):
            for id, ptcs in jet.constituents.iteritems():
                for ptc in ptcs :
                    if ptc.q() == 0 :
                        continue
                    compute_IP_wrt_direction(ptc.path, primary_vertex, jet.p3())
                    self.smearing_significance_IP(ptc)

            if debug:
                print
                print "jet ", i
                print

            self.jet_tag(jet)

            # jet.n_charged, jet.m_inv_charged = self.track_multiplicty(jet,0,0)
            # jet.n_signif_larger3, jet.m_inv_signif_larger3 = self.track_multiplicty(jet,3,1)
            # jet.n_signif_larger2, jet.m_inv_signif_larger2 = self.track_multiplicty(jet,2,1)
            # jet.n_signif_larger0, jet.m_inv_signif_larger0 = self.track_multiplicty(jet,0,1)
            # jet.n_signif_smaller0, jet.m_inv_signif_smaller0 = self.track_multiplicty(jet,0,-1)
            #
            # jet.n_second_vertex, jet.m_inv_second_vertex, jet.pdgid_mother_second_vertex = self.m_inv_second_vertex(event, jet)
