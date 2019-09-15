from heppy.framework.analyzer import Analyzer

debug = False


class Sorter(Analyzer):
    '''
    Example:
    from heppy.analyzers.Sorter import Sorter
    sort_iso_leptons = cfg.Analyzer(
      Sorter,
      'sort_iso_leptons',
      objects = 'sel_iso_leptons',
      sorter_func = lambda lep : lep.iso.sumpt/lep.pt()
    )
    * input_objects : the input collection.
        if a dictionary, the filtering function is applied to the dictionary values,
        and not to the keys.
    * output : the output collection
    * filter_func : a function object.
    You may define a function in the usual way in your configuration file,
    or use a lambda statement as done above.
    This lambda statement is the definition of a function. It means:
    given ptc, return ptc.e()>10. and abs(ptc.pdgid()) in [11, 13].
    In other words, return True if the particle has an energy larger than 10 GeV,
    and a pdgid equal to +-11 (electrons) or +-13 (muons).
    '''

    def process(self, event):

        input_collection = getattr(event, self.cfg_ana.input_objects)
        sorter_func = self.cfg_ana.sorter_func

        if debug:
            def print_input_collection(input_collection):
                for particle in input_collection:
                    print particle
                    if hasattr(particle, 'iso'):
                        if hasattr(particle.iso, 'sume'):
                            print particle.iso.sume
                    elif hasattr(particle, 'logbtag'):
                        print particle.logbtag

        if debug:
            print
            print "sorting"
            print
            print "before"
            print_input_collection(input_collection)
            print

        input_collection.sort(key = sorter_func)

        if debug:
            print_input_collection(input_collection)
            print
