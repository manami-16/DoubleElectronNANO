import yaml
import subprocess
from pathlib import Path
import csv
import re

# Path to your YAML configuration file
YAML_FILE = "runNum_era.yml"

# Optional: directory to store output CSVs
OUTPUT_DIR = Path("lumi_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Normtag path (as per your command)
NORMTAG = "/cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json"

def check_lumi_sum(csv_file):
    """Check that the sum of the last column (recorded/fb) matches the summary total."""
    total_recorded_sum = 0.0
    summary_recorded = None

    with open(csv_file, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Parse only lines that are not comments and contain commas
    data_lines = [line for line in lines if not line.startswith("#") and "," in line]

    if not data_lines:
        print("   ❌ No data rows found.")
        return

    # Sum the last column (recorded(/fb))
    for line in data_lines:
        parts = [p.strip() for p in line.split(",")]
        try:
            value = float(parts[-1])  # last column
            total_recorded_sum += value
        except ValueError:
            continue

    # Find the summary section
    for i, line in enumerate(lines):
        if line.startswith("#nfill,nrun,nls,ncms,totdelivered(/fb),totrecorded(/fb)"):
            # The next line should have the numeric summary
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                nums = re.findall(r"[-+]?\d*\.\d+|\d+", next_line)
                if len(nums) >= 6:
                    summary_recorded = float(nums[-1])
            break

    if summary_recorded is None:
        print("   ⚠️  Could not find proper summary line with 'totrecorded(/fb)'.")
        return

    # Compare values
    diff = abs(total_recorded_sum - summary_recorded)
    rel_diff = diff / summary_recorded if summary_recorded != 0 else 0

    print(f"   📊 Calculated recorded sum: {total_recorded_sum:.9f} /fb")
    print(f"   📄 Summary recorded value:  {summary_recorded:.9f} /fb")
    print(f"   🔍 Difference:              {diff:.9e} ({rel_diff:.3%})")

    if rel_diff < 1e-6:
        print("   ✅ Match (perfect or rounding-level).")
    elif rel_diff < 1e-4:
        print("   ⚠️ Small rounding difference (OK).")
    else:
        print("   ❌ Mismatch detected!")

def main():
    # Load YAML
    with open(YAML_FILE, "r") as f:
        config = yaml.safe_load(f)

    # Loop over each year and era
    for year, info in config.items():
        lumi_json = info.get("Lumi")
        eras = info.get("era", {})

        if not lumi_json:
            print(f"Skipping {year} — no Lumi JSON found.")
            continue

        for era, runs in eras.items():
            if not runs or len(runs) != 2:
                print(f"Skipping {year} {era} — invalid run range: {runs}")
                continue

            run_start, run_end = runs
            output_file = OUTPUT_DIR / f"{year}_{era}_lumi.csv"

            cmd = [
                "brilcalc", "lumi",
                "--normtag", NORMTAG,
                "-u", "/fb",
                "-i", lumi_json,
                "-o", str(output_file),
                "--begin", str(run_start),
                "--end", str(run_end)
            ]

            print("\nRunning:", " ".join(cmd))
            try:
                subprocess.run(cmd, check=True)
                print(f"✅ Output saved to: {output_file}")

                # Immediately check lumi sums
                print(f"Verifying lumi sums for {year} {era}...")
                check_lumi_sum(output_file)

            except subprocess.CalledProcessError as e:
                print(f"❌ Error running brilcalc for {year} {era}: {e}")


if __name__ == "__main__":
    main()