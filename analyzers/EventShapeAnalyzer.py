from heppy.framework.analyzer import Analyzer
from heppy.utils.eventShape import eventShape


class EventShapeAnalyzer(Analyzer):
    '''
    from heppy.analyzers.EventShapeAnalyzer import EventShapeAnalyzer
    jets_shape = cfg.Analyzer(
      EventShapeAnalyzer,
      input_particles = 'jets',
      output_label = 'jets'
    )
    '''

    def process(self, event):
        input_particles = getattr(event, self.cfg_ana.input_particles)

        input_p4s = [ptc.p4() for ptc in input_particles]
        sphericity, aplanarity, planarity, sphericity_axis = eventShape(input_p4s)

        setattr(event, "sphericity_" + self.cfg_ana.output_label, sphericity)
        setattr(event, "aplanarity_" + self.cfg_ana.output_label, aplanarity)
        setattr(event, "planarity_" + self.cfg_ana.output_label, planarity)
        setattr(event, "sphericity_axis_" + self.cfg_ana.output_label, sphericity_axis[2])
