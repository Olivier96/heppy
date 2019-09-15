#!/bin/env python
"""Book and fill functions specialized for e+e- collision and top mass analysis."""

def var(tree, varName, type=float):
    tree.var(varName, type)

def fill(tree, varName, value):
    tree.fill( varName, value )

# simple p4
def bookMyP4(tree, pName):
    var(tree, '{pName}_e'.format(pName=pName))
    var(tree, '{pName}_px'.format(pName=pName))
    var(tree, '{pName}_py'.format(pName=pName))
    var(tree, '{pName}_pz'.format(pName=pName))
    var(tree, '{pName}_theta'.format(pName=pName))
    var(tree, '{pName}_phi'.format(pName=pName))
    var(tree, '{pName}_m'.format(pName=pName))

def fillMyP4(tree, pName, p4):
    fill(tree, '{pName}_e'.format(pName=pName), p4.e() )
    fill(tree, '{pName}_px'.format(pName=pName), p4.p4().Px() )
    fill(tree, '{pName}_py'.format(pName=pName), p4.p4().Py() )
    fill(tree, '{pName}_pz'.format(pName=pName), p4.p4().Pz() )
    fill(tree, '{pName}_theta'.format(pName=pName), p4.p4().Theta() )
    fill(tree, '{pName}_phi'.format(pName=pName), p4.phi() )
    fill(tree, '{pName}_m'.format(pName=pName), p4.m() )

# simple particle

def bookMyParticle( tree, pName ):
    var(tree, '{pName}_pdgid'.format(pName=pName))
    bookMyP4(tree, pName)

def fillMyParticle( tree, pName, particle ):
    fill(tree, '{pName}_pdgid'.format(pName=pName), particle.pdgid() )
    fillMyP4(tree, pName, particle )

# jet

def bookComponent( tree, pName ):
    var(tree, '{pName}_e'.format(pName=pName))
    var(tree, '{pName}_pt'.format(pName=pName))
    var(tree, '{pName}_num'.format(pName=pName))

def fillComponent(tree, pName, component):
    fill(tree, '{pName}_e'.format(pName=pName), component.e() )
    fill(tree, '{pName}_pt'.format(pName=pName), component.pt() )
    fill(tree, '{pName}_num'.format(pName=pName), component.num() )


pdgids = [211, 22, 130, 11, 13]

def bookMyJet( tree, pName ):
    bookMyP4(tree, pName )
    for pdgid in pdgids:
        bookComponent(tree, '{pName}_{pdgid:d}'.format(pName=pName, pdgid=pdgid))

    var(tree, '{pName}_btag'.format(pName = pName))
    var(tree, '{pName}_logbtag'.format(pName = pName))
    var(tree, '{pName}_log10btag'.format(pName = pName))
    var(tree, '{pName}_mc_b_quark_index'.format(pName = pName))

def fillMyJet( tree, pName, jet ):
    fillMyP4(tree, pName, jet )

    for pdgid in pdgids:
        component = jet.constituents.get(pdgid, None)
        if component is not None:
            fillComponent(tree, '{pName}_{pdgid:d}'.format(pName=pName, pdgid=pdgid), component )

    if hasattr(jet, 'btag'):
        fill(tree, '{pName}_btag'.format(pName = pName), jet.btag)
        fill(tree, '{pName}_logbtag'.format(pName = pName), jet.logbtag)
        fill(tree, '{pName}_log10btag'.format(pName = pName), jet.log10btag)

    if hasattr(jet, 'mc_b_quark_index'):
        fill(tree, '{pName}_mc_b_quark_index'.format(pName = pName), jet.mc_b_quark_index)


# isolation
iso_pdgids = [211, 22, 130]

def bookMyIso(tree, pName):
    var(tree, '{pName}_e'.format(pName=pName))
    var(tree, '{pName}_num'.format(pName=pName))
    var(tree, '{pName}_pt_wrt_lepton'.format(pName=pName))

def fillMyIso(tree, pName, iso):
    fill(tree, '{pName}_e'.format(pName=pName), iso.sume )
    fill(tree, '{pName}_num'.format(pName=pName), iso.num )
    fill(tree, '{pName}_pt_wrt_lepton'.format(pName=pName), iso.pt_wrt_lepton )

