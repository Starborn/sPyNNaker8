# Standard library imports
import matplotlib.pyplot as plt
import numpy as np

# Third party imports
import spynnaker8 as p

# Local application imports
import utilities as util
from pyNN.random import RandomDistribution, NumpyRNG
from pyNN.space import Grid2D
from pyNN.utility.plotting import Figure, Panel

DEBUG = True

p.setup(1)  # simulation timestep (ms)
runtime = 1000  # ms

n_row = 50
n_col = 50
p.set_number_of_neurons_per_core(p.IF_curr_exp, 255)

is_auto_receptor = False

rng = NumpyRNG(seed=77364, parallel_safe=True)
synaptic_weight = 0.6
synaptic_radius = 10
orientation_pref_shift = 1

# Post-synapse population
neuron_params = {
    "v_thresh": -50,
    "v_reset": -65,
    "v_rest": -65,
    "i_offset": 0.8,  # DC input
    "tau_m": 20,  # membrane time constant
    "tau_refrac": 1,
}

# Define excitatory population
exc_grid = Grid2D(aspect_ratio=1.0, dx=1.0, dy=1.0, x0=-0, y0=0, z=0, fill_order='sequential')
exc_space = p.Space(axes='xy', periodic_boundaries=((-n_col / 2, n_col / 2), (-n_row / 2, n_row / 2)))
v_init = RandomDistribution('uniform', low=-65, high=-55, rng=rng)
pop_exc = p.Population(n_row * n_col,
                       p.IF_curr_exp(**neuron_params),
                       cellparams=None,
                       initial_values={'v': v_init},
                       structure=exc_grid,
                       label="Excitatory grid cells"
                       )

# Create view
view_exc = p.PopulationView(pop_exc, np.array([0, 1, n_col, n_col + 1]))

# Create recurrent inhibitory connections
loopConnections = list()
for pre_syn in range(0, n_row * n_col):
    presyn_pos = (pop_exc.positions[pre_syn])
    dir_pref = np.array(util.get_dir_pref(presyn_pos))

    for post_syn in range(0, n_row * n_col):
        # If different neurons
        if pre_syn != post_syn or is_auto_receptor:
            postsyn_pos = (pop_exc.positions[post_syn])
            dist = exc_space.distances(presyn_pos, postsyn_pos)
            dist = dist[0]
            # dist = util.get_neuron_distance_periodic(n_col, n_row, presyn_pos, postsyn_pos)

            # Establish connection
            # (Gwendolyn)
            if np.all(abs(np.subtract(dist, (orientation_pref_shift * dir_pref))) <= synaptic_radius):
                singleConnection = (pre_syn, post_syn, synaptic_weight, util.normalise(dist, 0, n_row))
                loopConnections.append(singleConnection)


# Create inhibitory connections
proj_exc = p.Projection(
    pop_exc, pop_exc, p.FromListConnector(loopConnections, ('weight', 'delay')),
    p.StaticSynapse(),
    receptor_type='inhibitory',
    label="Excitatory grid cells inhibitory connections")

pop_exc.record("all")
p.run(runtime)

exc_data_pop = pop_exc.get_data()
exc_data_view = view_exc.get_data()
firing_rate = pop_exc.mean_spike_count(gather=True) * (1000 / runtime)
print("Mean spike count=" + str(pop_exc.mean_spike_count(gather=True)))

# Plot activity
pop_spike_trains = exc_data_pop.segments[0].spiketrains

# Plot
F = Figure(
    # plot data for postsynaptic neuron
    Panel(exc_data_view.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          xlabel="Time (ms)",
          data_labels=[pop_exc.label], yticks=True, xticks=True, xlim=(0, runtime)
          ),
    Panel(exc_data_view.segments[0].filter(name='gsyn_exc')[0],
          ylabel="Excitatory synaptic conduction (uS)",
          xlabel="Time (ms)",
          data_labels=[pop_exc.label], yticks=True, xticks=True, xlim=(0, runtime)
          ),
    Panel(exc_data_view.segments[0].filter(name='gsyn_inh')[0],
          ylabel="Inhibitory synaptic conduction (uS)",
          xlabel="Time (ms)",
          data_labels=[pop_exc.label], yticks=True, xticks=True, xlim=(0, runtime)
          ),
    Panel(exc_data_view.segments[0].spiketrains,
          yticks=True, xticks=True, xlabel="Time (ms)", markersize=2, xlim=(0, runtime)
          ),
    Panel(pop_spike_trains,
          yticks=True, xticks=True, xlabel="Time (ms)", markersize=2, xlim=(0, runtime)
          ),
)

plt.show()
p.end()

util.plot_population_firing_rate(pop_spike_trains, pop_exc.positions, [0, 150, 500, runtime], n_row, n_col, False)
util.plot_population_membrane_potential_activity(exc_data_pop.segments[0].filter(name='v')[0], pop_exc.positions,
                                                 -50, [0, 150, 500, runtime-1], n_row, n_col, False)
util.plot_population_spike_activity(pop_spike_trains, pop_exc.positions, [0, 150, 500, runtime], n_row, n_col, False)

# print(pop_exc.describe(template='population_default.txt', engine='default'))
if DEBUG:
    print(util.get_neuron_connections(0, loopConnections))
    print("Firing rate=" + str(firing_rate) + "Hz")
    print("i_offset=" + str(neuron_params['i_offset']) + "nA")
    print("tau_refrac=" + str(neuron_params['tau_refrac']) + "ms")
    print("tau_m=" + str(neuron_params['tau_m']) + "ms")