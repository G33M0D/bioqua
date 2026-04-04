# ============================================================
# AquaGuard: AI-Powered Bacteria Detection for Safe Drinking Water
#
# Original Author : Guillanne Marie Agreda
# Year            : 2026
# License         : MIT License
#
# This project is the original work of the author.
# Unauthorized removal of this notice is prohibited.
# ============================================================

"""
Learning Module 5: Risk Assessment
Interactive calculator that combines pH, EC, and bacteria type
to determine water safety risk level -- just like AquaGuard does.
"""


def print_header(title):
    width = 60
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width + "\n")


def print_subheader(title):
    print(f"\n--- {title} ---\n")


def pause():
    input("  [Press Enter to continue...]\n")


# Risk assessment constants
BACTERIA_RISK = {
    "e_coli":        {"name": "E. coli",           "base_risk": 90, "gram": "negative"},
    "vibrio":        {"name": "Vibrio cholerae",    "base_risk": 95, "gram": "negative"},
    "salmonella":    {"name": "Salmonella",         "base_risk": 85, "gram": "negative"},
    "shigella":      {"name": "Shigella",           "base_risk": 85, "gram": "negative"},
    "campylobacter": {"name": "Campylobacter",      "base_risk": 80, "gram": "negative"},
    "legionella":    {"name": "Legionella",         "base_risk": 75, "gram": "negative"},
    "leptospira":    {"name": "Leptospira",         "base_risk": 80, "gram": "negative"},
    "enterococcus":  {"name": "Enterococcus",       "base_risk": 70, "gram": "positive"},
    "staphylococcus":{"name": "Staphylococcus",     "base_risk": 60, "gram": "positive"},
    "bacillus":      {"name": "Bacillus (generic)",  "base_risk": 40, "gram": "positive"},
    "none":          {"name": "No bacteria detected","base_risk": 0,  "gram": "n/a"},
}


def introduction():
    print_header("RISK ASSESSMENT: How AquaGuard Decides If Water Is Safe")

    print("""  When AquaGuard tests a water sample, it doesn't just look
  at ONE measurement. It combines MULTIPLE data points to
  calculate an overall RISK LEVEL.

  Think of it like a doctor's checkup. A doctor doesn't just
  check your temperature -- they also check blood pressure,
  heart rate, and other signs. Only by looking at everything
  together can they make a good diagnosis.

  AquaGuard combines three key measurements:

      1. pH          -- Is the water's chemistry balanced?
      2. EC (uS/cm)  -- How much stuff is dissolved in it?
      3. Bacteria    -- What (if any) bacteria were detected?

  In this module, YOU will be the AquaGuard system! You'll
  input water measurements and see how the risk calculator
  works step by step.
""")
    pause()


def explain_scoring():
    print_header("HOW THE RISK SCORE WORKS")

    print("""  AquaGuard uses a point-based risk system from 0 to 100:

      RISK SCORE     RISK LEVEL        COLOR     ACTION
      ----------     ---------------   -------   ----------------
       0 - 20        LOW               GREEN     Safe to drink
      21 - 40        MODERATE          YELLOW    Caution advised
      41 - 60        HIGH              ORANGE    Do not drink
      61 - 80        VERY HIGH         RED       Dangerous
      81 - 100       CRITICAL          RED       Extremely unsafe

  Each factor contributes to the total score:

      +-------------------+----------------------------------+
      | FACTOR            | HOW IT ADDS RISK                 |
      +-------------------+----------------------------------+
      | pH                | 0 pts if 6.5-8.5 (safe range)   |
      |                   | +5-15 pts if slightly off        |
      |                   | +20-30 pts if very off           |
      +-------------------+----------------------------------+
      | EC                | 0 pts if < 800 uS/cm            |
      |                   | +5-10 pts if 800-1500            |
      |                   | +15-25 pts if > 1500             |
      +-------------------+----------------------------------+
      | Bacteria type     | 0 pts if none detected           |
      |                   | +40-95 pts depending on species  |
      |                   | (E. coli and Vibrio are highest) |
      +-------------------+----------------------------------+

  The final score is the SUM of all factors, capped at 100.

  IMPORTANT: If ANY bacteria are detected in drinking water,
  the risk is automatically at least MODERATE (score >= 40).
  This matches WHO/EPA guidelines: zero bacteria tolerance.
""")
    pause()


