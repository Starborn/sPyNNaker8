import spynnaker8 as p
import numpy
import math
import unittest
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

p.setup(1) # simulation timestep (ms)
runtime = 500

# Post-synapse population
neuron_params = {
    "v_thresh": -50,
    "v_reset": -70,
    "v_rest": -65,
    "i_offset": 0 # DC input
                 }

# Learning parameters
min_weight = 0
max_weight = 0.1
pot_alpha=0.01
t_peak=100
initial_weight = 0.05
plastic_delay = 4

purkinje_cell = p.Population(1, # number of neurons
                       p.extra_models.IFCondExpCerebellum(**neuron_params),  # Neuron model
                       label="Purkinje Cell" # identifier
                       )


# Spike source to send spike via synapse
pf_spike_times = [50, 60, 65, 85, 101, 400]#, 150, 175, 180, 190, 240, 250, 255,
#                270, 300, 345, 350, 360, 370, 400, 422, 425, 427, 429]

granular_cell = p.Population(1, # number of sources
                        p.SpikeSourceArray, # source type
                        {'spike_times': pf_spike_times}, # source spike times
                        label="src1" # identifier
                        )

# Spike source to send spike via synapse from climbing fibre
cf_spike_times = [55, 80, 90, 95, 96, 201]#, 104, 107, 246]
climbing_fibre = p.Population(1, # number of sources
                        p.SpikeSourceArray, # source type
                        {'spike_times': cf_spike_times}, # source spike times
                        label="src2" # identifier
                        )

# Create projection from GC to PC
pfpc_plas = p.STDPMechanism(
    timing_dependence=p.extra_models.TimingDependencePFPC(t_peak=t_peak),
    weight_dependence=p.extra_models.WeightDependencePFPC(w_min=min_weight,
                                                          w_max=max_weight,
                                                          pot_alpha=pot_alpha),
    weight=initial_weight, delay=plastic_delay)

synapse_pfpc = p.Projection(
    granular_cell, purkinje_cell, p.AllToAllConnector(),
    synapse_type=pfpc_plas, receptor_type="excitatory")


# Create projection from CF to PC
synapse = p.Projection(
    climbing_fibre, purkinje_cell, p.OneToOneConnector(),
    p.StaticSynapse(weight=0.0, delay=1), receptor_type="excitatory")


granular_cell.record('spikes')
climbing_fibre.record('spikes')
purkinje_cell.record("all")

p.run(runtime)

granluar_cell_spikes = granular_cell.get_data('spikes')
climbing_fibre_spikes = climbing_fibre.get_data('spikes')
purkinje_data = purkinje_cell.get_data()

pf_weights = synapse_pfpc.get('weight', 'list', with_address=False)
print pf_weights

# Plot
F = Figure(
    # plot data for postsynaptic neuron
    Panel(granluar_cell_spikes.segments[0].spiketrains,
          yticks=True, markersize=2, xlim=(0, runtime)),
    Panel(climbing_fibre_spikes.segments[0].spiketrains,
          yticks=True, markersize=2, xlim=(0, runtime)),
    Panel(purkinje_data.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[purkinje_cell.label], yticks=True, xlim=(0, runtime)),
    Panel(purkinje_data.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=[purkinje_cell.label], yticks=True, xlim=(0, runtime)),
    Panel(purkinje_data.segments[0].spiketrains,
          yticks=True, markersize=2, xlim=(0, runtime)),
    )


plt.show()
p.end()

print "Job Complete"