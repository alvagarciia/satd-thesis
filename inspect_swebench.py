from datasets import load_dataset
import pandas as pd

# Load SWE-bench Lite test split (300 instances)
ds = load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
df = ds.to_pandas()

# Group by repo and pick one base_commit per repo to inspect
summary = df.groupby("repo").agg(
    instance_count=("instance_id", "count"),
    sample_commit=("base_commit", "first")
).reset_index()

print(summary.to_string(index=False))
summary.to_csv("swebench_repos.csv", index=False)