def calculate_ph_risk(ph):
    """Calculate risk points from pH value."""
    if 6.5 <= ph <= 8.5:
        points = 0
        explanation = "pH is within the safe range (6.5-8.5). No risk added."
    elif 6.0 <= ph < 6.5 or 8.5 < ph <= 9.0:
        points = 8
        explanation = (f"pH {ph} is slightly outside the safe range. "
                       "Water may taste off. Bacteria removal efficiency "
                       "slightly reduced. (+8 risk points)")
    elif 5.0 <= ph < 6.0 or 9.0 < ph <= 10.0:
        points = 18
        explanation = (f"pH {ph} is moderately outside safe range. "
                       "May indicate chemical contamination. Can corrode "
                       "pipes and leach metals. (+18 risk points)")
    elif ph < 5.0:
        points = 30
        explanation = (f"pH {ph} is VERY acidic! This is dangerous. "
                       "Indicates serious contamination or industrial "
                       "waste. Can cause chemical burns. (+30 risk points)")
    else:  # ph > 10.0
        points = 30
        explanation = (f"pH {ph} is VERY alkaline! This is dangerous. "
                       "Indicates chemical contamination. Can cause "
                       "skin irritation and digestive issues. (+30 risk points)")
    return points, explanation


def calculate_ec_risk(ec):
    """Calculate risk points from EC value."""
    if ec < 800:
        points = 0
        explanation = (f"EC {ec} uS/cm is within acceptable range. "
                       "Dissolved solids are normal. No risk added.")
    elif 800 <= ec < 1500:
        points = 8
        explanation = (f"EC {ec} uS/cm is elevated. Higher than normal "
                       "dissolved solids -- could indicate mineral "
                       "buildup or mild contamination. (+8 risk points)")
    elif 1500 <= ec < 3000:
        points = 18
        explanation = (f"EC {ec} uS/cm is HIGH. Significant dissolved "
                       "solids present. Water may taste salty or bitter. "
                       "Could indicate sewage or agricultural runoff. "
                       "(+18 risk points)")
    else:
        points = 25
        explanation = (f"EC {ec} uS/cm is VERY HIGH. Water has extreme "
                       "levels of dissolved substances. Likely contaminated "
                       "by industrial waste, heavy metals, or concentrated "
                       "sewage. (+25 risk points)")
    return points, explanation


def calculate_bacteria_risk(bacteria_key):
    """Calculate risk points from bacteria type."""
    info = BACTERIA_RISK[bacteria_key]
    points = info["base_risk"]
    name = info["name"]

    if bacteria_key == "none":
        explanation = "No bacteria detected. This is the ideal result!"
    elif points >= 85:
        explanation = (f"{name} detected! This is a CRITICAL pathogen. "
                       f"Gram-{info['gram']}. Known to cause severe, "
                       f"potentially fatal disease through contaminated "
                       f"water. (+{points} risk points)")
    elif points >= 70:
        explanation = (f"{name} detected. This is a DANGEROUS pathogen. "
                       f"Gram-{info['gram']}. Causes significant illness "
                       f"and indicates fecal or environmental contamination. "
                       f"(+{points} risk points)")
    elif points >= 40:
        explanation = (f"{name} detected. Gram-{info['gram']}. While not "
                       f"the most dangerous waterborne pathogen, any "
                       f"bacteria in drinking water is concerning. "
                       f"(+{points} risk points)")
    else:
        explanation = (f"{name} detected. Gram-{info['gram']}. Low "
                       f"pathogenic risk in water, but presence still "
                       f"indicates contamination. (+{points} risk points)")

    return points, explanation


