#!/bin/python
from dataclasses import dataclass
from pathlib import Path
import json
import subprocess
from enum import Enum
import sys
import textwrap

CREATE_STRING = "create"
SUBMIT_STRING = "submit"


class SubCommand(Enum):
    CREATE = 1
    SUBMIT = 2
    HELP = -1

    @classmethod
    def from_string(cls, string: str):
        if string == CREATE_STRING:
            return SubCommand.CREATE
        elif string == SUBMIT_STRING:
            return SubCommand.SUBMIT
        else:
            return SubCommand.HELP


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

NODE_LIMITS = {
    "debug": (1, 2),
    "debug-scaling": (1, 10),
    "prod": (10, 496),
    "preemptable": (1, 10),
    "demand": (1, 56),
}

CPU_LIMIT = 32  # There are 32 physical cores per node
MEMORY_LIMIT = 256  # technically 512 GiB but for now...


@dataclass
class Config:
    pbs_script_path: Path
    spyral_start_script: Path
    spyral_workspace_path: Path
    spyral_trace_path: Path
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


def print_help() -> None:
    print(
        textwrap.dedent(
            """
            Usage:
            python submit_spyral_job.py COMMAND CONFIG

            A tool for creating PBS job scripts for AT-TPC Spyral analysis tasks and
            submitting them to the Polaris system at Argonne Natl. Lab

            Available COMMANDS
            create  Creates a job script
            submit  Submits the job script (if the script does not exist it is created)
            help    Displays this message

            CONFIG is the path to a JSON configuration file of the following format
            {
                "pbs_script_path": "/some/path/somewhere.pbs",
                "spyral_start_script": "/some/path/somewhere.py",
                "spyral_workspace_path": "/some/path/somewhere/",
                "spyral_trace_path": "/some/path/somewhere/",
                "container_path": "/some/path/somewhere.img",
                "log_path": "/some/path/somewhere/",
                "job_name": "spyral_job",
                "queue": "debug",
                "nodes": 1,
                "cpus_per_node": 32,
                "memory_per_node": 20,
                "walltime": 60
            }
            Memory is specified in GBs and Walltime is in minutes.
            """
        )
    )


def create_job_script(config: Config):
    with open(config.pbs_script_path, "w") as script:
        script.write(
            textwrap.dedent(
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

                apptainer -s exec --bind {config.spyral_workspace_path}:/workspace,{config.spyral_trace_path}:/traces {config.container_path} python {config.spyral_start_script}
                """
            )
        )


def load_job_config(config_path: Path) -> Config:
    with open(config_path, "r") as config_file:
        config_data = json.load(config_file)
        return Config(
            Path(config_data["pbs_script_path"]),
            Path(config_data["spyral_start_script"]),
            Path(config_data["spyral_workspace_path"]),
            Path(config_data["spyral_trace_path"]),
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


def main(config_path: Path, sub: SubCommand):
    if not config_path.exists():
        print(f"ERROR - Configuration {config_path} does not exist")
        return
    config = load_job_config(config_path)

    # Do some sanitization
    if config.pbs_script_path.exists():
        print(
            f"WARNING - PBS script {config.pbs_script_path} already exists and has been overwritten"
        )
    # Make the directory for the script if it does not exist
    config.pbs_script_path.parent.mkdir(exist_ok=True)

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

    queue_node_limits = NODE_LIMITS[config.queue]
    if config.nodes < queue_node_limits[0] or config.nodes > queue_node_limits[1]:
        print(
            f"ERROR - Nodes {config.nodes} exceeds node limits {queue_node_limits} (min, max)"
        )
        return

    if config.cpus_per_node > CPU_LIMIT:
        print(f"ERROR - CPUs {config.cpus_per_node} exceeds cpu limit {CPU_LIMIT}")
        return

    if config.memory_per_node > MEMORY_LIMIT:
        print(
            f"ERROR - Memory {config.memory_per_node} exceeds memory limit {MEMORY_LIMIT}"
        )
        return

    queue_wall_limits = WALL_LIMITS[config.queue]
    if config.walltime < queue_wall_limits[0] or config.walltime > queue_wall_limits[1]:
        print(
            f"ERROR - Walltime {config.walltime} mins is not in the valid range {queue_wall_limits} (min, max) for the selected queue {config.queue}"
        )
        return

    if not config.log_path.exists():
        config.log_path.mkdir(exist_ok=True)

    # Handle whatever command the user threw at us
    response = None
    match sub:
        case SubCommand.CREATE:
            create_job_script(config)
        case SubCommand.SUBMIT:
            if not config.pbs_script_path.exists():
                create_job_script(config)
            response = submit_pbs_job(config)
        case SubCommand.HELP:
            print_help()
            return
        case _:
            print("ERROR - Unrecognized sub command")
            print_help()
            return

    if response is not None:
        print(f"Job submitted with status code {response.returncode}")
        print(f"Stdout repsonse: {response.stdout}")
    else:
        print(f"Created PBS job script {config.pbs_script_path}")


if __name__ == "__main__":
    print("--------- Spyral-Polaris Job Tool ---------")
    if len(sys.argv) != 3:
        print(
            "ERROR - Requires two positional arguments, a command and a configuration file."
        )
        print_help()
    else:
        main(Path(sys.argv[2]), SubCommand.from_string(sys.argv[1]))
    print("-------------------------------------------")
