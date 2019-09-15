from heppy.framework.analyzer import Analyzer

class ShowVertices(Analyzer):

    '''
    from heppy.analyzers.ShowVertices import ShowVertices
    show_vertices = cfg.Analyzer(
        ShowVertices,
        rec_particles = 'rec_particles',
    )

    '''

    def process(self, event):
        rec_particles = getattr(event, self.cfg_ana.rec_particles)

        print event.quark_type

        for rec_ptc in rec_particles:
            if rec_ptc.q() == 0:
                print
                continue

            print
            print "NEW PARTICLE"
            print
            print rec_ptc
            tmp = 'pos(mm) x = {x:9.8f}, y = {y:9.8f}, z = {z:9.8f}'
            print tmp.format(x = rec_ptc.vertex.X()*1000.,
                             y = rec_ptc.vertex.Y()*1000.,
                             z = rec_ptc.vertex.Z()*1000.,)
            print
            matched = rec_ptc.match
            print matched
            print matched.start_vertex()
            print
            tmp = 'helix: origin_X = {origin_X}, origin_Y = {origin_Y}, origin_Z = {origin_Z}, E = {E}, rho = {rho}, omega = {omega}'
            print tmp.format(origin_X = rec_ptc.path.origin.X(),
                             origin_Y = rec_ptc.path.origin.Y(),
                             origin_Z = rec_ptc.path.origin.Z(),
                             E = rec_ptc.path.p4.E(),
                             rho = rec_ptc.path.rho,
                             omega = rec_ptc.path.omega)
