from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from heppy.analyzers.ntuple_mod import *

from ROOT import TFile

class TreeTTSemilep(Analyzer):

    def beginLoop(self, setup):
        super(TreeTTSemilep, self).beginLoop(setup)
        self.rootfile = TFile('/'.join([self.dirName, 'tree.root']), 'recreate')
        self.tree = Tree('events', '')

        var(self.tree, 'ev_number', int)

        bookMyParticle(self.tree, 'mc_lepton1')
        bookMyParticle(self.tree, 'mc_lepton2')
        bookMyParticle(self.tree, 'mc_neutrino1')
        bookMyParticle(self.tree, 'mc_neutrino2')
        bookMyParticle(self.tree, 'mc_w_lep1')
        bookMyParticle(self.tree, 'mc_w_lep2')
        
        # Add the top quark and W boson to mc_particles save
        bookMyParticle(self.tree, 'mc_tquark1')
        bookMyParticle(self.tree, 'mc_tquark2')
        bookMyParticle(self.tree, 'mc_w1')
        bookMyParticle(self.tree, 'mc_w2')
        bookMyParticle(self.tree, 'mc_w3')
        bookMyParticle(self.tree, 'mc_w4')

        bookMyLepton(self.tree, 'lep1')
        bookMyLepton(self.tree, 'lep2')

        bookMyJet(self.tree, 'jet1')
        bookMyJet(self.tree, 'jet2')
        bookMyJet(self.tree, 'jet3')
        bookMyJet(self.tree, 'jet4')

        bookMCbQuark(self.tree, 'mc_bquark1')
        bookMCbQuark(self.tree, 'mc_bquark2')
        
        bookMCbQuark(self.tree, 'mc_quarkjet1')
        bookMCbQuark(self.tree, 'mc_quarkjet2')

        bookJetsInvariantMasses(self.tree)
        bookJetsShape(self.tree)
        bookChargedTracks(self.tree)
        bookMissingEnergy(self.tree)

        bookTopConstrainer(self.tree)


    def process(self, event):
        self.tree.reset()

        fill(self.tree, 'ev_number', event.iEv)

        #if hasattr(event, 'mc_lepton'):
        mc_lepton = getattr(event, self.cfg_ana.mc_lepton, [])
        for ilep,lep in enumerate(mc_lepton):
            if ilep == 2:
                break
            fillMyParticle(self.tree, 'mc_lepton{ilep}'.format(ilep=ilep+1), lep)
        #if hasattr(event, 'mc_neutrino'):
        mc_neutrino = getattr(event, self.cfg_ana.mc_neutrino, [])
        for ineut,neut in enumerate(mc_neutrino):
            if ineut == 2:
                break
            fillMyParticle(self.tree, 'mc_neutrino{ineut}'.format(ineut=ineut+1), neut)
        #if hasattr(event, 'mc_w_lep'):
        mc_w_lep = getattr(event, 'mc_w_lep', [])
        for iw,w in enumerate(mc_w_lep):
            if iw == 2:
                break
            fillMyParticle(self.tree, 'mc_w_lep{iw}'.format(iw=iw+1), w)

        leptons = getattr(event, self.cfg_ana.leptons, [])
        #if leptons != []:
        #    leptons = leptons[0]
        for ilep,lep in enumerate(leptons):
            if ilep == 2:
                break
            fillMyLepton(self.tree, 'lep{ilep}'.format(ilep=ilep+1),lep)

        jets = getattr(event, self.cfg_ana.jets)
        for ijet, jet in enumerate(jets):
            if ijet == 4:
                break
            fillMyJet(self.tree, 'jet{ijet}'.format(ijet=ijet+1), jet)

        if hasattr(event, self.cfg_ana.mc_b_quarks):
            mc_b_quarks = getattr(event, self.cfg_ana.mc_b_quarks)
            for iquark, quark in enumerate(mc_b_quarks):
                # Stop at 2 bquarks
                if iquark == 2:
                    break
                fillMCbQuark(self.tree, 'mc_bquark{iquark}'.format(iquark=iquark+1), quark)
        
        # Add code to fill also quarks associated to jets
        #if hasattr(event, self.cfg_ana.mc_quark_jets):
        mc_quark_jets = getattr(event, self.cfg_ana.mc_quark_jets,[])
        for iquark, quark in enumerate(mc_quark_jets):
            # Stop at 2 quarks
            if iquark == 2:
                break
            fillMCbQuark(self.tree, 'mc_quarkjet{iquark}'.format(iquark=iquark+1), quark)
        
        # Add code to fill top quarks and W bosons
        #if hasattr(event, self.cfg_ana.mc_t_quarks):
        mc_t_quarks = getattr(event, self.cfg_ana.mc_t_quarks, [])
        for iquark, quark in enumerate(mc_t_quarks):
            # Stop at 2 tquarks
            if iquark == 2:
                break
            fillMyParticle(self.tree, 'mc_tquark{iquark}'.format(iquark=iquark+1), quark)
                
        #if hasattr(event, self.cfg_ana.mc_w_bosons):
        mc_w_bosons = getattr(event, self.cfg_ana.mc_w_bosons, [])
        for iboson, boson in enumerate(mc_w_bosons):
            # Stop at 4 W bosons:
            # The 2 W bosons can possibly decay to W > W+l again
            if iboson == 4:
                break
            fillMyParticle(self.tree, 'mc_w{iboson}'.format(iboson=iboson+1), boson)

        fillJetsInvariantMasses(self.tree, event)
        fillMissingEnergy(self.tree, event)
        fillJetsShape(self.tree, event)
        fillChargedTracks(self.tree, event)
        fillTopConstrainer(self.tree, event)

        self.tree.tree.Fill()

    def write(self, setup):
        self.rootfile.Write()
        self.rootfile.Close()
