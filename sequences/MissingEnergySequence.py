import heppy.framework.config as cfg

def missing_energy_sequence(cdm_energy):
    from heppy.analyzers.RecoilBuilder import RecoilBuilder
    missing_sim = cfg.Analyzer(
        RecoilBuilder,
        output = 'missing_sim',
        sqrts = cdm_energy,
        to_remove = 'gen_particles_stable'
    )

    missing_rec = cfg.Analyzer(
        RecoilBuilder,
        output = 'missing_rec',
        sqrts = cdm_energy,
        to_remove = 'rec_particles'
    )

    from heppy.analyzers.TotalEnergy import TotalEnergy
    total_energy = cfg.Analyzer(
      TotalEnergy,
      gen_particles_stable_and_neutrinos = 'gen_particles_stable_and_neutrinos',
      gen_particles_stable = 'gen_particles_stable',
      rec_particles = 'rec_particles',
    )

    from heppy.analyzers.ChargeAndNeutralEnergy import ChargeAndNeutralEnergy
    charge_neutral_energy = cfg.Analyzer(
        ChargeAndNeutralEnergy,
        rec_particles = 'rec_particles',
        gen_particles_stable = 'gen_particles_stable',
    )

    return [
        missing_sim,
        missing_rec,
        # total_energy,
        # charge_neutral_energy
    ]
