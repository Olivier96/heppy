from heppy.framework.analyzer import Analyzer

class CountChargedTracks(Analyzer):
    '''
    from heppy.analyzers.CountChargedTracks import CountChargedTracks
    count_charged_tracks = cfg.Analyzer(
        CountChargedTracks,
        rec_particles = 'rec_particles',
    )

    '''

    def process(self, event):
        rec_particles = getattr(event, self.cfg_ana.rec_particles)

        e_rec_charged = 0.
        n_rec_charged = 0.

        for rec_ptc in rec_particles:
            if rec_ptc.q() != 0:
                e_rec_charged += rec_ptc.e()
                n_rec_charged += 1

        event.e_rec_charged = e_rec_charged
        event.n_rec_charged = n_rec_charged
