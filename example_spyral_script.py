import dotenv

dotenv.load_dotenv()

from spyral import (
    Pipeline,
    start_pipeline,
    PointcloudPhase,
    ClusterPhase,
    EstimationPhase,
    InterpLeastSqSolverPhase,
)
from spyral import (
    PadParameters,
    GetParameters,
    FribParameters,
    DetectorParameters,
    ClusterParameters,
    SolverParameters,
    EstimateParameters,
    DEFAULT_MAP,
    DEFAULT_LEGACY_MAP,
)

from pathlib import Path
import multiprocessing

workspace_path = Path("/workspace/some/experiment")
trace_path = Path("/traces/")

run_min = 94
run_max = 94
n_processes = 4

pad_params = PadParameters(
    pad_geometry_path=DEFAULT_MAP,
    pad_time_path=DEFAULT_MAP,
    pad_electronics_path=DEFAULT_MAP,
    pad_scale_path=DEFAULT_MAP,
)

get_params = GetParameters(
    baseline_window_scale=20.0,
    peak_separation=50.0,
    peak_prominence=20.0,
    peak_max_width=50.0,
    peak_threshold=40.0,
)

frib_params = FribParameters(
    baseline_window_scale=100.0,
    peak_separation=50.0,
    peak_prominence=20.0,
    peak_max_width=500.0,
    peak_threshold=100.0,
    ic_delay_time_bucket=1100,
    ic_multiplicity=1,
    correct_ic_time=True,
)

det_params = DetectorParameters(
    magnetic_field=2.85,
    electric_field=45000.0,
    detector_length=1000.0,
    beam_region_radius=25.0,
    micromegas_time_bucket=10.0,
    window_time_bucket=560.0,
    get_frequency=6.25,
    garfield_file_path=Path("./corrections/garfield.txt"),
    do_garfield_correction=False,
)

cluster_params = ClusterParameters(
    min_cloud_size=50,
    min_points=3,
    min_size_scale_factor=0.05,
    min_size_lower_cutoff=10,
    cluster_selection_epsilon=10.0,
    min_cluster_size_join=15,
    circle_overlap_ratio=0.25,
    outlier_scale_factor=0.05,
)

estimate_params = EstimateParameters(
    min_total_trajectory_points=30, smoothing_factor=100.0
)

solver_params = SolverParameters(
    gas_data_path=Path("./gases/data.json"),
    particle_id_filename=Path("./pids/id.json"),
    ic_min_val=900.0,
    ic_max_val=1350.0,
    n_time_steps=1000,
    interp_ke_min=0.1,
    interp_ke_max=70.0,
    interp_ke_bins=350,
    interp_polar_min=2.0,
    interp_polar_max=88.0,
    interp_polar_bins=166,
    fit_vertex_rho=True,
    fit_vertex_phi=True,
    fit_azimuthal=True,
)

pipe = Pipeline(
    [
        PointcloudPhase(
            get_params,
            frib_params,
            det_params,
            pad_params,
        ),
        ClusterPhase(cluster_params, det_params),
        EstimationPhase(estimate_params, det_params),
        InterpLeastSqSolverPhase(solver_params, det_params),
    ],
    [True, True, True, True],
    workspace_path,
    trace_path,
)


def main():
    start_pipeline(pipe, run_min, run_max, n_processes)


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")
    main()
