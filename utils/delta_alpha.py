def delta_alpha(ptc1, ptc2):
    """Angular distance between two particles."""
    return ptc1.p4().Angle(ptc2.p3())
