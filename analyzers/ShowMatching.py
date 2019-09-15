from heppy.framework.analyzer import Analyzer
from heppy.utils.delta_alpha import delta_alpha

class ShowMatching(Analyzer):
    '''
    from heppy.analyzers.ShowMatching import ShowMatching
    show_matching = cfg.Analyzer(
        ShowMatching,
        rec_particles = 'rec_particles',
        gen_particles_stable = 'gen_particles_stable',
    )

    '''

    def process(self, event):
        gen_particles_stable = getattr(event, self.cfg_ana.gen_particles_stable)
        rec_particles = getattr(event, self.cfg_ana.rec_particles)

        print
        print
        print
        print "GEN PARTICLES"

        for i, gen_ptc in enumerate(gen_particles_stable):
            print
            print "particle ", i
            print gen_ptc
            print "match: ", gen_ptc.match
            if gen_ptc.match != None:
                print "delta_alpha= ", delta_alpha(gen_ptc, gen_ptc.match)
                print "match of the match: ", gen_ptc.match.match
                if gen_ptc.match.match == gen_ptc:
                    print "match of the match OK"
                else:
                    print "match of the match NOT OK"
            print
        print
        print
        print
        print "REC PARTICLES"

        for i, rec_ptc in enumerate(rec_particles):
            print
            print "particle ", i
            print rec_ptc
            print "match: ", rec_ptc.match
            if rec_ptc.match != None:
                print "delta_alpha= ", delta_alpha(rec_ptc, rec_ptc.match)
                print "match of the match: ", rec_ptc.match.match
                if rec_ptc.match.match == rec_ptc:
                    print "match of the match OK"
                else:
                    print "match of the match NOT OK"
            print
