from heppy.framework.analyzer import Analyzer

class ChargeAndNeutralEnergy(Analyzer):
    '''Energy and number of particles, total, charged, photons and neutral, both
    generated and reconstructed.

    Here is an example:
    from heppy.analyzers.ChargeAndNeutralEnergy import ChargeAndNeutralEnergy
    charge_neutral_energy = cfg.Analyzer(
        ChargeAndNeutralEnergy,
        rec_particles = 'rec_particles',
        gen_particles_stable = 'gen_particles_stable',
    )
    '''

    def process(self, event):
        gen_particles_stable = getattr(event, self.cfg_ana.gen_particles_stable)
        rec_particles = getattr(event, self.cfg_ana.rec_particles)

        gen_energy = 0.
        gen_charged = 0.
        gen_photon = 0.
        gen_neutral = 0.

        rec_energy = 0.
        rec_charged = 0.
        rec_photon = 0.
        rec_neutral = 0.

        n_gen = 0.
        n_gen_charged = 0.
        n_gen_photon = 0.
        n_gen_neutral = 0.

        n_rec = 0.
        n_rec_charged = 0.
        n_rec_photon = 0.
        n_rec_neutral = 0.


        for gen_ptc in gen_particles_stable:
            gen_energy += gen_ptc.e()
            n_gen += 1
            if gen_ptc.q() != 0:
                gen_charged += gen_ptc.e()
                n_gen_charged += 1
            elif gen_ptc.q() == 0 and gen_ptc.pdgid() == 22:
                gen_photon += gen_ptc.e()
                n_gen_photon += 1
            else:
                gen_neutral += gen_ptc.e()
                n_gen_neutral += 1

        for rec_ptc in rec_particles:
            rec_energy += rec_ptc.e()
            n_rec += 1
            if rec_ptc.q() != 0:
                rec_charged += rec_ptc.e()
                n_rec_charged += 1
            elif rec_ptc.q() == 0 and rec_ptc.pdgid() == 22:
                rec_photon += rec_ptc.e()
                n_rec_photon += 1
            else:
                rec_neutral += rec_ptc.e()
                n_rec_neutral += 1

        event.gen_energy = gen_energy
        event.gen_charged = gen_charged
        event.gen_photon = gen_photon
        event.gen_neutral = gen_neutral

        event.rec_energy = rec_energy
        event.rec_charged = rec_charged
        event.rec_photon = rec_photon
        event.rec_neutral = rec_neutral

        event.n_gen = n_gen
        event.n_gen_charged = n_gen_charged
        event.n_gen_photon = n_gen_photon
        event.n_gen_neutral = n_gen_neutral

        event.n_rec = n_rec
        event.n_rec_charged = n_rec_charged
        event.n_rec_photon = n_rec_photon
        event.n_rec_neutral = n_rec_neutral


        if gen_energy == 0:
            event.delta_energy = -99
        else:
            event.delta_energy = (rec_energy - gen_energy)/gen_energy

        if gen_charged == 0:
            event.delta_charged = -99
        else:
            event.delta_charged = (rec_charged - gen_charged)/gen_charged

        if gen_photon == 0:
            event.delta_photon = -99
        else:
            event.delta_photon = (rec_photon - gen_photon)/gen_photon

        if gen_neutral == 0:
            event.delta_neutral = -99
        else:
            event.delta_neutral = (rec_neutral - gen_neutral)/gen_neutral