def get_risk_level(score):
    """Return risk level string and recommendations."""
    if score <= 20:
        level = "LOW"
        color = "GREEN"
        bar = "[##########....................] 0-20"
        recommendation = (
            "Water appears safe for drinking based on tested parameters.\n"
            "  Continue regular monitoring as a precaution."
        )
    elif score <= 40:
        level = "MODERATE"
        color = "YELLOW"
        bar = "[..........##########..........] 21-40"
        recommendation = (
            "Caution advised. One or more parameters are outside ideal\n"
            "  range. Consider additional testing or treatment before\n"
            "  drinking. Boiling may help if bacteria is present."
        )
    elif score <= 60:
        level = "HIGH"
        color = "ORANGE"
        bar = "[....................##########] 41-60"
        recommendation = (
            "DO NOT DRINK this water without treatment. Multiple risk\n"
            "  factors detected. Boil water for at least 1 minute or use\n"
            "  a certified water filter. Seek an alternative source."
        )
    elif score <= 80:
        level = "VERY HIGH"
        color = "RED"
        bar = "[....................##########] 61-80"
        recommendation = (
            "DANGEROUS. This water poses a serious health risk. Do NOT\n"
            "  drink, cook with, or bathe in this water. Seek emergency\n"
            "  alternative water supply. Report to local health authority."
        )
    else:
        level = "CRITICAL"
        color = "RED"
        bar = "[....................##########] 81-100"
        recommendation = (
            "EXTREMELY UNSAFE. This water is critically contaminated.\n"
            "  Immediate health risk. Avoid ALL contact. Alert local\n"
            "  health authorities immediately. Seek emergency water supply."
        )

    return level, color, bar, recommendation


def interactive_calculator():
    print_header("INTERACTIVE RISK CALCULATOR")
    print("  You are now the AquaGuard system! Enter water sample")
    print("  measurements and see the risk assessment in real time.\n")
    print("  (Type 'quit' at any prompt to skip to the quiz)\n")

    while True:
        print_subheader("NEW WATER SAMPLE")

        # Get pH
        try:
            ph_input = input("  Enter pH value (0-14): ").strip()
            if ph_input.lower() == "quit":
                break
            ph = float(ph_input)
            if ph < 0 or ph > 14:
                print("  pH must be between 0 and 14. Try again.\n")
                continue
        except ValueError:
            print("  Please enter a number. Try again.\n")
            continue

        # Get EC
        try:
            ec_input = input("  Enter EC value in uS/cm (0-10000): ").strip()
            if ec_input.lower() == "quit":
                break
            ec = float(ec_input)
            if ec < 0:
                print("  EC cannot be negative. Try again.\n")
                continue
        except ValueError:
            print("  Please enter a number. Try again.\n")
            continue

        # Get bacteria type
        print("\n  Select bacteria detected:")
        bacteria_options = list(BACTERIA_RISK.keys())
        for i, key in enumerate(bacteria_options, 1):
            info = BACTERIA_RISK[key]
            gram_str = f"(Gram-{info['gram']})" if info['gram'] != 'n/a' else ""
            print(f"    {i:2d}. {info['name']} {gram_str}")

        try:
            bac_input = input("\n  Enter number (1-{}): ".format(
                len(bacteria_options))).strip()
            if bac_input.lower() == "quit":
                break
            bac_idx = int(bac_input) - 1
            if bac_idx < 0 or bac_idx >= len(bacteria_options):
                print("  Invalid selection. Try again.\n")
                continue
            bacteria_key = bacteria_options[bac_idx]
        except ValueError:
            print("  Please enter a number. Try again.\n")
            continue

        # Calculate risk
        print("\n" + "=" * 56)
        print("  AQUAGUARD RISK ASSESSMENT REPORT")
        print("=" * 56)

        print_subheader("INPUT DATA")
        print(f"  pH:        {ph}")
        print(f"  EC:        {ec} uS/cm")
        print(f"  TDS (est): {ec * 0.6:.0f} ppm")
        print(f"  Bacteria:  {BACTERIA_RISK[bacteria_key]['name']}")

        print_subheader("ANALYSIS: pH Factor")
        ph_risk, ph_explanation = calculate_ph_risk(ph)
        print(f"  {ph_explanation}")

        print_subheader("ANALYSIS: EC Factor")
        ec_risk, ec_explanation = calculate_ec_risk(ec)
        print(f"  {ec_explanation}")

        print_subheader("ANALYSIS: Bacteria Factor")
        bac_risk, bac_explanation = calculate_bacteria_risk(bacteria_key)
        print(f"  {bac_explanation}")

        # Total score
        total = min(ph_risk + ec_risk + bac_risk, 100)
        level, color, bar, recommendation = get_risk_level(total)

        print_subheader("FINAL RISK SCORE")
        print(f"  pH risk:       {ph_risk:3d} points")
        print(f"  EC risk:       {ec_risk:3d} points")
        print(f"  Bacteria risk: {bac_risk:3d} points")
        print(f"  --------------------------")
        print(f"  TOTAL:         {total:3d} / 100\n")
        print(f"  Risk Level:    {level}")
        print(f"  Status Color:  {color}")
        print(f"  {bar}\n")

        print_subheader("RECOMMENDATION")
        print(f"  {recommendation}\n")

        # Show what AquaGuard would do
        print_subheader("AQUAGUARD RESPONSE")
        if total <= 20:
            print("  AquaGuard LED:  GREEN (steady)")
            print("  AquaGuard LCD:  'Water Safe - All parameters normal'")
            print("  Cloud upload:   Routine data logged")
        elif total <= 40:
            print("  AquaGuard LED:  YELLOW (slow blink)")
            print("  AquaGuard LCD:  'Caution - Review parameters'")
            print("  Cloud upload:   Flagged for review")
        elif total <= 60:
            print("  AquaGuard LED:  ORANGE (fast blink)")
            print("  AquaGuard LCD:  'WARNING - Do not drink!'")
            print("  Cloud upload:   Alert sent to operator")
        else:
            print("  AquaGuard LED:  RED (rapid blink)")
            print("  AquaGuard LCD:  'DANGER - Water contaminated!'")
            print("  Cloud upload:   Emergency alert sent!")
            print("  SMS/Email:      Notification to health authority")

        print()

        another = input("  Test another sample? (y/n): ").strip().lower()
        if another != "y":
            break
        print()


