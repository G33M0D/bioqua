# ============================================================
# BIOQUA: AI-Assisted Water Quality Monitoring System
#
# Authors         : Agreda, G.M., Joven, C.L., Mendez, A.V., Tangao, W., Zamora, G.D.
# Year            : 2026
# License         : MIT License
#
# This project is the original work of the authors.
# Unauthorized removal of this notice is prohibited.
# ============================================================

"""
Learning Module 5: Risk Assessment (Phase IV Gated Fusion)
===========================================================
Interactive walkthrough of how BIOQUA combines Phase II (bacteria class)
with Phase III (chemical condition) using Table 2.3 of the paper to land
on one of five Phase IV risk levels. Sources the real table from config.py
so this module always matches the production logic.
"""

import os
import sys

# Make the root-level python/ package importable so we can load the real tables
_HERE = os.path.dirname(os.path.abspath(__file__))
_PYTHON_DIR = os.path.join(os.path.dirname(_HERE), "python")
sys.path.insert(0, _PYTHON_DIR)

from config import (  # noqa: E402
    BACTERIA_CLASSES,
    CHEMICAL_SEVERE,
    CHEMICAL_MODERATE,
    CHEMICAL_STABLE,
    GATED_FUSION_TABLE,
    GATED_FUSION_FALLBACK,
    EC_SPIKE_HIGH,
    EC_SPIKE_MODERATE,
    PH_DROP_THRESHOLD,
    PH_NORMAL_MIN,
    PH_NORMAL_MAX,
    RISK_SHORT_CODE,
)


def print_header(title):
    width = 64
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width + "\n")


def print_subheader(title):
    print(f"\n--- {title} ---\n")


def pause():
    input("  [Press Enter to continue...]\n")


def introduction():
    print_header("RISK ASSESSMENT: The Gated Fusion Logic (Phase IV)")
    print("""  BIOQUA's four-phase methodology ends with a decision step:
  Phase II says WHAT kind of bacteria was detected, Phase III
  says WHAT the chemistry looks like, and Phase IV combines
  the two using a lookup table — called gated fusion.

  Why "gated"? Because each risk verdict is gated by BOTH
  dimensions at once. Gram-negative rods alone is bad news.
  A high TDS spike alone is bad news. But the same gram-negative
  rods with STABLE water chemistry is interpreted differently
  than the same bacteria with a pH-dropping contamination event.

  This module walks you through Table 2.3 of the research paper
  (docs/Phase.pdf) and lets you explore the same decision table
  that the production controller uses.
""")
    pause()


def explain_tables():
    print_header("THE THREE TABLES")
    print("""  Table 2.1 — Phase II Classifications (6 bacteria types)
  --------------------------------------------------------""")
    for name in BACTERIA_CLASSES:
        print(f"    - {name}")

    print("""
  Table 2.2 — Phase III Classifications (3 chemical conditions)
  --------------------------------------------------------------
    - Severe   : High TDS spike + pH drop
    - Moderate : Moderate TDS increase (or pH outside normal)
    - Stable   : No TDS spike and normal pH

  Thresholds the controller uses:""")
    print(f"    EC_SPIKE_HIGH      = {EC_SPIKE_HIGH} uS/cm")
    print(f"    EC_SPIKE_MODERATE  = {EC_SPIKE_MODERATE} uS/cm")
    print(f"    pH drop cutoff     = < {PH_DROP_THRESHOLD}")
    print(f"    pH normal range    = {PH_NORMAL_MIN} – {PH_NORMAL_MAX}")

    print("""
  Table 2.3 — Phase IV Risk Assessment (5 levels)
  ------------------------------------------------
    1. Low-Risk Contamination          (LOW)
    2. Moderate Biological Risk        (MOD-BIO)
    3. Moderate Risk                   (MOD)
    4. Moderate-High Risk              (MOD-HIGH)
    5. High-Risk Contamination         (HIGH)

  Plus a pseudo-level BIOQUA adds for "no bacteria + stable chemistry":
    0. Safe                            (SAFE)
""")
    pause()


def classify_chemistry(ph, ec):
    """Mirror of controller.derive_chemical_condition — kept local to avoid
    a circular import in the learning module."""
    if ec >= EC_SPIKE_HIGH and ph < PH_DROP_THRESHOLD:
        return CHEMICAL_SEVERE
    if ec >= EC_SPIKE_MODERATE or ph < PH_NORMAL_MIN or ph > PH_NORMAL_MAX:
        return CHEMICAL_MODERATE
    return CHEMICAL_STABLE


def lookup(bacteria, chemistry):
    """Return (risk_level, interpretation) from the table, applying the
    Gram-positive-cocci fallback if needed."""
    bacteria = GATED_FUSION_FALLBACK.get(bacteria, bacteria)
    return GATED_FUSION_TABLE.get((bacteria, chemistry), (None, None))


def preset_scenarios():
    print_header("PRESET SCENARIOS: The Table in Action")

    scenarios = [
        ("Clean tap water",          7.2,  350,  None),
        ("River with Gram-neg rods", 7.0,  400,  "Gram-negative rods"),
        ("Flood + E.coli-like",      6.0,  2800, "Gram-negative rods"),
        ("Mild pollution + cocci",   6.4,  1700, "Gram-positive cocci (clusters)"),
        ("Clear well + strep",       7.1,  450,  "Gram-positive cocci (chains)"),
        ("Sewage + enterococcus",    5.8,  3200, "Gram-negative cocci"),
    ]

    for name, ph, ec, bac in scenarios:
        chem = classify_chemistry(ph, ec)
        if bac is None:
            verdict = "Safe" if chem == CHEMICAL_STABLE else "Chemistry-only risk"
            interp = "No bacteria detected"
        else:
            level, interp = lookup(bac, chem)
            verdict = level or "Unrecognized bacteria class"

        print(f"  {name}")
        print(f"    pH={ph}  EC={ec}  Phase II={bac or '—'}")
        print(f"    Phase III: {chem}")
        print(f"    Phase IV:  {verdict}")
        print(f"      {interp}")
        print()

    pause()


