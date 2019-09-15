from ROOT import TLorentzVector, TVector3

def pt_wrt_axis(axis, particles):
    """Transverse momentum of a set of particles wrt to a given axis.

    axis must be a TVector3 object,
    particles must be a list of particle objects
    """
    total_momentum = TLorentzVector(0, 0, 0, 0)

    for particle in particles:
        total_momentum += particle.p4()

    return total_momentum.Perp(axis)
