unattended_experiments_example_config = {
    "compute": {
        "vm_size": "Standard_D1_v2",
        "compute_name": "ML-UNATT-EXP-TST",
        "min_nodes": 0,
        "max_nodes": 1,
    },
    "data": {"cloud_data_dir": "my_project_name", "script_input_name": "my_data",},
    "environment_name": "my_project_environment",
    "experiment_name": "my-unattended-experiment",
}