def interactive_calculator():
    print_header("INTERACTIVE GATED FUSION CALCULATOR")
    print("  Enter pH, EC, and a bacteria class — BIOQUA will show you")
    print("  the exact Table 2.3 row that triggers, plus the resulting")
    print("  risk level. Type 'quit' at any prompt to move on.\n")

    # Build the selectable bacteria list — include "none" for chemistry-only cases
    selectable = ["(none detected)"] + BACTERIA_CLASSES

    while True:
        print_subheader("NEW WATER SAMPLE")

        try:
            ph_raw = input("  pH (0–14): ").strip()
            if ph_raw.lower() == "quit":
                return
            ph = float(ph_raw)
        except ValueError:
            print("  Please enter a number.\n")
            continue

        try:
            ec_raw = input("  EC in uS/cm (0–10000): ").strip()
            if ec_raw.lower() == "quit":
                return
            ec = float(ec_raw)
        except ValueError:
            print("  Please enter a number.\n")
            continue

        print("\n  Bacteria class:")
        for i, name in enumerate(selectable, 1):
            print(f"    {i}. {name}")
        try:
            bac_raw = input("\n  Pick a number: ").strip()
            if bac_raw.lower() == "quit":
                return
            bac_idx = int(bac_raw) - 1
            if bac_idx < 0 or bac_idx >= len(selectable):
                print("  Out of range.\n")
                continue
            bacteria = None if bac_idx == 0 else selectable[bac_idx]
        except ValueError:
            print("  Please enter a number.\n")
            continue

        chem = classify_chemistry(ph, ec)

        print("\n  Phase II (bacteria):    ", bacteria or "none detected")
        print("  Phase III (chemistry):  ", chem)

        if bacteria is None:
            if chem == CHEMICAL_STABLE:
                level = "Safe"
                interp = "No bacteria detected and chemistry within safe bounds"
            elif chem == CHEMICAL_MODERATE:
                level = "Moderate Risk"
                interp = "Developing chemical pollution with no bacteria detected"
            else:
                level = "High-Risk Contamination"
                interp = "Severe chemical pollution with no bacteria detected"
        else:
            level, interp = lookup(bacteria, chem)
            if level is None:
                level = "Unknown"
                interp = "No matching row in Table 2.3"

        short = RISK_SHORT_CODE.get(level, "?")
        print(f"  Phase IV (risk):        {level}  (LCD shows: {short})")
        print(f"    {interp}\n")

        again = input("  Test another sample? (y/n): ").strip().lower()
        if again != "y":
            return


def quiz():
    print_header("QUIZ (4 questions)")

    score = 0

    print("  Q1. Which phase combines bacteria class with chemistry?")
    print("    A) Phase I   B) Phase II   C) Phase III   D) Phase IV")
    if input("\n  Your answer: ").strip().upper() == "D":
        print("  Correct — Phase IV is the gated fusion step.\n")
        score += 1
    else:
        print("  Answer is D. Phase IV is the fusion step.\n")

    print("  Q2. Gram-negative rods + Stable chemistry = ?")
    print("    A) Low-Risk Contamination")
    print("    B) Moderate Biological Risk")
    print("    C) High-Risk Contamination")
    print("    D) Safe")
    if input("\n  Your answer: ").strip().upper() == "B":
        print("  Correct — Table 2.3: bacteria detected but chemistry is fine.\n")
        score += 1
    else:
        print("  Answer is B. Bacteria alone without chemistry spike = Moderate Biological Risk.\n")

    print("  Q3. What single chemistry signature is treated as SEVERE?")
    print("    A) High TDS spike alone")
    print("    B) pH drop alone")
    print("    C) High TDS spike AND pH drop together")
    print("    D) Any pH outside 6.5–8.5")
    if input("\n  Your answer: ").strip().upper() == "C":
        print("  Correct — both signals together is the Severe row of Table 2.2.\n")
        score += 1
    else:
        print("  Answer is C. Table 2.2 requires both signals for Severe.\n")

    print("  Q4. The LCD shows 'Risk: MOD-HIGH'. Which combination produced it?")
    print("    A) Gram-positive rods + Stable water")
    print("    B) Gram-negative rods + Moderate TDS")
    print("    C) No bacteria + Stable water")
    print("    D) Gram-positive cocci (clusters) + Moderate TDS")
    if input("\n  Your answer: ").strip().upper() == "B":
        print("  Correct — Moderate-High Risk only comes from Gram-negative bacteria\n"
              "  crossed with Moderate chemistry per Table 2.3.\n")
        score += 1
    else:
        print("  Answer is B. Moderate-High is reserved for Gram-negative × Moderate.\n")

    return score


def main():
    print("\n" + "*" * 64)
    print("  BIOQUA LEARNING MODULE 5")
    print("  Risk Assessment: Phase IV Gated Fusion")
    print("*" * 64)
    pause()

    introduction()
    explain_tables()
    preset_scenarios()

    print_header("YOUR TURN")
    interactive_calculator()

    score = quiz()

    print_header("MODULE COMPLETE")
    print(f"  You scored {score}/4.")
    if score == 4:
        print("  Perfect — you now read Table 2.3 the same way the controller does.")
    elif score >= 2:
        print("  Good — revisit the preset scenarios if any rows surprised you.")
    else:
        print("  Re-read docs/Phase.pdf §A.2.4 and run this module again.")
    print()


if __name__ == "__main__":
    main()
