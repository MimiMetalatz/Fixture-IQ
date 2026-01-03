import numpy as np
from app.context.context_builder import ContextBuilder
from app.context.context_vector_builder import ContextVectorBuilder

# 1. Build historical context
context_builder = ContextBuilder(data_dir="data/raw", form_window=5)
context_df = context_builder.build()

# 2. Pick one historical row
row = context_df.iloc[0]

# 3. Build vectors both ways
vb = ContextVectorBuilder()

v_batch = vb.build(context_df).iloc[0].tolist()
v_single = vb.build_single(row.to_dict())

# 4. Compare
print("Batch vector:", v_batch)
print("Single vector:", v_single)
print("Identical:", np.allclose(v_batch, v_single))
