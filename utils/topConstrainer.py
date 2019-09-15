from numpy import array, zeros, dot, sign, copy, linalg, delete, insert
from numpy.random import random
from math import atan, log, cos, sin, sqrt
from ROOT import TLorentzVector
from copy import copy, deepcopy

class topConstrainer(object):
    """Kinematic contrainer for ttbar semileptonic decay.

    Giving it the 4momenta of the jets, and the lepton, the btags of the jets,
    the center-of-mass energy and the theory value (like mtop and mw), it does:
    - compute the missing energy (that is interpreted as a neutrino)
    - search for the correct pairing of the jets, lepton and neutrino to reconstruct
    the W bosons and the top quarks decaying leptonic and hadronic.

    The problem has:
    8 constraint
        - 4 energy-momenta conservation
        - 4 invariant masses for W bosons and top quarks
    8 unknowns
        - 4 jet energies, assuming the direction to be well measured
        - 4 components of the missing energy (massive neutrino when you are
        dealing with an electron or a muon coming from a tau decay)
        - NB: it is assumed that the lepton is well measured
    The 8 equations can be solved linearizing the problem and iterating until
    the procedure converges.

    A few combination (according to the btag of the jets) are used.
    If the procedure converges for one of these combination, the event is
    classified as ttbar semileptonic, and both the well paired combination and
    the "fitted" energy are given back.
    """

    def __init__(self, jets, btags, lepton, com, mw=80.4, mtop=173., verbosity=-1):
        """
        Arguments
        jets = list of 4 TLorentzVector's
        btags = list of btags for the jets (dimension N)
        lepton: charged lepton (electron, muon, or tau decay products)
        com = centre-of-mass energy
        mw = W mass
        mtop = top mass
        """
        self.mw = mw
        self.mtop = mtop
        self.com = com
        self.fixMuon = True
        self.fillSecond = False
        self.verbosity = verbosity

        # Jets and b-tags
        self.jets = []
        self.btags = []
        for jet in jets:
            self.jets.append(jet)
        for btag in btags:
            self.btags.append(max(btag,1E-9))

        # Lepton
        self.lepton = lepton
        # Missing energy
        self.miss = TLorentzVector(0.,0.,0.,com)
        self.miss -= self.lepton
        self.miss -= reduce(lambda x,y:x+y, self.jets)

        # Print jets
        def printJets(string):
            print string
            for i,j in enumerate(self.jets):
                print "Jet ",i," : ",j.X(),j.Y(),j.Z(),j.E(),j.M(),self.btags[i]
            print '-------------'

        if self.verbosity >= 3: printJets("Jets in input")

        # Then merge jets (according the smallest mass) until four jets remain
        while len(self.jets) > 4:
            njets = len(self.jets)
            massMin = 1E9
            for i in range(njets):
                for j in range(i+1,njets):
                    massij = (self.jets[i]+self.jets[j]).M()
                    #massij = jets[i].Angle(jets[j].Vect())
                    if massij < massMin:
                        massMin = massij
                        imin = i
                        jmin = j
                        #print i,j,massij
            self.jets[imin]  = self.jets[imin] + self.jets[jmin]
            self.btags[imin] = max(self.btags[imin],self.btags[jmin])
            self.jets.pop(jmin)
            self.btags.pop(jmin)
        if self.verbosity >= 3: printJets("Jets after jet merging")

        # And now, order jets with increasing b tagging
        def getKey(item):
            return item[0]

        bjets = []
        for i,j in enumerate(self.jets):
            bjets.append([self.btags[i],j])
        self.jets = []
        bjets.sort(key=getKey)
        for b in bjets:
            self.jets.append(b[1])
        self.btags.sort()
        if self.verbosity >= 3: printJets("Jets after b-tag ordering")


    def setFixMuon(self,fixMuon):
        self.fixMuon = fixMuon

    def setFillSecond(self,fillSecond):
        self.fillSecond = fillSecond

    def setVerbosity(self,verbosity):
        self.verbosity = verbosity

    def pxConservation(self,fillDerivatives=True):
        # Value of the constraint
        value = 0.
        for ip in range(6):
            value += self.x[ip]*self.beta[ip]*sin(self.theta[ip])*cos(self.phi[ip])

        if not fillDerivatives:
            return value,zeros(self.nvar),zeros((self.nvar,self.nvar))

        # Derivatives with respects to all variables
        derivatives = zeros(self.nvar)
        for ip in range(6):
            derivatives[ip] = self.beta[ip]*sin(self.theta[ip])*cos(self.phi[ip])
        st5 = sin(self.theta[5])
        ct5 = cos(self.theta[5])
        sp5 = sin(self.phi[5])
        cp5 = cos(self.phi[5])
        derivatives[6] =  self.x[5] * st5 * cp5
        derivatives[7] =  self.x[5]*self.beta[5]*ct5*cp5
        derivatives[8] = -self.x[5]*self.beta[5]*st5*sp5

        # Second derivatives with respects to all variables
        second = zeros((self.nvar,self.nvar))
        second[5,6] =  st5 * cp5
        second[5,7] =  self.beta[5] * ct5 * cp5
        second[5,8] = -self.beta[5] * st5 * sp5
        second[6,7] =  self.x[5] * ct5 * cp5
        second[6,8] = -self.x[5] * st5 * sp5
        second[7,7] = -self.x[5] * self.beta[5] * st5 * cp5
        second[7,8] = -self.x[5] * self.beta[5] * ct5 * sp5
        second[8,8] = -self.x[5] * self.beta[5] * st5 * cp5
        for i in range(self.nvar):
            for j in range(i+1,self.nvar):
                second[j,i] = second[i,j]

        if self.verbosity >= 3:
            print '--------------------'
            print "pX conservation"
            print "Value : ",value
            print "Derivatives : ",derivatives
            print "Second derivatives : "
            print second

        return value, derivatives, second

    def pyConservation(self,fillDerivatives=True):
        # Value of the constraint
        value = 0.
        for ip in range(6):
            value += self.x[ip]*self.beta[ip]*sin(self.theta[ip])*sin(self.phi[ip])

        if not fillDerivatives:
            return value,zeros(self.nvar),zeros((self.nvar,self.nvar))

        # Derivatives with respects to all variables
        derivatives = zeros(self.nvar)
        for ip in range(6):
            derivatives[ip] = self.beta[ip]*sin(self.theta[ip])*sin(self.phi[ip])
        st5 = sin(self.theta[5])
        ct5 = cos(self.theta[5])
        sp5 = sin(self.phi[5])
        cp5 = cos(self.phi[5])
        derivatives[6] =  self.x[5] * st5 * sp5
        derivatives[7] =  self.x[5]*self.beta[5]*ct5*sp5
        derivatives[8] =  self.x[5]*self.beta[5]*st5*cp5

        # Second derivatives with respects to all variables
        second = zeros((self.nvar,self.nvar))
        second[5,6] =  st5 * sp5
        second[5,7] =  self.beta[5] * ct5 * sp5
        second[5,8] =  self.beta[5] * st5 * cp5
        second[6,7] =  self.x[5] * ct5 * sp5
        second[6,8] =  self.x[5] * st5 * cp5
        second[7,7] = -self.x[5] * self.beta[5] * st5 * sp5
        second[7,8] =  self.x[5] * self.beta[5] * ct5 * cp5
        second[8,8] = -self.x[5] * self.beta[5] * st5 * sp5
        for i in range(self.nvar):
            for j in range(i+1,self.nvar):
                second[j,i] = second[i,j]

        if self.verbosity >= 3:
            print '--------------------'
            print "pY conservation"
            print "Value : ",value
            print "Derivatives : ",derivatives
            print "Second derivatives : "
            print second

        return value, derivatives, second

    def pzConservation(self,fillDerivatives=True):
        # Value of the constraints
        value = 0.
        for ip in range(6):
            value += self.x[ip]*self.beta[ip]*cos(self.theta[ip])

        if not fillDerivatives:
            return value,zeros(self.nvar),zeros((self.nvar,self.nvar))

        # Derivatives with respects to all variables
        derivatives = zeros(self.nvar)
        for ip in range(6):
            derivatives[ip] = self.beta[ip]*cos(self.theta[ip])
        st5 = sin(self.theta[5])
        ct5 = cos(self.theta[5])
        derivatives[6] =  self.x[5] * ct5
        derivatives[7] = -self.x[5]*self.beta[5]*st5

        # Second derivatives with respects to all variables
        second = zeros((self.nvar,self.nvar))
        second[5,6] =  ct5
        second[5,7] = -self.beta[5] * st5
        second[6,7] = -self.x[5] * st5
        second[7,7] = -self.x[5] * self.beta[5] * ct5
        for i in range(self.nvar):
            for j in range(i+1,self.nvar):
                second[j,i] = second[i,j]

        if self.verbosity >= 3:
            print '--------------------'
            print "pZ conservation"
            print "Value : ",value
            print "Derivatives : ",derivatives
            print "Second derivatives : "
            print second

        return value, derivatives, second

    def energyConservation(self,fillDerivatives=True):
        # Value of the constraints
        value = -1.
        for ip in range(6):
            value += self.x[ip]

        if not fillDerivatives:
            return value,zeros(self.nvar),zeros((self.nvar,self.nvar))

        # Derivatives with respects to all variables
        derivatives = zeros(self.nvar)
        for ip in range(6):
            derivatives[ip] = 1.

        # Second derivatives with respects to all variables
        second = zeros((self.nvar,self.nvar))
        for i in range(self.nvar):
            for j in range(i+1,self.nvar):
                second[j,i] = second[i,j]

        if self.verbosity >= 3:
            print '--------------------'
            print "Energy conservation"
            print "Value : ",value
            print "Derivatives : ",derivatives
            print "Second derivatives : "
            print second

        return value, derivatives, second

    def leptonicWMassConstraint(self,fillDerivatives=True):
        st4 = sin(self.theta[4])
        ct4 = cos(self.theta[4])
        st5 = sin(self.theta[5])
        ct5 = cos(self.theta[5])
        cp45 = cos(self.phi[4]-self.phi[5])
        sp45 = sin(self.phi[4]-self.phi[5])
        # Value of the constraints
        wMass = self.mw/self.com
        scalar = self.beta[4] * self.beta[5] * (st4*st5*cp45 + ct4*ct5)
        value = self.x[4] * self.x[4] * (1. - self.beta[4]*self.beta[4]) \
            +   self.x[5] * self.x[5] * (1. - self.beta[5]*self.beta[5]) \
            +   2. * self.x[4] * self.x[5] * (1. - scalar) \
            -   wMass*wMass
        #check = (self.p_out[4]+self.p_out[5]).M()
        #print 'Jet-Jet mass = ',check
        #check *= check
        #check /= self.com*self.com
        #check -= wMass*wMass

        if not fillDerivatives:
            return value,zeros(self.nvar),zeros((self.nvar,self.nvar))

        # Derivatives with respects to all variables
        derivatives = zeros(self.nvar)
        derivatives[4] =  2. * self.x[4] * (1.-self.beta[4]*self.beta[4]) + 2. * self.x[5] * (1. - scalar)
        derivatives[5] =  2. * self.x[5] * (1.-self.beta[5]*self.beta[5]) + 2. * self.x[4] * (1. - scalar)
        derivatives[6] = -2. * self.x[5] * self.x[5] * self.beta[5] \
                        - 2. * self.x[4] * self.x[5] * self.beta[4] * (st4*st5*cp45 + ct4*ct5)
        derivatives[7] =  2. * self.x[4] * self.x[5] * self.beta[4] * self.beta[5] * (-st4*ct5*cp45+ct4*st5)
        derivatives[8] =  2. * self.x[4] * self.x[5] * self.beta[4] * self.beta[5] * (-st4*st5*sp45)

        # Second derivatives with respects to all variables
        second = zeros((self.nvar,self.nvar))
        second[4,4] =  2. * (1.-self.beta[4]*self.beta[4])
        second[4,5] =  2. * (1. - scalar)
        second[4,6] = -2. * self.x[5] * self.beta[4] * (st4*st5*cp45 + ct4*ct5)
        second[4,7] =  2. * self.x[5] * self.beta[4] * self.beta[5] * (-st4*ct5*cp45+ct4*st5)
        second[4,8] =  2. * self.x[5] * self.beta[4] * self.beta[5] * (-st4*st5*sp45)
        second[5,5] =  2. * (1.-self.beta[5]*self.beta[5])
        second[5,6] = -4. * self.x[5] * self.beta[5] \
                      -2. * self.x[4] * self.beta[4] * (st4*st5*cp45 + ct4*ct5)
        second[5,7] =  2. * self.x[4] * self.beta[4] * self.beta[5] * (-st4*ct5*cp45+ct4*st5)
        second[5,8] =  2. * self.x[4] * self.beta[4] * self.beta[5] * (-st4*st5*sp45)
        second[6,6] = -2. * self.x[5] * self.x[5]
        second[6,7] = -2. * self.x[4] * self.x[5] * self.beta[4] * (st4*ct5*cp45 - ct4*st5)
        second[6,8] =  2. * self.x[4] * self.x[5] * self.beta[4] * (-st4*st5*sp45)
        second[7,7] =  2. * self.x[4] * self.x[5] * self.beta[4] * self.beta[5] * (st4*st5*cp45+ct4*ct5)
        second[7,8] =  2. * self.x[4] * self.x[5] * self.beta[4] * self.beta[5] * (-st4*ct5*sp45)
        second[8,8] =  2. * self.x[4] * self.x[5] * self.beta[4] * self.beta[5] * (st4*st5*cp45)
        for i in range(self.nvar):
            for j in range(i+1,self.nvar):
                second[j,i] = second[i,j]

        if self.verbosity >= 3:
            print '--------------------'
            print 'Leptonic W mass constraint'
            print "Value : ",value
            print "Derivatives : ",derivatives
            print "Second derivatives : "
            print second

        return value, derivatives, second

    def hadronicWMassConstraint(self,fillDerivatives=True):
        st0 = sin(self.theta[0])
        ct0 = cos(self.theta[0])
        st1 = sin(self.theta[1])
        ct1 = cos(self.theta[1])
        cp01 = cos(self.phi[0]-self.phi[1])
        # Value of the constraints
        wMass = self.mw/self.com
        scalar = self.beta[0] * self.beta[1] * (st0*st1*cp01 + ct0*ct1)
        value = self.x[0] * self.x[0] * (1. - self.beta[0]*self.beta[0]) \
            +   self.x[1] * self.x[1] * (1. - self.beta[1]*self.beta[1]) \
            +   2. * self.x[0] * self.x[1] * (1. - scalar) \
            -   wMass*wMass
        #check = (self.p_out[0]+self.p_out[1]).M()
        #print 'Jet-Jet mass = ',check
        #check *= check
        #check /= self.com*self.com
        #check -= wMass*wMass

        if not fillDerivatives:
            return value,zeros(self.nvar),zeros((self.nvar,self.nvar))

        # Derivatives with respects to all variables
        derivatives = zeros(self.nvar)
        derivatives[0] = 2.*self.x[0]*(1.-self.beta[0]*self.beta[0]) + 2. * self.x[1] * (1. - scalar)
        derivatives[1] = 2.*self.x[1]*(1.-self.beta[1]*self.beta[1]) + 2. * self.x[0] * (1. - scalar)

        # Second derivatives with respects to all variables
        second = zeros((self.nvar,self.nvar))
        second[0,0] = 2.*(1.-self.beta[0]*self.beta[0])
        second[1,1] = 2.*(1.-self.beta[1]*self.beta[1])
        second[0,1] = 2.*(1. - scalar)
        for i in range(self.nvar):
            for j in range(i+1,self.nvar):
                second[j,i] = second[i,j]

        if self.verbosity >= 3:
            print '--------------------'
            print 'Hadronic W mass constraint'
            print "Value : ",value
            print "Derivatives : ",derivatives
            print "Second derivatives : "
            print second

        return value, derivatives, second

    def leptonicTopMassConstraint(self,fillDerivatives=True):
        st3 = sin(self.theta[3])
        ct3 = cos(self.theta[3])
        st4 = sin(self.theta[4])
        ct4 = cos(self.theta[4])
        st5 = sin(self.theta[5])
        ct5 = cos(self.theta[5])
        cp34 = cos(self.phi[3]-self.phi[4])
        cp35 = cos(self.phi[3]-self.phi[5])
        cp45 = cos(self.phi[4]-self.phi[5])
        sp34 = sin(self.phi[3]-self.phi[4])
        sp35 = sin(self.phi[3]-self.phi[5])
        sp45 = sin(self.phi[4]-self.phi[5])
        # Value of the constraints
        wMass = self.mw/self.com
        topMass = self.mtop/self.com
        scalar34 = self.beta[3] * self.beta[4] * (st3*st4*cp34 + ct3*ct4)
        scalar35 = self.beta[3] * self.beta[5] * (st3*st5*cp35 + ct3*ct5)
        scalar45 = self.beta[4] * self.beta[5] * (st4*st5*cp45 + ct4*ct5)
        value = self.constraints[4] + wMass*wMass \
              + self.x[3] * self.x[3] * (1. - self.beta[3]*self.beta[3]) \
              + 2. * self.x[3] * self.x[4] * (1. - scalar34) \
              + 2. * self.x[3] * self.x[5] * (1. - scalar35) \
              - topMass*topMass
        #check = (self.p_out[3]+self.p_out[4]+self.p_out[5]).M()
        #print 'Jet-Jet-Jet mass = ',check
        #check *= check
        #check /= self.com*self.com
        #check -= topMass*topMass

        if not fillDerivatives:
            return value,zeros(self.nvar),zeros((self.nvar,self.nvar))

        # Derivatives with respects to all variables
        derivatives = zeros(self.nvar)
        for i in range(self.nvar):
            derivatives[i] = self.dconstraints[4][i]
        derivatives[3] +=  2. * self.x[3] * (1.-self.beta[3]*self.beta[3]) \
                        +  2. * self.x[4] * (1. - scalar34) \
                        +  2. * self.x[5] * (1. - scalar35)
        derivatives[4] +=  2. * self.x[3] * (1. - scalar34)
        derivatives[5] +=  2. * self.x[3] * (1. - scalar35)
        derivatives[6] += -2. * self.x[3] * self.x[5] * self.beta[3] * ( st3*st5*cp35 + ct3*ct5 )
        derivatives[7] += -2. * self.x[3] * self.x[5] * self.beta[3] * self.beta[5] * ( st3*ct5*cp35 - ct3*st5 )
        derivatives[8] += -2. * self.x[3] * self.x[5] * self.beta[3] * self.beta[5] * ( st3*st5*sp35 )

        # Second derivatives with respects to all variables
        second = zeros((self.nvar,self.nvar))
        for i in range(self.nvar):
            for j in range(i,self.nvar):
                second[i,j] = self.d2constraints[4][i,j]
        second[3,3] += 2. * (1.-self.beta[3]*self.beta[3])
        second[3,4] += 2. * (1.-scalar34)
        second[3,5] += 2. * (1.-scalar35)
        second[3,6] += -2. * self.x[5] * self.beta[3] * ( st3*st5*cp35 + ct3*ct5 )
        second[3,7] += -2. * self.x[5] * self.beta[3] * self.beta[5] * ( st3*ct5*cp35 - ct3*st5 )
        second[3,8] += -2. * self.x[5] * self.beta[3] * self.beta[5] * ( st3*st5*sp35 )
        second[5,6] += -2. * self.x[3] * self.beta[3] * ( st3*st5*cp35 + ct3*ct5 )
        second[5,7] += -2. * self.x[3] * self.beta[3] * self.beta[5] * ( st3*ct5*cp35 - ct3*st5 )
        second[5,8] += -2. * self.x[3] * self.beta[3] * self.beta[5] * ( st3*st5*sp35 )
        second[6,7] += -2. * self.x[3] * self.x[5] * self.beta[3] * ( st3*ct5*cp35 - ct3*st5 )
        second[6,8] += -2. * self.x[3] * self.x[5] * self.beta[3] * ( st3*st5*sp35 )
        second[7,7] += -2. * self.x[3] * self.x[5] * self.beta[3] * self.beta[5] * ( -st3*st5*cp35 - ct3*ct5 )
        second[7,8] += -2. * self.x[3] * self.x[5] * self.beta[3] * self.beta[5] * ( st3*ct5*sp35 )
        second[8,8] += -2. * self.x[3] * self.x[5] * self.beta[3] * self.beta[5] * ( -st3*st5*cp35 )

        for i in range(self.nvar):
            for j in range(i+1,self.nvar):
                second[j,i] = second[i,j]

        if self.verbosity >= 3:
            print '--------------------'
            print 'Leptonic top mass constraint'
            print "Value : ",value
            print "Derivatives : ",derivatives
            print "Second derivatives : "
            print second

        return value, derivatives, second

    def hadronicTopMassConstraint(self,fillDerivatives=True):
        st0 = sin(self.theta[0])
        ct0 = cos(self.theta[0])
        st1 = sin(self.theta[1])
        ct1 = cos(self.theta[1])
        st2 = sin(self.theta[2])
        ct2 = cos(self.theta[2])
        cp01 = cos(self.phi[0]-self.phi[1])
        cp02 = cos(self.phi[0]-self.phi[2])
        cp12 = cos(self.phi[1]-self.phi[2])
        # Value of the constraints
        wMass = self.mw/self.com
        topMass = self.mtop/self.com
        scalar01 = self.beta[0] * self.beta[1] * (st0*st1*cp01 + ct0*ct1)
        scalar02 = self.beta[0] * self.beta[2] * (st0*st2*cp02 + ct0*ct2)
        scalar12 = self.beta[1] * self.beta[2] * (st1*st2*cp12 + ct1*ct2)
        value = self.constraints[5] + wMass*wMass \
              + self.x[2] * self.x[2] * (1. - self.beta[2]*self.beta[2]) \
              + 2. * self.x[0] * self.x[2] * (1. - scalar02) \
              + 2. * self.x[1] * self.x[2] * (1. - scalar12) \
              - topMass*topMass
        #check = (self.p_out[0]+self.p_out[1]+self.p_out[2]).M()
        #print 'Jet-Jet-Jet mass = ',check
        #check *= check
        #check /= self.com*self.com
        #check -= topMass*topMass

        if not fillDerivatives:
            return value,zeros(self.nvar),zeros((self.nvar,self.nvar))

        # Derivatives with respects to all variables
        derivatives = zeros(self.nvar)
        for i in range(self.nvar):
            derivatives[i] = self.dconstraints[5][i]
        derivatives[0] += 2. * self.x[2] * (1. - scalar02)
        derivatives[1] += 2. * self.x[2] * (1. - scalar12)
        derivatives[2] += 2. * self.x[2] * (1.-self.beta[2]*self.beta[2]) \
                        + 2. * self.x[0] * (1. - scalar02) \
                        + 2. * self.x[1] * (1. - scalar12)

        # Second derivatives with respects to all variables
        second = zeros((self.nvar,self.nvar))
        for i in range(self.nvar):
            for j in range(i,self.nvar):
                second[i,j] = self.d2constraints[5][i,j]
        second[0,2] += 2. * (1.-scalar02)
        second[1,2] += 2. * (1.-scalar12)
        second[2,2] += 2. * (1.-self.beta[2]*self.beta[2])
        for i in range(self.nvar):
            for j in range(i+1,self.nvar):
                second[j,i] = second[i,j]

        if self.verbosity >= 3:
            print '--------------------'
            print 'Hadronic top mass constraint'
            print "Value : ",value
            print "Derivatives : ",derivatives
            print "Second derivatives : "
            print second

        return value, derivatives, second

    def neutrinoMassConstraint(self,fillDerivatives=True):
        # Value of the constraints
        value = self.beta[5]-1.
        #check = self.p_out[5].P()/self.p_out[5].E()-1.

        if not fillDerivatives:
            return value,zeros(self.nvar),zeros((self.nvar,self.nvar))

        # Derivatives with respects to all variables
        derivatives = zeros(self.nvar)
        derivatives[6] = 1.

        # Second derivatives with respects to all variables
        second = zeros((self.nvar,self.nvar))
        for i in range(self.nvar):
            for j in range(i+1,self.nvar):
                second[j,i] = second[i,j]

        if self.verbosity >= 3:
            print '--------------------'
            print "Neutrino mass constraint"
            print "Value : ",value
            print "Derivatives : ",derivatives
            print "Second derivatives : "
            print second

        return value, derivatives, second

    def muonEnergyConstraint(self,fillDerivatives=True):
        # Value of the constraints
        value = 100.*(self.x[5]-self.p_ini[5].E()/self.com)
        #check = self.p_out[5].P()/self.p_out[5].E()-1.

        if not fillDerivatives:
            return value,zeros(self.nvar),zeros((self.nvar,self.nvar))

        # Derivatives with respects to all variables
        derivatives = zeros(self.nvar)
        derivatives[5] = 100.

        # Second derivatives with respects to all variables
        second = zeros((self.nvar,self.nvar))
        for i in range(self.nvar):
            for j in range(i+1,self.nvar):
                second[j,i] = second[i,j]

        if self.verbosity >= 3:
            print '--------------------'
            print "Muon energy constraint"
            print "Value : ",value
            print "Derivatives : ",derivatives
            print "Second derivatives : "
            print second

        return value, derivatives, second

    def fillInputVariables(self, combination, onlyParticles = False):
        # Initialize input and output TLorentzVectors
        self.p_ini = []
        self.btags_ini = []
        for i,jet in enumerate(combination[1]):
            self.p_ini.append(self.jets[jet])
            self.btags_ini.append(self.btags[combination[1][i]])
        self.p_ini.append(self.lepton)
        self.p_ini.append(self.miss)
        if self.verbosity >= 2:
            print "Input particles"
            for i,j in enumerate(self.p_ini):
                if i < 4:
                    print "Particle ",i," : ",j.X(),j.Y(),j.Z(),j.E(),j.M(),self.btags_ini[i]
                else:
                    print "Particle ",i," : ",j.X(),j.Y(),j.Z(),j.E(),j.M()
            print '-------------'

        if onlyParticles: return

        # Initialize input variables
        self.x = []      # Reduced energies
        self.beta = []   # Velocities
        self.theta = []  # Polar angle
        self.phi = []    # Azimutal angle
        #
        for part in self.p_ini:
            self.x.append(part.E()/self.com)
            self.beta.append(part.P()/part.E())
            self.theta.append(part.Theta())
            self.phi.append(part.Phi())

        # Initialize unknown variables
        self.nvar = 9
        self.ncons = 9
        self.alpha = zeros(self.nvar)
        # First six variables are the jet energies, the lepton energy and the missing energy
        for i in range(6):
            self.alpha[i] = self.x[i]
        # Then the missing velocity (module, theta and phi)
        self.alpha[6] = self.beta[5]
        self.alpha[7] = self.theta[5]
        self.alpha[8] = self.phi[5]

        if self.verbosity >= 3:
            print 'X     : ',self.x
            print 'Beta  : ',self.beta
            print 'Theta : ',self.theta
            print 'Phi   : ',self.phi

    def fillOutputParticles(self, combination):
        # Initialize input and output TLorentzVectors
        self.p_out = [TLorentzVector() for part in range(6) ]
        self.btags_out = [0. for part in range(4)]

        for i,jet in enumerate(combination[1]):
            #p_ini = self.jets[jet]
            #x_ini = p_ini.E()/self.com
            #x_out = self.alpha[i]
            #scale = x_out / x_ini
            self.p_out[i] = self.jets[jet] * (self.alpha[i] / self.jets[jet].E() * self.com)
            self.btags_out[i] = self.btags[combination[1][i]]

        #x_ini = self.lepton.E()/self.com
        #x_out = self.alpha[4]
        #scale = x_out / x_ini
        self.p_out[4] = self.lepton * (self.alpha[4] / self.lepton.E() * self.com)

        self.p_out[5].SetXYZT(self.alpha[5]*self.alpha[6]*self.com*sin(self.alpha[7])*cos(self.alpha[8]), \
                              self.alpha[5]*self.alpha[6]*self.com*sin(self.alpha[7])*sin(self.alpha[8]), \
                              self.alpha[5]*self.alpha[6]*self.com*cos(self.alpha[7]), \
                              self.alpha[5]*self.com)

        if self.verbosity >= 2:
            print "Output particles"
            for i,j in enumerate(self.p_out):
                k = self.p_ini[i]
                if i < 4:
                    #print "Particle ",i," : ",k.X(),k.Y(),k.Z(),k.E(),k.M(),self.btags[combination[1][i]]
                    print "Particle ",i," : ",j.X(),j.Y(),j.Z(),j.E(),j.M(),self.btags_out[i]
                else:
                    #print "Particle ",i," : ",k.X(),k.Y(),k.Z(),k.E(),k.M()
                    print "Particle ",i," : ",j.X(),j.Y(),j.Z(),j.E(),j.M()
            ptot = (self.p_out[0]+self.p_out[1]+self.p_out[2]+self.p_out[3]+self.p_out[4]+self.p_out[5])
            print 'Hadronic  W  mass = ',(self.p_out[0]+self.p_out[1]).M()
            print 'Leptonic  W  mass = ',(self.p_out[4]+self.p_out[5]).M()
            print 'Hadronic top mass = ',(self.p_out[0]+self.p_out[1]+self.p_out[2]).M()
            print 'Leptonic top mass = ',(self.p_out[3]+self.p_out[4]+self.p_out[5]).M()
            print 'Total Energy/Mom  = ',ptot.X(),ptot.Y(),ptot.Z(),ptot.E()
            print '-------------'


    def fillUnknowns(self):
        for i in range(6):
            self.x[i] = self.alpha[i]
        self.beta[5] = self.alpha[6]
        self.theta[5] = self.alpha[7]
        self.phi[5] = self.alpha[8]

    def fillConstraints(self,fillDerivatives=True):
        self.constraints = []
        self.dconstraints = []
        self.d2constraints = []
        # pX conservation
        value, derivatives, doubleDerivatives = self.pxConservation(fillDerivatives)
        self.constraints.append(value)
        if fillDerivatives:
            self.dconstraints.append(derivatives)
            self.d2constraints.append(doubleDerivatives)

        # pY conservation
        value, derivatives, doubleDerivatives = self.pyConservation(fillDerivatives)
        self.constraints.append(value)
        if fillDerivatives:
            self.dconstraints.append(derivatives)
            self.d2constraints.append(doubleDerivatives)

        # pZ conservation
        value, derivatives, doubleDerivatives = self.pzConservation(fillDerivatives)
        self.constraints.append(value)
        if fillDerivatives:
            self.dconstraints.append(derivatives)
            self.d2constraints.append(doubleDerivatives)

        # energy conservation
        value, derivatives, doubleDerivatives = self.energyConservation(fillDerivatives)
        self.constraints.append(value)
        if fillDerivatives:
            self.dconstraints.append(derivatives)
            self.d2constraints.append(doubleDerivatives)

        # leptonic W mass constraint
        value, derivatives, doubleDerivatives = self.leptonicWMassConstraint(fillDerivatives)
        self.constraints.append(value)
        if fillDerivatives:
            self.dconstraints.append(derivatives)
            self.d2constraints.append(doubleDerivatives)

        # hadronic W mass constraint
        value, derivatives, doubleDerivatives = self.hadronicWMassConstraint(fillDerivatives)
        self.constraints.append(value)
        if fillDerivatives:
            self.dconstraints.append(derivatives)
            self.d2constraints.append(doubleDerivatives)

        # leptonic top mass constraint
        value, derivatives, doubleDerivatives = self.leptonicTopMassConstraint(fillDerivatives)
        self.constraints.append(value)
        if fillDerivatives:
            self.dconstraints.append(derivatives)
            self.d2constraints.append(doubleDerivatives)

        # hadronic top mass constraint
        value, derivatives, doubleDerivatives = self.hadronicTopMassConstraint(fillDerivatives)
        self.constraints.append(value)
        if fillDerivatives:
            self.dconstraints.append(derivatives)
            self.d2constraints.append(doubleDerivatives)

        # neutrino mass constraint
        value, derivatives, doubleDerivatives = self.neutrinoMassConstraint(fillDerivatives)
        self.constraints.append(value)
        if fillDerivatives:
            self.dconstraints.append(derivatives)
            self.d2constraints.append(doubleDerivatives)

        # muon energy constraint
        #value, derivatives, doubleDerivatives = self.muonEnergyConstraint(fillDerivatives)
        #self.constraints.append(value)
        #if fillDerivatives:
            #self.dconstraints.append(derivatives)
            #self.d2constraints.append(doubleDerivatives)



    def fillChiSquaredConstraints(self,fillDerivatives=True):
        value = 0.
        nvar = self.nvar
        if self.fixMuon: nvar -= 1
        derivatives = zeros(nvar)
        second = zeros((nvar,nvar))
        for k,constraint in enumerate(self.constraints):
            if self.verbosity >=3: print "Constraint ",k," = ",constraint
            if self.fixMuon and not self.fillSecond and k == 8: continue
            value += constraint * constraint
            if fillDerivatives:
                if self.fillSecond:
                    for i in range(nvar):
                        ii = i
                        if self.fixMuon and i >= 4: ii = i+1
                        derivatives[i] += 2. * constraint * self.dconstraints[k][ii]
                        for j in range(nvar):
                            jj = j
                            if self.fixMuon and j >= 4: jj = j+1
                            second[i,j] += 2. * self.dconstraints[k][ii] * self.dconstraints[k][jj] \
                                         + 2. * constraint * self.d2constraints[k][ii,jj]
                else:
                    derivatives[k] += constraint
                    for i in range(nvar):
                        ii = i
                        if self.fixMuon and i >= 4: ii = i+1
                        second[k,i] += self.dconstraints[k][ii]

        if self.verbosity >=2:
            print '--------------------'
            print "Chi squared"
            print "Value : ",value
            if fillDerivatives:
                print "Derivatives : ",derivatives
                print "Second derivatives : "
                print second

        return value, derivatives, second

    def fillChiSquaredMeasured(self):
        chi2Jets = 0.
        chi2Lepton = 0.
        for i,jet in enumerate(self.p_out):
            if i<4:
                delta = jet.E()-self.p_ini[i].E()
                chi2Jets += delta*delta / (0.10 * self.p_ini[i].E())
            if i==4:
                delta = 1./jet.Perp() - 1./self.p_ini[i].Perp()
                chi2Lepton += delta*delta / 1E-8
                #chi2Jets += chi2Lepton
        return chi2Jets, chi2Lepton

    def fillCheck(self):
        self.fillUnknowns()
        self.fillConstraints()
        epsilon = 1E-8
        der = zeros(self.nvar)
        der2 = zeros((self.nvar,self.nvar))
        chi2, dChi2, d2Chi2 = self.fillChiSquaredConstraints()
        for i in range(self.nvar):
            #print i,self.alpha[i],chi2
            self.alpha[i] -= epsilon
            self.fillUnknowns()
            self.fillConstraints()
            chi2m, dChi2m, d2Chi2m = self.fillChiSquaredConstraints()
            #print i,self.alpha[i],chi2m
            self.alpha[i] += 2.*epsilon
            self.fillUnknowns()
            self.fillConstraints()
            chi2p, dChi2p, d2Chi2p = self.fillChiSquaredConstraints()
            der[i] = (chi2p-chi2m)/(2.*epsilon)
            for j in range(self.nvar):
                der2[i,j] += (dChi2p[j]-dChi2m[j])/(2.*epsilon)
            #print i,self.alpha[i],chi2p
            self.alpha[i] -= epsilon
            self.fillUnknowns()
            self.fillConstraints()

        print '+++++ CHECK start ... +++++'
        nprob = 0
        for i in range(self.nvar):
            if abs(dChi2[i] - der[i]) > 1E-4:
                print i,dChi2[i],der[i]
                nprob += 1
            for j in range(self.nvar):
                if abs(d2Chi2[i,j] - der2[i,j]) > 1E-4:
                    print i,d2Chi2[i,j],der2[i,j]
                    nprob += 1

        if nprob == 0 : print '+++++ CHECK OK ! +++++'

    def rescale(self,chi2Cut=1E-5):
        combinations = []
        # These two combinations are the most likely, with the two b jets tagged with the highest b-tag
        combinations.append([1.,[0,1,2,3]])
        combinations.append([1.,[0,1,3,2]])
        # Next to likely
        combinations.append([self.btags[2]/self.btags[1],[0,2,1,3]])
        combinations.append([self.btags[2]/self.btags[1],[0,2,3,1]])
        # Quite un-likely
        #combinations.append([4.,[0,3,1,2]])
        #combinations.append([4.,[0,3,2,1]])
        # More un-likely
        combinations.append([self.btags[2]/self.btags[0],[1,2,0,3]])
        combinations.append([self.btags[2]/self.btags[0],[1,2,3,0]])
        # Even more un-likely
        #combinations.append([16.,[1,3,0,2]])
        #combinations.append([16.,[1,3,2,0]])
        # Are you kidding me ?
        #combinations.append([32.,[2,3,0,1]])
        #combinations.append([32.,[2,3,1,0]])

        # Loop over all combinations
        chi2Min1 = 1E9
        chi2Min2 = 1E9
        penalty1 = 1.0
        penalty2 = 1.0
        success = False
        success1 = False
        success2 = False
        theSolution1 = combinations[0]
        theSolution2 = combinations[0]
        self.fillInputVariables(theSolution1)
        theAlphas = zeros(self.nvar)
        theAlphas1 = zeros(self.nvar)
        theAlphas2 = zeros(self.nvar)
        for combination in combinations:
            self.fillInputVariables(combination)
            self.fillUnknowns()
            self.fillConstraints(False)
            chi2Before,dChi2,d2Chi2 = self.fillChiSquaredConstraints(False)
            #combination[0] = chi2Before
            wrong = self.fit()
            if wrong: continue
            chi2After,dChi2,d2Chi2 = self.fillChiSquaredConstraints(False)
            if self.verbosity >=0:
                print 'Combination ',combination,', chi2 before = ',chi2Before,', Chi2 after = ',chi2After
            self.fillOutputParticles(combination)
            ptot = (self.p_out[0]+self.p_out[1]+self.p_out[2]+self.p_out[3]+self.p_out[4]+self.p_out[5])
            #if not noChi2Cut and chi2After > 5E-4: continue
            success = True
            chi2Jets,chi2Lepton = self.fillChiSquaredMeasured()
            # Introduce a penalty for the probability of the combination
            penalty = combination[0]
            chi2Jets *= penalty
            chi2Lepton *= penalty
            #print 'chi2 jets = ',chi2Jets,', chi2 lepton = ',chi2Lepton
            #print '-------------'
            if chi2Jets < chi2Min1:
                if chi2After < chi2Cut:
                    if self.verbosity >=2:
                        print 'Combination w/ chi2 cut ',combination,', chi2 jets = ',chi2Jets,',chi2 lepton = ',chi2Lepton
                    chi2Min1 = chi2Jets
                    penatly1 = penalty
                    theSolution1 = combination
                    success1 = True
                    theAlphas1 = self.alpha
            if chi2Jets < chi2Min2:
                if self.verbosity >=2:
                    print 'Combination w/o chi2 cut ',combination,', chi2 jets = ',chi2Jets,',chi2 lepton = ',chi2Lepton
                chi2Min2 = chi2Jets
                penatly2 = penalty
                theSolution2 = combination
                success2 = True
                theAlphas2 = self.alpha

        if not success1 and not success2: return False, 1E9

        theSolution = theSolution1
        theAlphas = theAlphas1
        if not success1 :
            theSolution = theSolution2
            theAlphas = theAlphas2

        if self.verbosity >=0:
            print 'Success1/2 : ',success1,success2
            print 'The solution is found with the jet combination : ',theSolution[1]
        self.fillInputVariables(theSolution,True)
        if self.verbosity >=1:
            print "Input particles"
            for i,j in enumerate(self.p_ini):
                if i < 4:
                    print "Particle ",i," : ",j.X(),j.Y(),j.Z(),j.E(),j.M(),self.btags_ini[i]
                else:
                    print "Particle ",i," : ",j.X(),j.Y(),j.Z(),j.E(),j.M()
            print '-------------'
        self.alpha = theAlphas
        self.fillOutputParticles(theSolution)
        if self.verbosity >=1:
            print "Output particles"
            for i,j in enumerate(self.p_out):
                k = self.p_ini[i]
                if i < 4:
                    print "Particle ",i," : ",j.X(),j.Y(),j.Z(),j.E(),j.M(),self.btags_out[i]
                else:
                    print "Particle ",i," : ",j.X(),j.Y(),j.Z(),j.E(),j.M()
            ptot = (self.p_out[0]+self.p_out[1]+self.p_out[2]+self.p_out[3]+self.p_out[4]+self.p_out[5])
            print 'Hadronic  W  mass = ',(self.p_out[0]+self.p_out[1]).M()
            print 'Leptonic  W  mass = ',(self.p_out[4]+self.p_out[5]).M()
            print 'Hadronic top mass = ',(self.p_out[0]+self.p_out[1]+self.p_out[2]).M()
            print 'Leptonic top mass = ',(self.p_out[3]+self.p_out[4]+self.p_out[5]).M()
            print 'Total Energy/Mom  = ',ptot.X(),ptot.Y(),ptot.Z(),ptot.E()
            print '-------------'
        return success1,chi2Min1 / penalty1

    def fixMiss(self):
        self.fillUnknowns()
        miss = TLorentzVector(0.,0.,0.,1.)
        for i in range(5):
            miss -= TLorentzVector(self.x[i]*self.beta[i]*sin(self.theta[i])*cos(self.phi[i]), \
                                   self.x[i]*self.beta[i]*sin(self.theta[i])*sin(self.phi[i]), \
                                   self.x[i]*self.beta[i]*cos(self.theta[i]), \
                                   self.x[i])
        self.alpha[5] = miss.E()
        self.alpha[6] = miss.P()/miss.E()
        self.alpha[7] = miss.Theta()
        self.alpha[8] = miss.Phi()
        self.fillUnknowns()
        self.fillConstraints(False)

    def fit(self):
        iter = 0
        wrong = False
        chi2prev = 1E9
        self.fillUnknowns()
        self.fillConstraints()
        chi2, dChi2, d2Chi2 = self.fillChiSquaredConstraints(True)
        while abs(chi2-chi2prev) > 1E-10 and iter < 20:
            chi2prev = chi2
            #if self.fixMuon:
                #if self.fillSecond:
                    # In case one wants to fix the muon energy.
                    #d2Chi2 = delete(d2Chi2, [4], axis=0)
                    #d2Chi2 = delete(d2Chi2, [4], axis=1)
                    #dChi2 = delete(dChi2,4)
            dalpha = linalg.solve(d2Chi2,dChi2)
            if self.fixMuon: dalpha = insert(dalpha,4,0.)
            big = False
            wrong = False
            for i,d in enumerate(dalpha):
                if i<4:
                    if abs(d) > 0.5:
                        dalpha[i] = 0.6*sign(d)
                        big = True
                    if self.alpha[i] > 0.5 or self.alpha[i] < 0.01:
                        #print 'Warning ! alpha[',i,'] = ',self.alpha[i]
                        wrong = True
            if wrong: return wrong
            if big:
                dalpha[5] = 0.
                dalpha[6] = 0.
                dalpha[7] = 0.
                dalpha[8] = 0.

            if self.verbosity >= 2:
                print '--------------------'
                print 'Iteration ',iter
                print "Chi2 : ",chi2
                print "Derivatives : ",dChi2
                print "Constraints : ",self.constraints
                print 'alpha  : ',self.alpha
                print 'dalpha : ',dalpha
            self.alpha -= dalpha
            self.fillUnknowns()
            if big: self.fixMiss()
            self.fillConstraints(False)
            chi2, dChi2, d2Chi2 = self.fillChiSquaredConstraints(False)
            step = 0
            while chi2 > min(chi2prev+1E-4,chi2prev*1.10) and step < 5:
                step += 1
                if self.verbosity >= 2: print 'Warning : Chi2 has increased from ',chi2prev,' to ',chi2,' !!!'
                self.alpha += dalpha
                for i in range(self.nvar):
                    if i < 4:
                        dalpha[i] *= 0.5
                    elif i > 4: dalpha[i] = 0.

                #self.alpha += dalpha
                #dalpha = map(lambda x:-x*0.7, dalpha)
                self.alpha -= dalpha
                self.fillUnknowns()
                self.fixMiss()
                self.fillConstraints(False)
                chi2, dChi2, d2Chi2 = self.fillChiSquaredConstraints(False)
            self.fillConstraints()
            chi2, dChi2, d2Chi2 = self.fillChiSquaredConstraints()

            iter += 1

        return wrong
