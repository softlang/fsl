from pathlib import Path
import csv

log_dir = "."
log_files = [
    "instances",
    "used_instances",
    "unused_instances",
    "instance_properties",
    "subclasses",
    "used_subclasses",
    "unused_subclasses",
    "subclass_properties"
    ]

with open("summary.csv", "w", newline="", encoding="utf-8") as out:
    writer = csv.writer(out)
    writer.writerow(["Metric", "Count"])

    for stem in log_files:
        path = Path(log_dir + "/" + stem + ".log")

        with path.open("r", encoding="utf-8", errors="replace") as f:
            line_count = sum(1 for _ in f)

        writer.writerow([stem, line_count])
