#!/usr/bin/env python
import spynnaker8 as p
from spynnaker8.utilities import neo_convertor
from p8_integration_tests.base_test_case import BaseTestCase


class TestSynapsesExcitVsInhib(BaseTestCase):

    def do_run(self):
        p.setup(timestep=1.0, min_delay=1.0, max_delay=1.0)

        cell_params = {'i_offset': .1, 'tau_refrac': 3.0, 'v_rest': -65.0,
                       'v_thresh': -51.0, 'tau_syn_E': 2.0,
                       'tau_syn_I': 5.0, 'v_reset': -70.0,
                       'e_rev_E': 0., 'e_rev_I': -80.}

        # setup test population
        if_pop = p.Population(1, p.IF_cond_exp, cell_params)
        # setup spike sources
        exc_pop = p.Population(1, p.SpikeSourceArray,
                               {'spike_times': [20., 40., 60.]})
        inh_pop = p.Population(1, p.SpikeSourceArray,
                               {'spike_times': [120., 140., 160.]})
        # setup excitatory and inhibitory connections
        listcon = p.FromListConnector([(0, 0, 0.05, 1.0)])
        p.Projection(exc_pop, if_pop, listcon, receptor_type='excitatory')
        p.Projection(inh_pop, if_pop, listcon, receptor_type='inhibitory')
        # setup recorder
        if_pop.record(["v"])
        p.run(100)
        p.reset()
        if_pop.initialize(v=-65)
        p.run(100)
        # read out voltage and plot
        neo = if_pop.get_data("all")
        v = neo_convertor.convert_data(neo, "v")
        p.end()

        self.assertGreater(v[22][2], v[21][2])
        self.assertGreater(v[42][2], v[41][2])
        self.assertGreater(v[62][2], v[61][2])
        self.assertLess(v[122][2], v[121][2])
        self.assertLess(v[142][2], v[141][2])
        self.assertLess(v[162][2], v[161][2])

    def test_run(self):
        self.runsafe(self.do_run)
