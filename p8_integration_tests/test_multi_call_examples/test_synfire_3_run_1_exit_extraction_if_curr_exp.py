"""
Synfirechain-like example
"""
from p8_integration_tests.base_test_case import BaseTestCase
from p8_integration_tests.scripts.synfire_run import SynfireRunner
import spynnaker.plot_utils as plot_utils
import spynnaker.spike_checker as spike_checker


nNeurons = 200  # number of neurons in each population
run_times = [1000, 1000, 1000]
reset = False
synfire_run = SynfireRunner()


class Synfire3Run1ExitExtractionIfCurrExp(BaseTestCase):

    def test_run(self):
        synfire_run.do_run(nNeurons, run_times=run_times, reset=reset)
        spikes = synfire_run.get_output_pop_spikes_list_numpy()

        self.assertEquals(53, len(spikes[0]))
        self.assertEquals(106, len(spikes[1]))
        self.assertEquals(158, len(spikes[2]))
        spike_checker.synfire_spike_checker(spikes[0], nNeurons)
        spike_checker.synfire_spike_checker(spikes[1], nNeurons)
        spike_checker.synfire_spike_checker(spikes[2], nNeurons)


if __name__ == '__main__':
    synfire_run.do_run(nNeurons, run_times=run_times, reset=reset)
    gsyn = synfire_run.get_output_pop_gsyn_exc_list_numpy()
    v = synfire_run.get_output_pop_voltage_list_numpy()
    spikes = synfire_run.get_output_pop_spikes_list_numpy()

    print len(spikes[0])
    print len(spikes[1])
    print len(spikes[2])
    plot_utils.plot_spikes(spikes)
    plot_utils.heat_plot(v[0], title="v1")
    plot_utils.heat_plot(gsyn[0], title="gysn1")
    plot_utils.heat_plot(v[1], title="v2")
    plot_utils.heat_plot(gsyn[1], title="gysn2")
    plot_utils.heat_plot(v[2], title="v3")
    plot_utils.heat_plot(gsyn[2], title="gysn3")
