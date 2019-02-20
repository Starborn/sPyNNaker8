from __future__ import division
import spynnaker8 as sim

CHIPS_PER_BOARD_EXCLUDING_SAFETY = 43.19

class ManyBoards(object):
    def add_pop(self, x, y, n_neurons, input):
        pop = sim.Population(
            n_neurons, sim.IF_curr_exp(), label="pop_{}_{}".format(x, y))
        pop.add_placement_constraint(x=x, y=y)
        sim.Projection(input, pop, sim.AllToAllConnector(),
                       synapse_type=sim.StaticSynapse(weight=5, delay=1))
        pop.record("all")
        return pop


    def setup(self, n_boards, n_neurons, simtime):
        n_chips_required = n_boards * CHIPS_PER_BOARD_EXCLUDING_SAFETY
        sim.setup(timestep=1.0, n_chips_required=n_chips_required)
        machine = sim.get_machine()
        input_spikes = list(range(0, simtime - 100, 10))
        input = sim.Population(1, sim.SpikeSourceArray(spike_times=input_spikes),
                               label="input")
        pops = []
        for i, chip in enumerate(machine.ethernet_connected_chips):
            if i >= n_boards:
                break
            offset = machine.BOARD_48_CHIPS[i % 48]
            pops.append(self.add_pop(
                chip.x + offset[0], chip.y + offset[1], n_neurons, input))
        return pops


    def check_core(self, spikes, v, simtime, label, index):
        if len(spikes) <= (simtime/10 - 15):
            raise AssertionError(
                "Too few spikes for neuron {} in {}. Expected {} found {}".
                    format(index, label, (simtime/10 - 15), len(spikes)))
        for spike_time in spikes:
            time = int(spike_time.magnitude)
            if not (-53 < v[time] < -49):
                raise AssertionError(
                    "Incorrect prespike V for neuron {} at time {} in {}. "
                    "Found {}".format(
                        index, time, label, v[time]))
            if not (-66 < v[time+1] < -64):
                raise AssertionError(
                    "Incorrect postspike V for neuron {} at time {} in {}. "
                    "Found {}".format(
                        index, time, label, v[time]))

    def check_pop(self, pop, simtime):
        neo = pop.get_data(["spikes", "v"])
        spikes = neo.segments[0].spiketrains
        v = neo.segments[0].filter(name="v")[0]
        if len(v) != simtime:
            print(len(v), simtime)
            raise AssertionError(
                "Incorrect size of v in {}. Expected {} found {}".format(
                    pop.label, simtime, len(v)))
        assert(len(v) == simtime)
        for i in range(len(spikes)):
            self.check_core(spikes[i], v[:, i], simtime, pop.label, i)

    def do_run(self, n_boards, n_neurons, simtime):
        pops = self.setup(n_boards=n_boards, n_neurons=n_neurons, simtime=simtime)
        sim.run(simtime)
        for pop in pops:
            self.check_pop(pop, simtime)
        return sim


if __name__ == '__main__':
    """
    main entrance method
    """
    me = ManyBoards()
    sim = me.do_run(n_boards=5, n_neurons=255, simtime=300)
    sim.end()
