from heppy.framework.analyzer import Analyzer

class ShowParticles(Analyzer):

    '''
    from heppy.analyzers.ShowParticles import ShowParticles
    show_particles = cfg.Analyzer(
        ShowParticles,
        gen_particles = 'gen_particles',
        rec_particles = 'rec_particles',
    )

    '''

    def process(self, event):
        gen_particles = getattr(event, self.cfg_ana.gen_particles)
        rec_particles = getattr(event, self.cfg_ana.rec_particles)

        print
        print "GEN PARTICELS"
        print
        for gen_ptc in gen_particles:
            print gen_ptc

        print
        print "REC PARTICELS"
        print
        for rec_ptc in rec_particles:
            print rec_ptc
