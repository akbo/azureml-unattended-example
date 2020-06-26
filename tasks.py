import os
from pprint import pprint

from azureml.core import Experiment
from azureml.core.compute import AmlCompute
from invoke import task
from tabulate import tabulate

from aml_utils import get_workspace
from config import unattended_experiments_example_config as config


@task
def clean(c):
    c.run("rm -rf __pycache__")
    c.run("rm -rf joblib")

    for f in os.listdir("outputs"):
        if f != ".git_keep":
            c.run(f"rm outputs/{f}")

    c.run("rm -rf logs/azureml")
    c.run("rm -rf azureml-logs")


@task
def clean_azml_workspace(ctx):
    """
    [WARNING] Only use in test-only workspace. Remove or disable all compute clusters from Azure ML workspace.
    """

    ws = get_workspace(config)

    # remove compute clusters
    for _, compute in ws.compute_targets.items():
        if not compute.provisioning_state == "Deleting":
            print(f"Deleting {compute.name}")
            compute.delete()


@task
def show_available_vm_sizes(ctx):
    """
    Show, which VM Sizes are available in the workspace's Azure region
    """

    ws = get_workspace(config)

    pprint(AmlCompute.supported_vmsizes(workspace=ws))

    print(
        "\n>>> For VM prices, see https://azure.microsoft.com/en-us/pricing/details/virtual-machines/linux/ <<<\n"
    )


@task
def show_git_versions(ctx):
    """
    List all experiment runs and their git version
    """

    ws = get_workspace(config)

    exp = Experiment(ws, config["experiment_name"])

    versions = [
        (run.id, run.get_properties()["azureml.git.commit"]) for run in exp.get_runs()
    ]

    print(tabulate(versions, headers=["Run ID", "Git Version"]))
