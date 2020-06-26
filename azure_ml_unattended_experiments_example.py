import os
from datetime import datetime

from fire import Fire
from azureml.core import Dataset, Environment, Experiment, ScriptRunConfig

from aml_utils import get_or_create_compute, get_workspace
from config import unattended_experiments_example_config as config


def run_experiment(input_fpath, run_locally=False):

    run_timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")

    ws = get_workspace(config)

    # Upload data to the default file storage of the Azure ML workspace - note that the data has a version in its filename
    datastore = ws.get_default_datastore()
    datastore.upload_files(
        files=[input_fpath],
        target_path=config["data"]["cloud_data_dir"],
        overwrite=False,
        show_progress=True,
    )

    # Create a reference to the uploaded data, which can be referenced from within the compute job
    dataset = Dataset.File.from_files(
        path=[(datastore, config["data"]["cloud_data_dir"])]
    )

    # Declare the Python dependencies required to run the code
    environment = Environment.from_conda_specification(
        name=config["environment_name"], file_path="environment.yml"
    )

    # Use Docker instead of running directly on machine. When running locally, this keeps the machine clean of temporary conda environments and data. Azure ML Compute Clusters don't support non-Docker runs.
    environment.docker.enabled = True

    # Specify the name of the "experiment", in which the runs will be tracked in the Azure ML workspace
    experiment = Experiment(workspace=ws, name=config["experiment_name"])

    # Specify, what should be run
    runconfig = ScriptRunConfig(
        source_directory="src",  # The whole directory will be uploaded to the workspace and kept as a "Snapshot" for the Run
        script="script.py",  # This file (that resides in the above directory) will be run
        arguments=[
            dataset.as_named_input(
                config["data"]["script_input_name"]
            ).as_download(),  # The dataset will be downloaded to the compute target and made available to the code
            run_timestamp,
            input_fpath.split("/")[-1],
        ],
    )
    runconfig.run_config.environment = environment

    # Set compute target
    if run_locally:
        runconfig.run_config.target = "local"  # local means your laptop
    else:
        # Create compute cluster to run code on (or get reference if it already exists)
        compute_target = get_or_create_compute(ws, **config["compute"])

        runconfig.run_config.target = compute_target

    # Run the exeriment
    run = experiment.submit(config=runconfig)
    run.wait_for_completion(show_output=True)

    # Get logs and output files
    run.download_files()


if __name__ == "__main__":
    Fire(run_experiment)
