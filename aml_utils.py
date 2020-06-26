from azureml.core import Workspace
from azureml.core.authentication import InteractiveLoginAuthentication
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.core.compute_target import ComputeTargetException


def get_workspace(config):
    if "tenant_id" in config:
        # This part is only required, if you have access to multiple tenants (=Azure Active Directories), which is probably not the case.
        interactive_auth = InteractiveLoginAuthentication(tenant_id=config["tenant_id"])
        ws = Workspace.from_config(auth=interactive_auth)
    else:
        # This should suffice in the typical case.
        ws = Workspace.from_config()
    return ws


def get_or_create_compute(
    workspace: Workspace,
    compute_name: str,
    vm_size: str,
    min_nodes: int,
    max_nodes: int,
) -> ComputeTarget:
    try:
        return ComputeTarget(workspace=workspace, name=compute_name)
    except ComputeTargetException:
        compute_target = ComputeTarget.create(
            workspace,
            compute_name,
            AmlCompute.provisioning_configuration(
                vm_size=vm_size,
                vm_priority="lowpriority",
                min_nodes=min_nodes,
                max_nodes=max_nodes,
            ),
        )
        compute_target.wait_for_completion(show_output=True)
        return compute_target
