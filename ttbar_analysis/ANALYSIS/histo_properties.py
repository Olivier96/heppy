

#################STRUCT CLASS DEFINTION#########################
# Create a class to store all the properties 
class histo_properties:
    def __init__(self, filename, var, n_bins, x_min, x_max, xlabel, cuts, overflow = False, underflow = False, default_cuts = ""):
        self.filename = filename
        self.var =var
        self.n_bins = n_bins
        self.x_min = x_min
        self.x_max = x_max
        self.xlabel = xlabel
        #self.ylabel = ylabel
        self.cuts = cuts
        self.histo_name="histo_"+self.xlabel
        self.overflow = overflow
        self.underflow = underflow
        self.default_cuts = default_cuts
        
# Unit test
test = histo_properties("file1.root", "test_e", 100, 0, 1000, "x    (m)", "four_jets_mass > 150")
def test_histo_properties(histo):
    print histo.__dict__
    return 1

#test_histo_properties(test)
#print test.n_bins
# End unit test
#################END STRUCT CLASS DEFINTION#####################












