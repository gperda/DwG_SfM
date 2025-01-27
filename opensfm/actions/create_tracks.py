from timeit import default_timer as timer

from opensfm import io
from opensfm import tracking
import networkx as nx
import matplotlib.pyplot as plt
from opensfm import graphing
from opensfm.dataset_base import DataSetBase


def run_dataset(data: DataSetBase) -> None:
    """Link matches pair-wise matches into tracks."""

    start = timer()
    features, colors, segmentations, instances = tracking.load_features(
        data, data.images()
    )
    features_end = timer()
    matches = tracking.load_matches(data, data.images())
    matches_end = timer()

    tracks_manager = tracking.create_tracks_manager(
        features,
        colors,
        segmentations,
        instances,
        matches,
        data.config["min_track_length"],
    )
    tracks_end = timer()

    G = tracking.as_weighted_graph(tracks_manager)
    # operazioni sul grafo
    matches_to_remove = graphing.update_graph(G)

    new_matches = tracking.remove_matches(matches, matches_to_remove)

    tracks_manager = tracking.create_tracks_manager(
        features,
        colors,
        segmentations,
        instances,
        new_matches,
        data.config["min_track_length"],
    )

    data.save_tracks_manager(tracks_manager)
    write_report(
        data,
        tracks_manager,
        features_end - start,
        matches_end - features_end,
        tracks_end - matches_end,
    )


def write_report(
    data: DataSetBase, tracks_manager, features_time, matches_time, tracks_time
) -> None:
    view_graph = [
        (k[0], k[1], v) for k, v in tracks_manager.get_all_pairs_connectivity().items()
    ]

    report = {
        "wall_times": {
            "load_features": features_time,
            "load_matches": matches_time,
            "compute_tracks": tracks_time,
        },
        "wall_time": features_time + matches_time + tracks_time,
        "num_images": tracks_manager.num_shots(),
        "num_tracks": tracks_manager.num_tracks(),
        "view_graph": view_graph,
    }
    data.save_report(io.json_dumps(report), "tracks.json")
