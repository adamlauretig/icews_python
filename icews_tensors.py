import pandas as pd
import numpy as np
import pickle
import tensorly as tl
from tensorly.decomposition import tucker, parafac, non_negative_tucker, matrix_product_state

tensor = np.random.random((10, 10, 10))
# mode-1 unfolding (i.e. zeroth mode)
unfolded = tl.unfold(tensor, mode=0)
# refold the unfolded tensor
tl.fold(unfolded, mode=0, shape=tensor.shape)
factors = parafac(tensor, rank=5)
core, factors = non_negative_tucker(tensor, rank=[5, 5, 5])
file_to_use = open("icews_df.obj", 'rb')
icews_df = pickle.load(file_to_use)
file_to_use.close()
dyad_event_counts = icews_df.sum(
    level = ['Source Country Code', 'Target Country Code', 'Quad Count'])
dyad_event_counts.reset_index(inplace = True)
dyad_event_counts_melt = dyad_event_counts.melt(
    id_vars = list(dyad_event_counts)[0:3], 
    value_vars = list(dyad_event_counts)[3:28], 
    var_name = 'year', value_name = 'event_count')
dyad_event_counts_melt_group = dyad_event_counts_melt.groupby(
    ['Source Country Code', 'Target Country Code', 'year', 'Quad Count']
    )['event_count'].mean()
shape = tuple(map(len, dyad_event_counts_melt_group.index.levels))
events_array = np.full(shape, np.nan)

    
events_array[dyad_event_counts_melt_group.index.codes] = dyad_event_counts_melt_group.values.flat
events_array = np.nan_to_num(events_array)
factors = parafac(events_array, rank=5)

