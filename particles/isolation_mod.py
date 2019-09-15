from heppy.utils.delta_alpha import delta_alpha
from heppy.utils.pt_wrt_axis import pt_wrt_axis

class Area(object):
    """Base Area interface."""
    def is_inside(self, *args):
        """returns True if *args describes a particle inside the Cone.
        *args may be the particle itself, or the correct attributes to compute
        the isolation.
        """
        pass

class Cone(Area):
    """Cone in the 3D space."""
    def  __init__(self, alpha):
        """Create a cone of angle alpha"""
        self.alpha = alpha

    def is_inside(self, *args):
        angle = delta_alpha(*args)
        return angle < self.alpha


class IsolationInfo(object):
    """Holds the results of an isolation calculation."""
    def __init__(self, label, lepton):
        """Create an IsolationInfo.
        Attributes:
        - lepton    = the lepton
        - particles = list of particles around the lepton used in the calculation.
        the following quantities are computed for these particles
        - pt_wrt_lepton = total pT of the particles wrt to lepton momentum
        - sume  = total energy for the particles
        - num   = total number of particles
        """
        self.particles = []
        self.label = label
        self.lepton = lepton
        self.pt_wrt_lepton = 0
        self.sume = 0
        self.num = 0


    def add_particle(self, ptc):
        """Add a new particle and update counters."""
        self.particles.append(ptc)
        self.sume += ptc.e()
        self.num += 1
        self.pt_wrt_lepton = pt_wrt_axis(self.lepton.p3(), self.particles)

    def __iadd__(self, other):
        self.particles.extend(other.particles)
        self.sume += other.sume
        self.num += other.num
        self.pt_wrt_lepton = pt_wrt_axis(self.lepton.p3(), self.particles)
        return self

    def __str__(self):
        return 'iso {label:>3}: pt_wrt_lepton = {pt_wrt_lepton:5.2f}, sume = {sume:5.2f}, num = {num}'.format(
            label = self.label,
            pt_wrt_lepton = self.pt_wrt_lepton,
            sume = self.sume,
            num = self.num
        )



class IsolationComputer(object):
    """Computes isolation for a given lepton."""

    def __init__(self, on_areas, off_areas=None,
                 e_thresh=0, label=''):
        """Creates the isolation computer.
        Particles around the lepton are considered in the isolation if:
        - they pass the threshold:
          e_thresh  : energy threshold
        - they are in an active area around the lepton
        areas should
        on_areas and off_areas are lists of areas in which particles
        around the should be considered
        or ignored, respectively.
        for a given particle
        """

        self.on_areas = on_areas
        if off_areas is None:
            off_areas = []
        self.off_areas = off_areas
        self.e_thresh = e_thresh
        self.label = label


    def compute(self, lepton, particles, debug = False):
        """Compute the isolation for lepton, using particles.
        returns an IsolationInfo.
        """
        isolation = IsolationInfo(self.label, lepton)
        if debug:
            print
            print "start isolation"
            print
        for ptc in particles:
            if ptc is lepton:
                continue

            if debug:
                print
                print ptc
                print delta_alpha(lepton, ptc)
            if ptc.e()<self.e_thresh:
                continue
            is_on = False
            for area in self.on_areas:
                if area.is_inside(lepton, ptc):
                    is_on = True
                    break
            if debug:
                print is_on
                print
            if not is_on:
                continue
            for area in self.off_areas:
                if area.is_inside(lepton, ptc):
                    is_on = False
                    break
            if is_on:
                isolation.add_particle(ptc)
        return isolation
