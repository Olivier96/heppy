from detector import Detector, DetectorElement
import material as material
from geometry import VolumeCylinder
import math
import random


class ECAL(DetectorElement):

    def __init__(self):
        volume = VolumeCylinder('ecal', 2.02, 2.348, 1.808, 2.348)
        mat = material.Material('ECAL', 3.5e-3, 0.111)
        self.eta_crack = 3
        self.emin = 0.1
        self.eres = [0.17, 0., 0.01]
        super(ECAL, self).__init__('ecal', volume,  mat)


    def energy_resolution(self, energy, theta=0.):
        stoch = self.eres[0] / math.sqrt(energy)
        noise = self.eres[1] / energy
        constant = self.eres[2]
        return math.sqrt( stoch**2 + noise**2 + constant**2)

    def energy_response(self, energy, eta=0):
        return 1.

    def cluster_size(self, ptc):
        pdgid = abs(ptc.pdgid())
        if pdgid==22 or pdgid==11:
            return 0.005
        else:
            return 0.01


    def acceptance(self, cluster):
        energy = cluster.energy
        eta = abs(cluster.position.Eta())
        if eta < self.eta_crack:
            return energy > self.emin
        else:
            return False

    def space_resolution(self, ptc):
        pass


class HCAL(DetectorElement):

    def __init__(self):
        volume = VolumeCylinder('hcal', 3.33, 2.348, 2.02, 2.348)
        mat = material.Material('HCAL', 1.74e-3, 0.17)
        self.eta_crack = 3.
        self.eres = [0.5, 0., 0.]
        super(HCAL, self).__init__('hcal', volume, mat)


    def energy_resolution(self, energy, theta=0.):
        stoch = self.eres[0] / math.sqrt(energy)
        noise = self.eres[1] / energy
        constant = self.eres[2]
        return math.sqrt( stoch**2 + noise**2 + constant**2)


    def energy_response(self, energy, eta=0):
        return 1.

    def cluster_size(self, ptc):
        return 0.2


    def acceptance(self, cluster):
        energy = cluster.energy
        eta = abs(cluster.position.Eta())
        if eta < self.eta_crack :
            return energy>1.
        else:
            return False

    def space_resolution(self, ptc):
        pass


class Tracker(DetectorElement):

    def __init__(self):
        volume = VolumeCylinder('tracker',1.808, 2.348)
        mat = material.void
        super(Tracker, self).__init__('tracker', volume, mat)

    def acceptance(self, track):
        pt = track.pt
        eta = abs(track.p3.Eta())
        if eta < 2.4 and pt>0.1:
            return random.uniform(0,1)<1.
        else:
            return False

    def pt_resolution(self, track):
        pt = track.pt
	eta = abs(track.p3.Eta())
        if eta < 1.5:
            return 1e-2
        else:
            return False

class Field(DetectorElement):

    def __init__(self, magnitude):
        self.magnitude = magnitude
        volume = VolumeCylinder('field', 1.8, 2.4)
        mat = material.void
        super(Field, self).__init__('tracker', volume,  mat)

class BeamPipe(DetectorElement):

    def __init__(self):
        #Material Seamless AISI 316 LN, External diameter 53 mm, Wall thickness 1.5 mm (hors cms) X0 1.72 cm
        #in CMS, radius 25 mm (?), tchikness 8mm, X0 35.28 cm : berylluim
        factor = 1.0
        volume = VolumeCylinder('beampipe', 2.5e-2*factor+0.8e-3, 1.98, 2.5e-2*factor, 1.9785 )
        mat = material.Material('BeamPipe', 1e99, 0)
        super(BeamPipe, self).__init__('beampipe', volume, mat)

class ILD(Detector):

    def electron_acceptance(self, track):
        return track.p3.Mag() > 0.2 and abs(track.p3.Eta()) < 2.4

    def electron_energy_resolution(self, ptc):
        return 0.1 / math.sqrt(ptc.e())

    def muon_acceptance(self, track):
        return track.p3.Mag() > 0.2 and abs(track.p3.Eta()) < 2.4

    def muon_pt_resolution(self, ptc):
        return 0.005

    def __init__(self):
        super(ILD, self).__init__()
        self.elements['tracker'] = Tracker()
        self.elements['ecal'] = ECAL()
        self.elements['hcal'] = HCAL()
        self.elements['field'] = Field(3.5)
        self.elements['beampipe'] = BeamPipe()

ild = ILD()