def preset_scenarios():
    print_header("PRESET SCENARIOS: See How Risk Changes")

    scenarios = [
        {
            "name": "Clean Tap Water",
            "ph": 7.2, "ec": 350,
            "bacteria": "none",
            "description": "Normal treated municipal water"
        },
        {
            "name": "Slightly Off Well Water",
            "ph": 6.2, "ec": 950,
            "bacteria": "none",
            "description": "Well water with slightly low pH and elevated minerals"
        },
        {
            "name": "Contaminated River Water",
            "ph": 7.5, "ec": 600,
            "bacteria": "e_coli",
            "description": "Looks clean but E. coli detected"
        },
        {
            "name": "Flood Water",
            "ph": 6.8, "ec": 2500,
            "bacteria": "leptospira",
            "description": "After a flood -- high dissolved solids and bacteria"
        },
        {
            "name": "Industrial Contamination",
            "ph": 4.2, "ec": 4000,
            "bacteria": "none",
            "description": "Acidic water near an industrial site"
        },
    ]

    for i, s in enumerate(scenarios, 1):
        ph_risk, _ = calculate_ph_risk(s["ph"])
        ec_risk, _ = calculate_ec_risk(s["ec"])
        bac_risk, _ = calculate_bacteria_risk(s["bacteria"])
        total = min(ph_risk + ec_risk + bac_risk, 100)
        level, color, _, _ = get_risk_level(total)

        bac_name = BACTERIA_RISK[s["bacteria"]]["name"]

        print(f"  Scenario {i}: {s['name']}")
        print(f"  {s['description']}")
        print(f"  pH={s['ph']}  EC={s['ec']}  Bacteria={bac_name}")
        print(f"  Risk Score: {total}/100 -> {level} ({color})")
        print()

    print("""  NOTICE how Scenario 3 (Contaminated River Water) has a
  higher risk than Scenario 5 (Industrial Contamination),
  even though the industrial water has worse pH and EC.

  That's because BACTERIA presence is the most heavily
  weighted factor. Clean-looking water with E. coli is
  MORE dangerous than acidic water without bacteria!

  This is exactly how AquaGuard prioritizes threats.
""")
    pause()


