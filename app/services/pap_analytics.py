import datetime
from typing import Optional, List

# Define age categories and expected cell types for each category
age_categories = {
    "newborn": {"range": (0, 7), "expected_cells": ["predominantly intermediate", "few superficial"]},
    "early_childhood": {"range": (8, 8 * 365), "expected_cells": ["parabasal"]},
    "puberty": {"range": (8 * 365 + 1, 13 * 365), "expected_cells": ["predominantly intermediate", "few superficial"]},
    "reproductive": {"range": (14 * 365, 45 * 365), "expected_cells": {"menstrual_phase": {
        "menstrual": ["intermediate", "superficial", "endometrial"],
        "proliferative": ["predominantly intermediate"],
        "secretory": ["predominantly intermediate"]
    }}},
    "postmenopausal": {"range": (45 * 365 + 1, float('inf')), "expected_cells": ["glandular"]},
    "postpartum_lactation": {"expected_cells": ["similar to pregnancy"]},
    "pregnancy": {"expected_cells": ["superficial", "intermediate", "parabasal"]}
}

# Non-MI Cell thresholds for analysis
non_mi_thresholds = {
    "SM": 20,  # Squamous Metaplastic Cells threshold (% of total)
    "KC": 5,   # Koilocytes threshold (% of total)
    "EC": 1,   # Endocervical Cells threshold (% of total for postmenopausal)
    "EM": 1,   # Endometrial Cells threshold (% of total for age >= 45)
    "AC": 2    # Actinomyces threshold (% of total)
}

# Contraceptive and hormone therapy descriptions
hormone_descriptions = {
    "progesterone": "Progesterone may increase intermediate cells.",
    "estrogen": "Estrogen may increase superficial cells.",
    "androgen": "Androgen can reduce the presence of superficial cells."
}

# Helper function to classify age into categories
def classify_age(age_in_days):
    if age_in_days <= 7:
        return "newborn"
    elif 8 <= age_in_days <= 8 * 365:
        return "early_childhood"
    elif 8 * 365 < age_in_days <= 13 * 365:
        return "puberty"
    elif 14 * 365 <= age_in_days <= 45 * 365:
        return "reproductive"
    elif age_in_days > 45 * 365:
        return "postmenopausal"
    return None

# Phase calculation based on LMP, applies only to reproductive category
def calculate_phase(lmp_date, cycle_length=28):
    days_since_lmp = (datetime.date.today() - lmp_date).days % cycle_length
    if 1 <= days_since_lmp <= 5:
        return "menstrual"
    elif 6 <= days_since_lmp <= (cycle_length // 2):
        return "proliferative"
    elif (cycle_length // 2) < days_since_lmp <= cycle_length:
        return "secretory"
    return "unknown"

# Calculate Maturation Index for MI cells (Parabasal, Intermediate, Superficial)
def calculate_mi(counts):
    total_mi_cells = counts["PC"] + counts["IC"] + counts["SC"]
    if total_mi_cells == 0:
        return None  # Avoid division by zero if no MI cells are found
    pc_percent = (counts["PC"] / total_mi_cells) * 100
    ic_percent = (counts["IC"] / total_mi_cells) * 100
    sc_percent = (counts["SC"] / total_mi_cells) * 100
    return {"PC": pc_percent, "IC": ic_percent, "SC": sc_percent}

# Analyze non-MI cells and flag based on thresholds
def analyze_non_mi_cells(counts, total_cells, age_in_days):
    analysis = {}
    iud_diagnosis = None
    
    for cell_type, threshold in non_mi_thresholds.items():
        count = counts.get(cell_type, 0)
        percent = (count / total_cells) * 100 if total_cells > 0 else 0
        
        if cell_type == "AC" and percent > threshold:
            iud_diagnosis = "Actinomyces detected, suggesting IUD-related infection."
        
        if cell_type == "SM" and percent > threshold:
            analysis["SM"] = f"High squamous metaplastic cells: {percent:.2f}% (chronic inflammation/repair)"
        elif cell_type == "KC" and percent > threshold:
            analysis["KC"] = f"High koilocytes: {percent:.2f}% (HPV infection risk)"
        elif cell_type == "EC" and percent > threshold and age_in_days > 45 * 365:
            analysis["EC"] = f"High endocervical cells: {percent:.2f}% (may indicate glandular abnormalities)"
        elif cell_type == "EM" and percent > threshold and age_in_days >= 45 * 365:
            analysis["EM"] = f"High endometrial cells: {percent:.2f}% (evaluate for endometrial pathology)"
    
    return analysis, iud_diagnosis

# Determine expected cells based on age and phase (for non-pregnant patients)
def get_expected_cells(age_in_days, phase=None, condition=None):
    age_category = classify_age(age_in_days)

    # Handle special conditions like pregnancy or postpartum/lactation
    if condition == "pregnancy":
        return age_categories["pregnancy"]["expected_cells"]
    elif condition == "postpartum_lactation":
        return age_categories["postpartum_lactation"]["expected_cells"]

    # Get expected cells for regular age categories
    if age_category == "reproductive" and phase:
        return age_categories["reproductive"]["expected_cells"]["menstrual_phase"].get(phase, [])
    elif age_category in age_categories:
        return age_categories[age_category]["expected_cells"]
    return None


# Generate the final report
def generate_report(
    age_in_days: int,
    counts: dict,
    lmp_date=Optional[datetime.date],
    cycle_length=28,
    condition=Optional[str],
    contraceptives=Optional[str],
    hormone_therapy=Optional[str],
):
    total_cells = sum(counts.values())

    # Calculate menstrual phase for reproductive patients with LMP data
    phase = None
    if classify_age(age_in_days) == "reproductive" and lmp_date:
        phase = calculate_phase(lmp_date, cycle_length)

    # Calculate MI for non-pregnant patients
    if condition != "pregnancy":
        mi_result = calculate_mi(counts)
        mi_interpretation = f"MI: PC={mi_result['PC']:.2f}%, IC={mi_result['IC']:.2f}%, SC={mi_result['SC']:.2f}%" if mi_result else "No MI cells detected"
    else:
        mi_interpretation = "Pregnancy detected - age-based MI not applicable"

    # Analyze non-MI cells and check for IUD diagnosis
    non_mi_analysis, iud_diagnosis = analyze_non_mi_cells(counts, total_cells, age_in_days)

    # Expected cells based on age, phase, and conditions
    expected_cells = get_expected_cells(age_in_days, phase, condition)

    # Contraceptive and hormone therapy descriptions
    contraceptive_info = hormone_descriptions.get(contraceptives, "No specific hormone effect")
    hormone_therapy_info = hormone_descriptions.get(hormone_therapy, "No specific hormone effect")

    # Compile the report
    report = {
        "Age Category": classify_age(age_in_days),
        "Phase": phase if phase else "Not applicable",
        "Expected Cells": expected_cells,
        "Maturation Index (MI)": mi_interpretation,
        "Non-MI Cell Analysis": non_mi_analysis,
        "IUD Diagnosis": iud_diagnosis,
        "Contraceptive Impact": contraceptive_info,
        "Hormone Therapy Impact": hormone_therapy_info
    }
    return report
