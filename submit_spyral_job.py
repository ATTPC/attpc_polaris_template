#!/bin/python
from dataclasses import dataclass
from pathlib import Path
import json
import subprocess

VALID_QUEUES = [
    "debug",
    "debug-scaling",
    "prod",
    "preemptable",
    "demand",
]

# min, max time in minutes per queue
WALL_LIMITS = {
    "debug": (5, 60),
    "debug-scaling": (5, 60),
    "prod": (5, 24 * 60),
    "preemptable": (5, 72 * 60),
    "demand": (5, 60),
}

NODE_LIMIT = 10  # technically like 500 something but for now...
CPU_LIMIT = 32  # There are 32 physical cores per node
MEMORY_LIMIT = 256  # technically 512 GiB but for now...


@dataclass
class Config:
    pbs_script_path: Path
    spyral_start_script: Path
    spyral_workspace_path: Path
    container_path: Path
    log_path: Path
    job_name: str
    queue: str
    nodes: int
    cpus_per_node: int
    memory_per_node: int
    walltime: int

    def walltime_str(self) -> str:
        hours, minutes = divmod(self.walltime, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:00"


def create_job_script(config: Config):
    with open(config.pbs_script_path, "w") as script:
        script.write(
            f"""
            #!/bin/bash -l

            #PBS -A {config.job_name}
            #PBS -q debug
            #PBS -l select={config.nodes}:system=polaris:ncpus={config.cpus_per_node}:mem={config.memory_per_node}gb
            #PBS -l filesystems=home:eagle
            #PBS -l place=scatter
            #PBS -k doe
            #PBS -j oe
            #PBS -o {config.log_path}
            #PBS -l walltime={config.walltime_str()}

            module use /soft/spack/gcc/0.6.1/install/modulefiles/Core
            module load apptainer

            apptainer -s exec --bind {config.spyral_workspace_path}:/workspace {config.container_path} python {config.spyral_start_script}
            """
        )


def load_job_config(config_path: Path) -> Config:
    with open(config_path, "r") as config_file:
        config_data = json.load(config_file)
        return Config(
            Path(config_data["pbs_script_path"]),
            Path(config_data["spyral_start_script"]),
            Path(config_data["spyral_workspace_path"]),
            Path(config_data["container_path"]),
            Path(config_data["log_path"]),
            config_data["job_name"],
            config_data["queue"],
            config_data["nodes"],
            config_data["cpus_per_node"],
            config_data["memory_per_node"],
            config_data["walltime"],
        )


def submit_pbs_job(config: Config) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["qsub", f"{config.pbs_script_path}"], capture_output=True, encoding="utf-8"
    )


def main(config_path: Path):
    config = load_job_config(config_path)

    # Do some sanitization
    if config.pbs_script_path.exists():
        print(
            f"WARNING - PBS script {config.pbs_script_path} already exists and has been overwritten"
        )

    if not config.spyral_start_script.exists():
        print(f"ERROR - Spyral script {config.spyral_start_script} does not exist.")
        return

    if not (
        config.spyral_workspace_path.exists() and config.spyral_workspace_path.is_dir()
    ):
        print(
            f"ERROR - Spyral workspace directory {config.spyral_workspace_path} does not exist or is not a directory."
        )
        return

    if not config.container_path.exists():
        print(f"ERROR - Container {config.container_path} does not exist.")
        return

    if config.queue not in VALID_QUEUES:
        print(
            f"ERROR - Queue {config.queue} is not a valid queue. Valid queues are {VALID_QUEUES}"
        )
        return

    if config.nodes > NODE_LIMIT:
        print(f"ERROR - Nodes {config.nodes} exceeds node limit {NODE_LIMIT}")
        return

    if config.cpus_per_node > CPU_LIMIT:
        print(f"ERROR - CPUs {config.cpus_per_node} exceeds cpu limit {CPU_LIMIT}")
        return

    if config.memory_per_node > MEMORY_LIMIT:
        print(
            f"ERROR - Memory {config.memory_per_node} exceeds memory limit {MEMORY_LIMIT}"
        )
        return

    queue_limits = WALL_LIMITS[config.queue]
    if config.walltime < queue_limits[0] or config.walltime > queue_limits[1]:
        print(
            f"ERROR - Walltime {config.walltime} mins is not in the valid range {queue_limits} (min, max) for the selected queue {config.queue}"
        )
        return

    if not config.log_path.exists():
        config.log_path.mkdir(exist_ok=True)

    # Create the actual PBS job script
    create_job_script(config)