# LEPTON
def bookMyLepton( tree, pName, pflow=True ):
    bookMyParticle(tree, pName )
    if pflow:
        for pdgid in iso_pdgids:
            bookMyIso(tree, '{pName}_iso{pdgid:d}'.format(pName=pName, pdgid=pdgid))
    bookMyIso(tree, '{pName}_iso'.format(pName=pName))
    var(tree, '{pName}_match_with_mc'.format(pName=pName))


def fillMyLepton( tree, pName, lepton ):
    fillMyParticle(tree, pName, lepton )
    for pdgid in iso_pdgids:
        isoname='iso_{pdgid:d}'.format(pdgid=pdgid)
        if hasattr(lepton, isoname):
            iso = getattr(lepton, isoname)
            fillMyIso(tree, '{pName}_iso{pdgid:d}'.format(pName=pName, pdgid=pdgid), iso)
    fillMyIso(tree, '{pName}_iso'.format(pName=pName), lepton.iso)
    if hasattr(lepton, 'match_with_mc'):
        fill(tree, '{pName}_match_with_mc'.format(pName=pName), lepton.match_with_mc)



# MC B QUARK
def bookMCbQuark(tree, pName):
    bookMyParticle(tree, pName)
    var(tree, '{pName}_index_nearest_jet'.format(pName=pName), int)
    var(tree, '{pName}_delta_alpha_wrt_nearest_jet'.format(pName=pName) )
    var(tree, '{pName}_delta_e_wrt_nearest_jet'.format(pName=pName))
    bookMyJet(tree, '{pName}_nearest_jet'.format(pName=pName) )

def fillMCbQuark(tree, pName, quark):
    fillMyParticle(tree, pName, quark)
    fill(tree, '{pName}_index_nearest_jet'.format(pName=pName), quark.index_nearest_jet )
    fill(tree, '{pName}_delta_alpha_wrt_nearest_jet'.format(pName=pName), quark.delta_alpha_wrt_nearest_jet )
    fill(tree, '{pName}_delta_e_wrt_nearest_jet'.format(pName=pName), quark.e() - quark.nearest_jet.e())
    fillMyJet(tree, '{pName}_nearest_jet'.format(pName=pName), quark.nearest_jet )



# JETS VARIABLE
def bookJetsInvariantMasses(tree):
    var(tree, 'max_jet_e')
    var(tree, 'min_jet_e')

    var(tree, 'four_jets_mass')
    var(tree, 'min_jets_mass')
    var(tree, 'second_min_jets_mass')
    var(tree, 'max_jets_mass')
    var(tree, 'min_jets_angle')
    var(tree, 'second_min_jets_angle')
    var(tree, 'max_jets_angle')

    var(tree, 'min_jets_lepton_angle')
    var(tree, 'second_min_jets_lepton_angle')
    var(tree, 'max_jets_lepton_angle')
    var(tree, 'lep_pt_wrt_closest_jet')
    var(tree, 'lep_pt_wrt_second_closest_jet')
    var(tree, 'lep_pt_wrt_farthest_jet')

    var(tree, 'total_rec_mass')
    var(tree, 'jets_sumpt')
    var(tree, 'jets_vecp_over_sump')

def fillJetsInvariantMasses(tree, event):
    if hasattr(event, 'four_jets_mass'):
        fill(tree, 'max_jet_e', event.max_jet_e)
        fill(tree, 'min_jet_e', event.min_jet_e)

        fill(tree, 'four_jets_mass', event.four_jets_mass)
        fill(tree, 'min_jets_mass', event.min_jets_mass)
        fill(tree, 'second_min_jets_mass', event.second_min_jets_mass)
        fill(tree, 'max_jets_mass', event.max_jets_mass)
        fill(tree, 'min_jets_angle', event.min_jets_angle)
        fill(tree, 'second_min_jets_angle', event.second_min_jets_angle)
        fill(tree, 'max_jets_angle', event.max_jets_angle)

        fill(tree, 'min_jets_lepton_angle', event.min_jets_lepton_angle)
        fill(tree, 'second_min_jets_lepton_angle', event.second_min_jets_lepton_angle)
        fill(tree, 'max_jets_lepton_angle', event.max_jets_lepton_angle)
        fill(tree, 'lep_pt_wrt_closest_jet', event.lep_pt_wrt_closest_jet)
        fill(tree, 'lep_pt_wrt_second_closest_jet', event.lep_pt_wrt_second_closest_jet)
        fill(tree, 'lep_pt_wrt_farthest_jet', event.lep_pt_wrt_farthest_jet)

        fill(tree, 'total_rec_mass', event.total_rec_mass)
        fill(tree, 'jets_sumpt', event.jets_sumpt)
        fill(tree, 'jets_vecp_over_sump', event.jets_vecp_over_sump)