def quiz():
    print_header("QUIZ TIME! (4 Questions)")
    print("  Test your understanding of risk assessment.\n")

    score = 0

    # Q1
    print("  Question 1:")
    print("  Water has pH 7.0, EC 400, and no bacteria detected.")
    print("  What is the risk level?")
    print("    A) CRITICAL -- you can never be too careful")
    print("    B) MODERATE -- some risk always exists")
    print("    C) LOW -- all parameters are within safe ranges")
    print("    D) HIGH -- EC is too high")
    answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
    if answer == "C":
        print("  Correct! pH 7.0 (safe), EC 400 (safe), no bacteria = LOW risk.\n")
        score += 1
    else:
        print("  Incorrect. The answer is C -- all values are normal, so LOW risk.\n")

    # Q2
    print("  Question 2:")
    print("  Water looks crystal clear with perfect pH (7.2) and low")
    print("  EC (200), but E. coli is detected. Is this water safe?")
    print("    A) Yes -- the pH and EC are perfect")
    print("    B) No -- ANY bacteria in drinking water makes it unsafe")
    print("    C) Maybe -- it depends on how much E. coli")
    print("    D) Yes -- E. coli is harmless")
    answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
    if answer == "B":
        print("  Correct! Zero tolerance for bacteria in drinking water.\n"
              "  Even one E. coli means the water is unsafe.\n")
        score += 1
    else:
        print("  Incorrect. The answer is B -- zero bacteria tolerance.\n")

    # Q3
    print("  Question 3:")
    print("  Why does AquaGuard combine MULTIPLE measurements instead")
    print("  of just testing for bacteria?")
    print("    A) To make the device more expensive")
    print("    B) Because one measurement alone doesn't tell the full")
    print("       story -- multiple data points give a complete picture")
    print("    C) Because bacteria tests are unreliable")
    print("    D) Just for extra credit")
    answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
    if answer == "B":
        print("  Correct! pH and EC can reveal chemical contamination that\n"
              "  bacteria testing alone would miss. The combination gives\n"
              "  a much more reliable safety assessment.\n")
        score += 1
    else:
        print("  Incorrect. The answer is B -- multiple data points give\n"
              "  a complete picture of water safety.\n")

    # Q4
    print("  Question 4:")
    print("  A risk score of 75/100 means the AquaGuard LED would show:")
    print("    A) GREEN (steady) -- everything is fine")
    print("    B) YELLOW (slow blink) -- minor caution")
    print("    C) RED (rapid blink) -- dangerous contamination")
    print("    D) No light -- the device is broken")
    answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
    if answer == "C":
        print("  Correct! A score of 75 is VERY HIGH risk = RED alert.\n")
        score += 1
    else:
        print("  Incorrect. The answer is C -- RED (rapid blink) for\n"
              "  a very high risk score.\n")

    return score


def main():
    print("\n" + "*" * 60)
    print("  AQUAGUARD LEARNING MODULE 5")
    print("  Risk Assessment: Combining Data for Water Safety")
    print("*" * 60)
    pause()

    introduction()
    explain_scoring()
    preset_scenarios()

    print_header("YOUR TURN: Interactive Risk Calculator")
    print("  Now try entering your own water measurements!\n")
    interactive_calculator()

    score = quiz()

    print_header("MODULE COMPLETE!")
    print(f"  Module complete! You scored {score}/4")
    print()
    if score == 4:
        print("  PERFECT SCORE! You understand how AquaGuard assesses risk!")
    elif score >= 3:
        print("  Great job! You've got a solid grasp of risk assessment.")
    else:
        print("  Review the scoring system and try again!")
    print()
    print("  You've completed all AquaGuard learning modules!")
    print("  You now understand:")
    print("    - Gram staining (Module 1)")
    print("    - Bacteria shapes (Module 2)")
    print("    - How AI detects bacteria (Module 3)")
    print("    - Water quality standards (Module 4)")
    print("    - Risk assessment (Module 5)")
    print()
    print("  Keep learning, keep building, keep making water safer!")
    print()


if __name__ == "__main__":
    main()
