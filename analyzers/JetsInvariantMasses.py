from heppy.framework.analyzer import Analyzer
from ROOT import TLorentzVector
from itertools import combinations
from heppy.utils.delta_alpha import delta_alpha
from heppy.utils.pt_wrt_axis import pt_wrt_axis

class JetsInvariantMasses(Analyzer):
    '''Store some variables related to the invariant masses of the jets.

    The analyzer computes:
    - four_jets_mass: invariant mass of the jets in the event
    - the invariant mass of every possible pair of jets
    then store:
    - four_jets_mass
    - min_jets_mass: smallest invariant mass of a pair of jets
    - second_min_jets_mass: next to smallest invariant mass of a pair of jets

    Here is an example:
    from heppy.analyzers.JetsInvariantMasses import JetsInvariantMasses
    jets_variables = cfg.Analyzer(
      JetsInvariantMasses,
      jets = 'jets',
      leptons = 'sel_iso_leptons'
    )

    TODO: expand documentation with new variables
    '''

    def process(self, event):
        jets = getattr(event, self.cfg_ana.jets)
        lepton = getattr(event, self.cfg_ana.leptons)[0]

        jets_energies = [jet.e() for jet in jets]
        jets_energies.sort()
        max_jet_e = jets_energies[-1]
        min_jet_e = jets_energies[0]

        four_jets_mass = 0.
        min_jets_mass = 0.
        second_min_jets_mass = 0.
        max_jets_mass = 0.

        def invariant_mass(ptc_list):
            totalp4 = TLorentzVector(0., 0., 0., 0.)
            for ptc in ptc_list:
                totalp4 += ptc.p4()
            return totalp4.M()

        four_jets_mass = invariant_mass(jets)

        inv_masses = []
        angles = []

        for combination in combinations(jets, 2):
            aux_m_inv = invariant_mass(combination)
            inv_masses.append(aux_m_inv)
            aux_angle = delta_alpha(combination[0], combination[1])
            angles.append(aux_angle)

        inv_masses.sort(key=lambda x: x)
        min_jets_mass = inv_masses[0]
        second_min_jets_mass = inv_masses[1]
        max_jets_mass = inv_masses[-1]

        angles.sort(key=lambda x: x)
        min_jets_angle = angles[0]
        second_min_jets_angle = angles[1]
        max_jets_angle = angles[-1]


        jets_p4 = TLorentzVector(0., 0., 0., 0.)
        jets_sumpt = 0.
        jets_sump = 0.

        lepton.angle_pt_wrt_jets = []
        for jet in jets:
            lepton.angle_pt_wrt_jets.append((delta_alpha(lepton, jet),
                                          pt_wrt_axis(jet.p3(), [lepton])))
            jets_p4 += jet.p4()
            jets_sumpt += jet.p4().Pt()
            jets_sump += jet.p4().P()

        lepton.angle_pt_wrt_jets.sort(key=lambda x: x[0])
        min_jets_lepton_angle = lepton.angle_pt_wrt_jets[0][0]
        second_min_jets_lepton_angle = lepton.angle_pt_wrt_jets[1][0]
        max_jets_lepton_angle = lepton.angle_pt_wrt_jets[-1][0]

        lep_pt_wrt_closest_jet = lepton.angle_pt_wrt_jets[0][1]
        lep_pt_wrt_second_closest_jet = lepton.angle_pt_wrt_jets[1][1]
        lep_pt_wrt_farthest_jet = lepton.angle_pt_wrt_jets[-1][1]

        total_rec_mass = (jets_p4 + lepton.p4()).M()
        jets_vecp_over_sump = jets_p4.P() / jets_sump

        #store variables
        event.max_jet_e = max_jet_e
        event.min_jet_e = min_jet_e

        event.four_jets_mass = four_jets_mass
        event.min_jets_mass = min_jets_mass
        event.second_min_jets_mass = second_min_jets_mass
        event.max_jets_mass = max_jets_mass
        event.min_jets_angle = min_jets_angle
        event.second_min_jets_angle = second_min_jets_angle
        event.max_jets_angle = max_jets_angle

        event.min_jets_lepton_angle = min_jets_lepton_angle
        event.second_min_jets_lepton_angle = second_min_jets_lepton_angle
        event.max_jets_lepton_angle = max_jets_lepton_angle
        event.lep_pt_wrt_closest_jet = lep_pt_wrt_closest_jet
        event.lep_pt_wrt_second_closest_jet = lep_pt_wrt_second_closest_jet
        event.lep_pt_wrt_farthest_jet = lep_pt_wrt_farthest_jet

        event.total_rec_mass = total_rec_mass
        event.jets_sumpt = jets_sumpt
        event.jets_vecp_over_sump = jets_vecp_over_sump