# JETS SHAPE
def bookJetsShape(tree):
    var(tree, 'sphericity_jets')
    var(tree, 'aplanarity_jets')
    var(tree, 'planarity_jets')
    var(tree, 'sphericity_axis_jets')

def fillJetsShape(tree, event):
    if hasattr(event, 'sphericity_jets'):
        fill(tree, 'sphericity_jets', event.sphericity_jets)
        fill(tree, 'aplanarity_jets', event.aplanarity_jets)
        fill(tree, 'planarity_jets', event.planarity_jets)
        fill(tree, 'sphericity_axis_jets', event.sphericity_axis_jets)


# COUNT CHARGED TRACKS
def bookChargedTracks(tree):
    var(tree, 'e_rec_charged')
    var(tree, 'n_rec_charged', int)

def fillChargedTracks(tree, event):
    if hasattr(event, 'e_rec_charged'):
        fill(tree, 'e_rec_charged', event.e_rec_charged)
    if hasattr(event, 'n_rec_charged'):
        fill(tree, 'n_rec_charged', event.n_rec_charged)


# MISSING ENERGY
def bookMissingEnergy(tree):
    bookMyP4(tree, 'missing_sim')
    bookMyP4(tree, 'missing_rec')

def fillMissingEnergy(tree, event):
    if hasattr(event, 'missing_sim'):
        fillMyP4(tree, 'missing_sim', event.missing_sim)
    if hasattr(event, 'missing_rec'):
        fillMyP4(tree, 'missing_rec', event.missing_rec)


# TOP CONSTRAINER
def bookTopConstrainer(tree):
    var(tree, 'success', int)
    var(tree, 'chi2_algorithm')
    var(tree, 'tophadRec')
    var(tree, 'whadRec')
    var(tree, 'toplepRec')
    var(tree, 'wlepRec')
    var(tree, 'missingMassRec')
    var(tree, 'tophadFit')
    var(tree, 'whadFit')
    var(tree, 'toplepFit')
    var(tree, 'wlepFit')
    var(tree, 'missingMassFit')

    var(tree, 'chi2_tophadRec')
    var(tree, 'chi2_whadRec')
    var(tree, 'chi2_toplepRec')
    var(tree, 'chi2_wlepRec')
    var(tree, 'chi2_top_constrainer')
    
    # Add the decay channel
    var(tree, 'decay_channel')

def fillTopConstrainer(tree, event):

    fill(tree, 'decay_channel', event.decay_channel)

    if hasattr(event, 'success'):
        fill(tree, 'success', event.success)

    if hasattr(event, 'chi2_algorithm'):
        fill(tree, 'chi2_algorithm', event.chi2_algorithm)
        fill(tree, 'tophadRec', event.tophadRec.p4().M())
        fill(tree, 'whadRec', event.whadRec.p4().M())
        fill(tree, 'toplepRec', event.toplepRec.p4().M())
        fill(tree, 'wlepRec', event.wlepRec.p4().M())
        fill(tree, 'missingMassRec', event.missingMassRec.p4().M())
        fill(tree, 'tophadFit', event.tophadFit.p4().M())
        fill(tree, 'whadFit', event.whadFit.p4().M())
        fill(tree, 'toplepFit', event.toplepFit.p4().M())
        fill(tree, 'wlepFit', event.wlepFit.p4().M())
        fill(tree, 'missingMassFit', event.missingMassFit.p4().M())

        fill(tree, 'chi2_tophadRec', event.chi2_tophadRec)
        fill(tree, 'chi2_whadRec', event.chi2_whadRec)
        fill(tree, 'chi2_toplepRec', event.chi2_toplepRec)
        fill(tree, 'chi2_wlepRec', event.chi2_wlepRec)
        fill(tree, 'chi2_top_constrainer', event.chi2_top_constrainer)
