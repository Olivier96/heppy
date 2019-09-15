import heppy.framework.config as cfg
import logging

def papas_sequence(detector_name):
    if detector_name == 'CMS':
        from heppy.papas.detectors.CMS_mod import CMS
        detector = CMS()
    elif detector_name == 'ILD':
        from heppy.papas.detectors.ILD import ILD
        detector = ILD()
    else:
        import pdb; pdb.set_trace()

    from heppy.analyzers.PapasSim import PapasSim
    papas = cfg.Analyzer(
        PapasSim,
        instance_label = 'papas',
        detector = detector,
        gen_particles = 'gen_particles_stable',
        sim_particles = 'sim_particles',
        verbose = True
    )

    from heppy.analyzers.PapasDisplay import PapasDisplay
    papasdisplay = cfg.Analyzer(
        PapasDisplay,
        instance_label = 'papas',
        detector = detector,
        projections = ['xy', 'yz'],
        screennames = ["simulated"],#["reconstructed"],#
        particles_type_and_subtypes = ['ps'],
        clusters_type_and_subtypes = [['es', 'hs']],
        #display_filter_func = lambda ptc: ptc.e()>1.,
        do_display = False
    )

    papasdisplaycompare = cfg.Analyzer(
        PapasDisplay,
        projections = ['xy', 'yz'],
        screennames = ["simulated", "reconstructed"],
        particles_type_and_subtypes = ['ps', 'pr'],
        clusters_type_and_subtypes = [['es', 'hs'],['em', 'hm']],
        detector = detector,
        #save = True,
        do_display = False
    )

    from heppy.analyzers.PapasPFBlockBuilder import PapasPFBlockBuilder
    pfblocks = cfg.Analyzer(
        PapasPFBlockBuilder,
        track_type_and_subtype = 'ts',
        ecal_type_and_subtype = 'em',
        hcal_type_and_subtype = 'hm'
    )

    from heppy.analyzers.PapasPFReconstructor import PapasPFReconstructor
    pfreconstruct = cfg.Analyzer(
        PapasPFReconstructor,
        track_type_and_subtype = 'ts',
        ecal_type_and_subtype = 'em',
        hcal_type_and_subtype = 'hm',
        block_type_and_subtype = 'br',
        # instance_label = 'papas_PFreconstruction',
        detector = detector,
        output = 'rec_particles',
        log_level=logging.WARNING
    )

    return [
        papas,
        pfblocks,
        pfreconstruct,
    ]
