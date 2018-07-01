from codex import io as codex_io
import warnings
import os.path as osp
import pandas as pd
import numpy as np


def aggregate(config, output_dir):
    """Aggregate cytometry data associated with an experiment into a single dataframe

    Args:
        config: Experiment configuration
        output_dir: Output directory for experiment
    Returns:
        DataFrame containing concatenation of all tile-based cytometry datasets with a global
            cell id as well as global x/y coordinates (where "global" means across region)
    """

    # Load per-tile csv exports
    df = []
    for idx in config.get_tile_indices():
        path = codex_io.get_cytometry_stats_path(idx.region_index, idx.tile_x, idx.tile_y)
        path = osp.join(output_dir, path)
        if not osp.exists(path):
            warnings.warn(
                'Expected cytometry data file at "{}" does not exist.  '
                'It will be ignored but this is worth investigating'
                .format(path)
            )
            continue
        df.append(pd.read_csv(path))
    df = pd.concat(df)

    # Start inserting before 'id' to get order rid, rx, ry (so they have to be inserted in reverse order)
    id_idx = df.columns.tolist().index('id')

    # Determine region coords for tile coordinate / point coordinate pairs
    def get_region_point_coords(r):
        tile_coord = r['tile_x'], r['tile_y']
        tile_point = r['x'], r['y']
        return config.get_region_point_coordinates(tile_coord, tile_point)
    reg_coords = df[['tile_x', 'tile_y', 'x', 'y']].apply(get_region_point_coords, axis=1)

    # Add region / global coordinates as separate fields
    df.insert(id_idx, 'ry', [c[1] for c in reg_coords])
    df.insert(id_idx, 'rx', [c[0] for c in reg_coords])

    # Insert global id for cells (i.e. across region)
    df.insert(id_idx, 'rid', np.arange(len(df)))

    return df





