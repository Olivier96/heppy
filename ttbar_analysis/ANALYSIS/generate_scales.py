import numpy as np

# Cross section in pb
cross = [0.0558251,0.0580268,0.0600319,0.0624185,0.0649094,0.0673648,0.0701316,0.0732234,0.0763333,0.0794255,0.0826998,0.0866187,0.0903434,0.0946387,0.0991898,0.103984,0.109054,0.114238,0.120787,0.127142,0.134166,0.141128,0.148895,0.15736,0.166943,0.176824,0.187491,0.198932,0.210874,0.224509,0.237346,0.253184,0.268178,0.284413,0.301317,0.318452,0.337021,0.355833,0.375295,0.393069,0.410327,0.429906,0.446551,0.464438,0.479664,0.495107,0.507218,0.517123,0.527827,0.536955,0.543833,0.54725,0.551434,0.554065,0.556295,0.555528,0.5546,0.552647,0.549299,0.547453,0.544625,0.542981,0.539828,0.538065,0.533784,0.533636,0.531985,0.529325,0.527584,0.52821,0.526444,0.526558,0.525235,0.526088,0.527314,0.5255,0.526316,0.52791,0.526638,0.526229,0.527792,0.527865,0.528102,0.529938,0.52977,0.530582,0.532031,0.532309,0.533521,0.532478,0.534065,0.535315,0.535931,0.536464,0.535827,0.537838,0.537522,0.539591,0.539621,0.541064,0.5415,0.54234,0.543261,0.544268,0.545691,0.546044,0.546117,0.546657,0.548466,0.548866,0.549467,0.550137,0.550742,0.552114,0.552878,0.554008,0.553898,0.555281,0.555572,0.55596,0.557561,0.558524,0.559096,0.560471,0.560975,0.561483,0.56207,0.562197,0.563689,0.564049,0.564652,0.565939,0.566953,0.566695,0.56772,0.568553,0.569411,0.569762,0.571852,0.571559,0.571296,0.572648,0.574086,0.573056,0.574318,0.574247,0.575616,0.576473,0.576183,0.577476]

sqrts_1715 = np.arange(339,354,0.1)
BR_hadronic = 0.457
BR_semilep = 0.438
BR_dilep = 0.105


#index = (np.abs(sqrts_1715-340)).argmin()
#print index
#for i in range(len(cross)):
#    print "{}\t {}".format(sqrts[i],cross[i])

#Takes top mass in GeV and gives new sqrts array for the cross section
def shifted_sqrts(mtop):
    ds = 2*(mtop-171.5)
    return np.arange(339+ds,354+ds,0.1)
    
# Find the index at which sqrts is in the list for numpy
def index_sqrts(list,s):
    idx = (np.abs(list-s)).argmin()
    if (list[idx]-s) > 0.1:
        return (idx,list[idx]-s)
    else:
        return idx

# Obtain the cross section from the index_sqrts() function
def get_cross(idx):
    if type(idx) == tuple:
        ds = idx[1]
        idx = idx[0]
    else:
        ds = 0
    # Extrapolate if necessary the cross section for lower values 
    if ds != 0:
        dcross_ds = (0.0580268-0.0558251)/0.1
        dcross = dcross_ds * ds
        new_cross = cross[idx] - dcross
        # If the cross section is extrapolated to negative values just set to 0
        if new_cross < 0:
            new_cross = 0
    else:
        new_cross = cross[idx]
    
    return new_cross
#print shifted_sqrts(174.2)
#print index_sqrts(shifted_sqrts(174.2),340)

N_ww = 1000000
N_hz = 26000
N_zz = 100000
# Takes top mass and integrated Luminosity in ab-1 and gives the scale matrix, in # events
def gen_scale_matrix(mtop,L_int):
    sqrts = shifted_sqrts(mtop)
    matrix = []
    for s in [340.,342.,344.,346.,350.]:
        idx = index_sqrts(sqrts,s)
        cross_tt = get_cross(idx)
#        print cross_tt
        N_tt = cross_tt * L_int * 1e6
        list = [int(N_tt*BR_semilep),int(N_tt*BR_dilep),int(N_tt*BR_hadronic),N_hz,N_zz,N_ww]
        matrix.append(list)
    return matrix

def gen_scale_matrix_list(mtop_list,L_int):
    scale_matrix_list = []
    for mtop in mtop_list:
        scale_matrix_list.append(gen_scale_matrix(mtop,L_int))
    return scale_matrix_list

L_int = 0.2 # ab-1
top_masses = [171.8,172.6,173.0,173.4,174.2]

# Check if this result is similar to the one used previously
#print gen_scale_matrix(171.5,0.2)
# Unit test ok!


scale_matrix_list = gen_scale_matrix_list(top_masses,L_int)

#for m in scale_matrix_list:
#    for row in m:
#        print row
#    print "-"*50
#
#print "\n"*3




def cross_graph_coords(mtop):
    # Init arrays for chosen top quark mass
    sqrts_array = shifted_sqrts(mtop)
    cross_array = cross[:]
    # While the sqrts smallest value is larger than 339 GeV keep adding points at the start of the array
    extra_sqrts = [sqrts_array[0]]
    extra_cross = [cross_array[0]]
    while (extra_sqrts[0] > 339) :
        # Grab new sqrts and cross section using help functions
        next_sqrts = extra_sqrts[0] - 0.1
        next_idx = index_sqrts(sqrts_array, next_sqrts)
        next_cross = get_cross(next_idx)
        extra_sqrts.insert(0,next_sqrts)
        extra_cross.insert(0,next_cross)
    # Remove redundant last points in extra_arrays:
    extra_sqrts = extra_sqrts[:-1]
    extra_cross = extra_cross[:-1]
    # Concatenate arrays and return
    sqrts_array = list(extra_sqrts)+ list(sqrts_array)
    cross_array = list(extra_cross)+ list(cross_array)
    return (sqrts_array,cross_array)

def test_cross_graph_coords():
    A = cross_graph_coords(174.2)
    ss = A[0]
    cc = A[1]
    for i in range(len(ss)):
        print ss[i], cc[i]
    return 0



