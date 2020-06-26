import pandas as pd
from azureml.core import Run
from fire import Fire
from random import random


def process(data_dir, run_timestamp, input_filename):

    output_filename = f"data_{run_timestamp}.parquet"

    run = Run.get_context()

    run.add_properties(
        {
            "input_filename": input_filename,
            "run_timestamp": run_timestamp,
            "output_filename": output_filename,
        }
    )

    run.log("my_metric", random())

    df = pd.read_excel(f"{data_dir}/{input_filename}")

    print(df)

    # Everything in the directory './outputs' is automatically uploaded to the Azure ML workspace after the Run finished
    df.to_parquet(f"outputs/{output_filename}")


if __name__ == "__main__":
    Fire(process)
