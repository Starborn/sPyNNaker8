import spynnaker8 as p
from pyNN.utility.plotting import Figure, Panel, DataTable
from pyNN.random import RandomDistribution
import matplotlib.pyplot as plt
import numpy as np
from neo.core.spiketrain import SpikeTrain
from scipy.ndimage.measurements import label
from matplotlib.pyplot import legend
from idna.core import _alabel_prefix

from neo.io import PyNNNumpyIO
from neo.io import AsciiSpikeTrainIO
from neo.io import PyNNTextIO

class SimpleClassifier():
    """
    Recreation of a simple classifier experiment from Brader, Senn, Fusi 2007.
    The network contains 2000 inputs, 1000 inhibitory units, and one Brader-Senn-Fusi neuron.
    It is presented 400 uncorrelated patters split into 2 classes.
    """

    w_mult=0.1
    a_plus = 0.11
    a_minus = 0.11
    w_min = 0.0
    w_max = 1.0
    w_drift = .0035
    th_w = 0.50
    V_th = -56.0
    Ca_th_l = 3.0
    Ca_th_h1 = 4.0
    Ca_th_h2 = 13.0
    tau_Ca = 150

    def __init__(self, N_patterns=400, inp_pop_sz=2000, inh_pop_sz=1000, low_inp_freq=2, high_inp_freq=50, low_teacher=50, high_teacher=150, inp_inh_conn_prob = 8.0/1000,
                 N_active = 100):
        init_patterns(N_patterns, inp_pop_sz, N_active)
        init_network(inp_pop_sz, inh_pop_sz, inp_inh_conn_prob)
        self.low_inp_freq = low_inp_freq
        self.high_inp_freq = high_inp_freq
        self.low_teacher =low_teacher
        self.high_teacher =high_teacher


    """
    Generate indices of active units in all patterns.
    Assume that first half of patterns is from class 0, and the other half is from class 1
    """
    def init_patterns(self, N_patterns, inp_pop_sz, N_active):
        self.N_patterns = N_patterns
        self.patterns = np.zeros((N_patterns, N_active))
        for i in N_patterns:
            inds = np.random.choice(inp_pop_sz, N_active, replace=False)
            self.patterns[i, :] = inds

    """
    Create populations and projections
    """
    def init_network(self, inp_pop_sz=2000, inh_pop_sz=1000, inp_inh_conn_prob = 8.0/1000):
        p.setup(1)
        # populations:
        self.pop_src = p.Population(inp_pop_sz, p.SpikeSourcePoisson(rate=10), label="src")
        self.pop_teacher = p.Population(1, p.SpikeSourcePoisson(rate=150), label="teacher")
        cell_params = {"i_offset":0.0,  "tau_ca2":self.tau_Ca, "i_alpha":1., "i_ca2":3.,   'v_reset':-65}
        self.pop_inh = p.Population(inh_pop_sz, p.IF_curr_exp(), label="inhibitory")
        self.pop_ex = p.Population(1, p.extra_models.IFCurrExpCa2Concentration, cell_params, label="test")
        # projections:
        rd = RandomDistribution('uniform', (0, self.w_mult))

        syn_plas = p.STDPMechanism(
            timing_dependence = p.PreOnly(A_plus = self.a_plus*self.w_max*self.w_mult, A_minus = self.a_minus*self.w_max*self.w_mult, th_v_mem=self.V_th, th_ca_up_l = self.Ca_th_l,
                                          th_ca_up_h = self.Ca_th_h2, th_ca_dn_l = self.Ca_th_l, th_ca_dn_h = self.Ca_th_h1),
            weight_dependence = p.WeightDependenceFusi(w_min=self.w_min*self.w_mult, w_max=self.w_max*self.w_mult, w_drift=self.w_drift*self.w_mult, th_w=self.th_w * self.w_mult),
            weight=rd, delay=1.0)


        self.proj_inp_ex = p.Projection(self.pop_src, self.pop_ex,   p.AllToAllConnector(),  synapse_type=syn_plas, receptor_type='excitatory')

        self.proj_inp_inh = p.Projection(self.pop_src,  self.pop_inh,  p.FixedProbabilityConnector(inp_inh_conn_prob),
                   synapse_type=p.StaticSynapse(weight=1.0),  receptor_type='excitatory')
        self.proj_inh_ex = p.Projection(self.pop_inh,  self.pop_ex,  p.AllToAllConnector(),
                   synapse_type=p.StaticSynapse(weight=self.w_mult),  receptor_type='inhibitory')
        self.proj_teach_ex = p.Projection(self.pop_teacher,  self.pop_ex,  p.AllToAllConnector(),
                   synapse_type=p.StaticSynapse(weight=2.0),  receptor_type='excitatory')

        self.pop_ex.record(['spikes'])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        p.end()

    """
    Present one pattern to the network
    """
    def present_pattern(self, num_pattern, teacher_freq):
        pass

    """
    Perform N_presentations presentations of the set of patterns, each time in a different random order
    """
    def train(self, N_presentations):
        #
        pass

    """
    Save results: output firing rates for each presentation of each pattern.
    """
    def save_data(self):
        pass

