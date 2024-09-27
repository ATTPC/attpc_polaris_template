# attpc_polaris_template

This is a template codespace for using the [attpc_spyral](https://github.com/ATTPC/Spyral) analysis framework on Polaris, the supercomputer at the ALCF at ANL. It serves as a location from which one can supply the appropriate configuration controls and contains a script which can create a PBS job script and submit the script to PBS to run the analysis.

This template can be used in practice, or it can be used simply as a guide for how to setup a codespace to use attpc_spyral at Polaris.

## The Setup

This template comes with a bunch of preloaded examples and directories to demonstrate how to run a Spyral job on Polaris. But first, you need to install Spyral and the Dragon libraries to make Spyral node aware. This can be done with the scripts in the `bin` directory. If it is your first time using Spyral, run

```bash
source ./bin/create_spyral_env.sh
```

This will load the appropriate Polaris modules, create a virtual environment, install Spryal and Dragon, and activate the environment. Note that the path to Dragon must be specified in the `.env` file in the repository using the `DRAGON_PATH` variable.

If you are returning to the codespace, you can use

```bash
source ./bin/activate_spyral_env.sh
```

which will activate the modules and environment. Finally, to deactivate the environment you can use

```bash
source ./bin/deactivate_spyral_env.sh
```

which will deactivate the environment.

## Creating and Submitting a Job Script

We'll start at the top with the file `spyral_job.py`. This is the main script you will actually run when you want to use Spyral on Polaris. `spyral_job.py` does two things:

- Create a PBS script describing the job you want to run, including invoking the image containing the attpc_spyral install
- Submit the PBS script to the PBS system

This makes it so that you don't really need to know very much about how PBS and Polaris work to run Spyral (you should still [read](https://docs.alcf.anl.gov/polaris/getting-started/) up on it though). To use `spyral_job.py`, you need to make sure you have your environment [active](#the-setup). You can then simply run the script as

```bash
python spyral_job.py COMMAND CONFIG
```

You should replace `COMMAND` with one of the following commands

- help - prints the help message
- create - creates a job script
- submit - submits a job script to the requested queue (if the script does not exist it is created)

and you should replace `CONFIG` with the path to a JSON configuration file. An example is given to you in the `configs` directory of the template. See the Job Configuration Parameters section for more details.

The other directories are for storing common Spyral data files, such as gas definitions, particle IDs, and for defining extensions. An example Spyral script is also included, `example_spyral_script.py`. There are a few differences from the normal scripts that are important, mostly for working with Dragon. First notice at the top of the script

```python
import dragon
```

This is critical. Dragon *must* be imported first. Then, at the bottom

```python
if __name__ == "__main__":
    multiprocessing.set_start_method("dragon")
    main()
```

Using `multiprocessing.set_start_method("dragon")` sets Dragon as the method by which we start new processes. Both of these are critical for correctly using Spyral with Dragon!

## Job Configuration Parameters

Here we'll go over the available configuration parameters for jobs with Spyral

- `pbs_script_path`: The path to where you want to store the created PBS job script
- `spyral_start_script`: The script to be run by Spyral. It should exist at the same location as `spyral_job.py`.
- `log_path`: The location at which you would like PBS logs to be written
- `job_name`: The name of this job in PBS
- `queue`: The queue you would like to submit the job to. See the Polaris [docs](https://docs.alcf.anl.gov/polaris/running-jobs/)
- `nodes`: The number of vnodes to use. See Polaris [docs](https://docs.alcf.anl.gov/running-jobs/job-and-queue-scheduling/)
- `walltime`: How long the job is allowed to run in units of minutes. See Polaris [docs](https://docs.alcf.anl.gov/running-jobs/job-and-queue-scheduling/)

```json
{
    "pbs_script_path": "/some/path/somewhere.pbs",
    "spyral_start_script": "some_script.py",
    "log_path": "/some/path/somewhere/",
    "project_name": "attpc",
    "queue": "debug",
    "nodes": 1,
    "walltime": 60
}
```

## Setting the `.env` file

By default the `.env` file looks like

```bash
DRAGON_DIR=/Path/to/some/Dragon

OMP_NUM_THREADS=1
OPENBLAS_NUM_THREADS=1
MKL_NUM_THREADS=1
VECLIB_MAXIMUM_THREADS=1
NUMEXPR_NUM_THREADS=1
POLARS_MAX_THREADS=1
```

In general, the only path you need to modify is the `DRAGON_DIR`. This should be set to the location of the Dragon installation for your project, and is used to create the correct virtual environment when setting up. The other variables most likely do not need modification.
