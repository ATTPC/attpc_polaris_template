# attpc_polaris_template

This is a template codespace for using the [attpc_spyral](https://github.com/ATTPC/Spyral) analysis framework on Polaris, the supercomputer at the ALCF at ANL. It serves as a location from which one can supply the appropriate configuration controls and contains a script which can create a PBS job script and submit the script to PBS to run the analysis through an installed Docker (actually apptainer) image which contains attpc_spyral.

This template can be used in practice, or it can be used simply as a guide for how to setup a codespace to use attpc_spyral at Polaris.

## The Setup

This template comes with a bunch of preloaded examples and directories to demonstrate how to run a Spyral job on Polaris. We'll start at the top with the file `spyral_job.py`. This is the main script *you* will actually run when you want to use Spyral on Polaris. `spyral_job.py` does two things:

- Create a PBS script describing the job you want to run, including invoking the image containing the attpc_spyral install
- Submit the PBS script to the PBS system

This makes it so that you don't really need to know very much about how PBS and Polaris work to run Spyral (you should still [read](https://docs.alcf.anl.gov/polaris/getting-started/) up on it though). To use `spyral_job.py`, you need to do a couple of things. First is you need to load the Polaris Python module. This is done by running the following commands

```bash
module use /soft/modulefiles; module load conda; conda activate base
```

This will load up the default Polaris conda environment. `spyral_job.py` only depends on having Python 3.8+, so you can then simply run the script as 

```bash
python spyral_job.py COMMAND CONFIG
```

You should replace `COMMAND` with one of the following commands

- help - prints the help message
- create - creates a job script
- submit - submits a job script to the requested queue (if the script does not exist it is created)

and you should replace `CONFIG` with the path to a JSON configuration file. An example is given to you in the `configs` directory of the template. See the Job Configuration Parameters section for more details.

The other directories are for storing common Spyral data files, such as gas definitions, particle IDs, and for defining extensions. An example Spyral script is also included, `example_spyral_script.py`. There are a few differences from the normal scripts that are important, mostly with regard to paths. Looking at the top of the file you'll see

```python
workspace_path = Path("/workspace/")
trace_path = Path("/traces/")
```

Normally these would point to the location on your disk for both the Spyral workspace and the path to the raw traces. But when running Spryal from the image, we have to rebind these locations. The trace directory is bound to `/traces` in the container and your workspace is bound to `/workspace`. This means that you do *not* need to change these if you change workspaces or traces. You should change the corresponding paths in your PBS script, and they will be bound to the same places in the container. The next points of interest are passing the extra data files to Spyral like

```python
particle_id_filename=Path("/app/pids/example.json"),
```

This is very similar to traces and workspaces. To run your code within the container, you need to bind the codespace to the container as well! The `spyral_job` script binds the current working directory (wherever you ran the script from) to the location `/app` in the container. In the template this means that to load the example PID, you need to reference the location `/app/pids/example.json` from your script.

Hopefully this all is clear, but as a simple guide remember that to your code this is how the locations are mapped inside the container:

- Trace data -> `/traces`
- Workspace -> `/workspace`
- Your codespace -> `/app`


## Job Configuration Parameters

```json
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
```