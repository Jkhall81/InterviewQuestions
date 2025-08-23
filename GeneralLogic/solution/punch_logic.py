import json
import re
from datetime import datetime
from pathlib import Path


def load_jsonc(filepath):
    """Read jsonc, strip comments, and return a dictionary"""
    with open(filepath, "r") as f:
        content = f.read()
    content = re.sub(r"/\*[\s\S]*?\*/|//.*", "", content)
    return json.loads(content)


def calculate_results(data):
    """Calculate payroll results from parsed JSON data."""
    job_rates = {j["job"]: (j["rate"], j["benefitsRate"]) for j in data["jobMeta"]}

    def hours_diff(start, end):
        format = "%Y-%m-%d %H:%M:%S"
        return (datetime.strptime(end, format) - datetime.strptime(start, format)).total_seconds() / 3600

    results = {}

    for emp in data["employeeData"]:
        employee = emp["employee"]
        punches = emp["timePunch"]

        total_hours = 0
        reg_hours = ot_hours = dt_hours = 0
        wage_total = benefit_total = 0

        for punch in punches:
            job = punch["job"]
            rate, ben_rate = job_rates[job]
            hrs = hours_diff(punch["start"], punch["end"])

            while hrs > 0:
                if total_hours < 40:
                    available = 40 - total_hours
                    use = min(hrs, available)
                    reg_hours += use
                    wage_total += use * rate
                    benefit_total += use * ben_rate
                    hrs -= use
                    total_hours += use
                elif total_hours < 48:
                    available = 48 - total_hours
                    use = min(hrs, available)
                    ot_hours += use
                    wage_total += use * rate * 1.5
                    benefit_total += use * ben_rate
                    hrs -= use
                    total_hours += use
                else:
                    dt_hours += hrs
                    wage_total += hrs * rate * 2
                    benefit_total += hrs * ben_rate
                    total_hours += hrs
                    hrs = 0

        results[employee] = {
            "employee": employee,
            "regular": f"{reg_hours:.4f}",
            "overtime": f"{ot_hours:.4f}",
            "doubletime": f"{dt_hours:.4f}",
            "wageTotal": f"{wage_total:.4f}",
            "benefitTotal": f"{benefit_total:.4f}",
        }
    return results


if __name__ == "__main__":
    # Doing this instead of a relative path in a string, to make sure this runs correctly wherever its used
    file_path = Path(__file__).parent.parent / "PunchLogicTest.jsonc"
    data = load_jsonc(file_path)
    results = calculate_results(data)

    print(json.dumps(results, indent=2))

    out_file = Path(__file__).parent / "results.json"
    with open(out_file, "w") as out:
        json.dump(results, out, indent=2)
