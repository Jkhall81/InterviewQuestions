import json
import re
from datetime import datetime
from pathlib import Path


def load_jsonc(filepath):
    """Read jsonc, strip comments, and return a dictionary."""
    with open(filepath, "r") as f:
        content = f.read()
    # re.sub(pattern, replacement, string being worked on)
    # need the r"" so we can use the escape '\'
    content = re.sub(r"/\*[\s\S]*?\*/|//.*", "", content)
    return json.loads(content)


def calculate_results(data):
    """Calculate payroll results from parsed JSON data, band-driven."""
    job_rates = {j["job"]: (j["rate"], j["benefitsRate"]) for j in data["jobMeta"]}

    def hours_diff(start, end):
        format = "%Y-%m-%d %H:%M:%S"
        return (datetime.strptime(end, format) - datetime.strptime(start, format)).total_seconds() / 3600

    # Define pay bands as (label, cutoff_hours, multiplier)
    PAY_BANDS = [
        ("regular", 40, 1),
        ("overtime", 48, 1.5),
        ("doubletime", None, 2),
    ]

    results = {}

    for emp in data["employeeData"]:
        employee = emp["employee"]
        punches = emp["timePunch"]

        # This and PAY_BANDS could be set up to be imported from JSON / a config file
        # I think in this case hardcoding it in the code is fine
        totals = {
            "regular": 0,
            "overtime": 0,
            "doubletime": 0,
            "wageTotal": 0,
            "benefitTotal": 0,
        }
        total_hours = 0

        for punch in punches:
            job = punch["job"]
            rate, ben_rate = job_rates[job]
            hrs = hours_diff(punch["start"], punch["end"])

            for label, cutoff, mult in PAY_BANDS:
                if hrs <= 0:
                    break
                # if cutoff is None, no limit (all remaining hrs go here)
                avail = hrs if cutoff is None else max(0, cutoff - total_hours)
                used = min(hrs, avail)
                if used > 0:
                    totals[label] += used
                    totals["wageTotal"] += used * rate * mult
                    totals["benefitTotal"] += used * ben_rate
                    hrs -= used
                    total_hours += used

        results[employee] = {
            "employee": employee,
            "regular": f"{totals['regular']:.4f}",
            "overtime": f"{totals['overtime']:.4f}",
            "doubletime": f"{totals['doubletime']:.4f}",
            "wageTotal": f"{totals['wageTotal']:.4f}",
            "benefitTotal": f"{totals['benefitTotal']:.4f}",
        }

    return results


if __name__ == "__main__":
    # Doing this instead of a relative path in a string, to make sure this runs correctly wherever its used
    file_path = Path(__file__).parent.parent / "PunchLogicTest.jsonc"
    data = load_jsonc(file_path)
    results = calculate_results(data)

    # without indent we get single line JSON, indent=2 gives us the pretty-printed version
    print(json.dumps(results, indent=2))

    out_file = Path(__file__).parent / "results.json"
    with open(out_file, "w") as out:
        json.dump(results, out, indent=2)
