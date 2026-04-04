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
Learning Module 4: Water Quality Standards
WHO/EPA standards, pH, EC/TDS, waterborne bacteria & diseases,
and safe vs unsafe water indicators.
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


def introduction():
    print_header("WATER QUALITY: What Makes Water Safe to Drink?")

    print("""  Every day, you turn on a tap and drink water without
  thinking about it. But for nearly 2 BILLION people worldwide,
  safe drinking water isn't guaranteed.

  Waterborne diseases kill over 500,000 people every year,
  mostly children under 5. That's why water quality testing
  matters -- and that's why AquaGuard exists.

  In this module, you'll learn:

      1. What pH means and why it matters
      2. What EC and TDS measure
      3. WHO and EPA drinking water standards
      4. Common waterborne bacteria and diseases
      5. How to tell safe water from unsafe water
""")
    pause()


def ph_section():
    print_header("WHAT IS pH?")

    print("""  pH measures how ACIDIC or BASIC (alkaline) a liquid is.
  The scale goes from 0 to 14:

      0                    7                    14
      |-------|-------|-------|-------|-------|-------|
      ACIDIC          NEUTRAL          BASIC/ALKALINE

  EVERYDAY EXAMPLES:

      pH 0-1   Battery acid           EXTREMELY ACIDIC
      pH 2     Lemon juice, vinegar   Very acidic
      pH 3     Orange juice, soda     Acidic
      pH 4     Tomato juice           Mildly acidic
      pH 5     Black coffee           Slightly acidic
      pH 6     Milk                   Nearly neutral
      pH 7     Pure water             NEUTRAL
      pH 8     Seawater               Slightly basic
      pH 9     Baking soda solution   Mildly basic
      pH 10    Milk of magnesia       Basic
      pH 11    Ammonia                Very basic
      pH 12    Soapy water            Very basic
      pH 13-14 Drain cleaner          EXTREMELY BASIC

  SAFE DRINKING WATER pH:

      +-----------------------------------------------+
      |   WHO Standard:  6.5  to  8.5                 |
      |   EPA Standard:  6.5  to  8.5                 |
      |   Ideal range:   6.5  to  7.5                 |
      +-----------------------------------------------+

  WHY pH MATTERS FOR BACTERIA:

      - Most bacteria thrive at pH 6.5-7.5 (near neutral)
      - Very low pH (<4) or very high pH (>9) kills most bacteria
      - pH outside 6.5-8.5 may also indicate chemical contamination
      - Water treatment (chlorination) works best at pH 6.5-7.5

  AQUAGUARD uses a pH sensor to check if water falls within
  the safe range. If it doesn't, that's already a warning sign!
""")
    pause()


def ec_tds_section():
    print_header("WHAT ARE EC AND TDS?")

    print_subheader("EC -- Electrical Conductivity")
    print("""  EC measures how well water conducts electricity.

  Pure water is actually a poor conductor of electricity.
  But when you dissolve minerals, salts, or metals in water,
  those dissolved particles carry electrical charge, making
  the water more conductive.

      MORE dissolved stuff  -->  HIGHER EC
      LESS dissolved stuff  -->  LOWER EC

  EC is measured in microsiemens per centimeter (uS/cm).
""")

    print_subheader("TDS -- Total Dissolved Solids")
    print("""  TDS is closely related to EC. It measures the total amount
  of dissolved substances in water (minerals, salts, metals,
  organic matter) in parts per million (ppm) or mg/L.

  A rough conversion:  TDS (ppm) = EC (uS/cm) x 0.5 to 0.7

  WHAT DOES TDS TELL US?

      TDS (ppm)     Quality Level        Taste
      ---------     ----------------     ----------------
      < 50          Very low minerals    Flat, tasteless
      50 - 150      Excellent            Clean, refreshing
      150 - 300     Good                 Normal tap water
      300 - 500     Acceptable           Slightly mineral
      500 - 900     Poor                 Noticeable taste
      900 - 1200    Very poor            Unpleasant
      > 1200        Unacceptable         Salty/bitter

  STANDARDS:
      +-----------------------------------------------+
      |   WHO Guideline:   < 600 ppm (ideal)          |
      |                    < 1000 ppm (maximum)        |
      |   EPA Standard:    < 500 ppm (recommended)     |
      +-----------------------------------------------+

  High TDS doesn't always mean unsafe, but it indicates
  something unusual is dissolved in the water. Combined with
  bacteria detection, it helps paint the full picture.
""")
    pause()


def standards_table():
    print_header("WHO & EPA DRINKING WATER STANDARDS")

    print("""  These are the key parameters for safe drinking water:

  +-------------------+-----------------+-----------------+
  | PARAMETER         | WHO GUIDELINE   | EPA STANDARD    |
  +-------------------+-----------------+-----------------+
  | pH                | 6.5 - 8.5      | 6.5 - 8.5      |
  | TDS               | < 1000 ppm     | < 500 ppm      |
  | EC                | < 1500 uS/cm   | < 800 uS/cm    |
  | Turbidity         | < 1 NTU        | < 1 NTU        |
  | E. coli           | 0 per 100mL    | 0 per 100mL    |
  | Total coliforms   | 0 per 100mL    | 0 per 100mL    |
  | Enterococci       | 0 per 100mL    | 0 per 100mL    |
  | Chlorine residual | 0.2-5 mg/L     | 0.2-4 mg/L     |
  | Lead              | < 0.01 mg/L    | < 0.015 mg/L   |
  | Arsenic           | < 0.01 mg/L    | < 0.01 mg/L    |
  | Nitrate           | < 50 mg/L      | < 10 mg/L      |
  +-------------------+-----------------+-----------------+

  THE GOLDEN RULE FOR BACTERIA:

      +---------------------------------------------------+
      |  ANY detection of E. coli or fecal coliforms in   |
      |  drinking water means the water is UNSAFE.        |
      |                                                   |
      |  The acceptable level is ZERO. Not 1. Not 0.5.   |
      |  ZERO bacteria per 100 mL.                        |
      +---------------------------------------------------+

  This is why AquaGuard's bacteria detection capability is
  so critical -- even a small amount of contamination can
  cause disease outbreaks.
""")
    pause()


def waterborne_bacteria():
    print_header("COMMON WATERBORNE BACTERIA & DISEASES")

    print("""  These are the most dangerous bacteria found in contaminated
  drinking water:

  +---------------------+-------------------+------------------+
  | BACTERIUM           | DISEASE           | SYMPTOMS         |
  +---------------------+-------------------+------------------+
  | Escherichia coli    | Gastroenteritis,  | Diarrhea, cramps |
  | (E. coli O157:H7)  | hemolytic uremic  | bloody stool,    |
  |                     | syndrome (HUS)    | kidney failure   |
  +---------------------+-------------------+------------------+
  | Vibrio cholerae     | Cholera           | Severe watery    |
  |                     |                   | diarrhea, can    |
  |                     |                   | kill in hours    |
  +---------------------+-------------------+------------------+
  | Salmonella typhi    | Typhoid fever     | High fever,      |
  |                     |                   | weakness, rash   |
  +---------------------+-------------------+------------------+
  | Shigella            | Dysentery         | Bloody diarrhea, |
  |                     |                   | fever, cramps    |
  +---------------------+-------------------+------------------+
  | Campylobacter       | Campylobacteriosis| Diarrhea, fever, |
  |                     |                   | nausea           |
  +---------------------+-------------------+------------------+
  | Legionella          | Legionnaires'     | Severe pneumonia |
  |                     | disease           | (from inhaling   |
  |                     |                   | contaminated     |
  |                     |                   | water mist)      |
  +---------------------+-------------------+------------------+
  | Leptospira          | Leptospirosis     | Fever, headache, |
  |                     |                   | muscle pain,     |
  |                     |                   | organ damage     |
  +---------------------+-------------------+------------------+

  GLOBAL IMPACT:

      - Cholera: 1-4 million cases per year worldwide
      - Typhoid: 11-20 million cases per year
      - Waterborne diseases: 500,000+ deaths per year
      - Most victims: children under 5 in developing countries
      - 80% of diseases in developing countries are water-related
""")
    pause()


def safe_vs_unsafe():
    print_header("SAFE vs UNSAFE WATER: How to Tell")

    print("""  CAN YOU TELL IF WATER IS SAFE JUST BY LOOKING AT IT?

      The honest answer: NOT ALWAYS.

  Clear water can still contain invisible bacteria, viruses,
  or chemical contaminants. That's why testing matters!

  But here are some warning signs:

  VISUAL INDICATORS (what you can see):
  +-------------------+-------------------------------------------+
  | INDICATOR         | WHAT IT MEANS                             |
  +-------------------+-------------------------------------------+
  | Cloudy/turbid     | Particles, possibly bacteria or sediment  |
  | Green tint        | Algae growth (may produce toxins)         |
  | Brown/yellow      | Rust, iron, organic matter                |
  | Foam/bubbles      | Detergents, organic contamination         |
  | Oily film         | Chemical contamination                    |
  +-------------------+-------------------------------------------+

  SMELL INDICATORS:
  +-------------------+-------------------------------------------+
  | SMELL             | POSSIBLE CAUSE                            |
  +-------------------+-------------------------------------------+
  | Rotten eggs       | Hydrogen sulfide (bacteria activity)      |
  | Chlorine (strong) | Over-chlorination                         |
  | Musty/earthy      | Algae or organic decay                   |
  | Chemical/gasoline | Industrial contamination                  |
  | No smell          | Good sign, but doesn't guarantee safety   |
  +-------------------+-------------------------------------------+

  WHAT AQUAGUARD MEASURES (beyond what you can see/smell):
  +-------------------+-------------------------------------------+
  | MEASUREMENT       | WHY IT MATTERS                            |
  +-------------------+-------------------------------------------+
  | pH                | Chemical balance                          |
  | EC / TDS          | Dissolved contaminants                    |
  | Bacteria count    | Biological contamination                  |
  | Bacteria type     | Risk level (E. coli = high danger)        |
  | Gram type         | Treatment options                         |
  +-------------------+-------------------------------------------+

  THE AQUAGUARD ADVANTAGE:

      Traditional testing: Send sample to lab, wait 24-48 hours
      AquaGuard testing:   On-site results in minutes

  This speed can literally save lives during outbreaks!
""")
    pause()


def quiz():
    print_header("QUIZ TIME! (5 Questions)")
    print("  Test your knowledge of water quality.\n")

    score = 0

    # Q1
    print("  Question 1:")
    print("  What is the safe pH range for drinking water?")
    print("    A) 0 to 14")
    print("    B) 4.0 to 5.0")
    print("    C) 6.5 to 8.5")
    print("    D) 10.0 to 12.0")
    answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
    if answer == "C":
        print("  Correct! Both WHO and EPA recommend 6.5 to 8.5.\n")
        score += 1
    else:
        print("  Incorrect. The answer is C -- 6.5 to 8.5.\n")

    # Q2
    print("  Question 2:")
    print("  What does TDS stand for?")
    print("    A) Total Dissolved Solids")
    print("    B) Temperature Detection System")
    print("    C) Toxic Drinking Standard")
    print("    D) Thermal Dissolved Salts")
    answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
    if answer == "A":
        print("  Correct! TDS = Total Dissolved Solids (measured in ppm).\n")
        score += 1
    else:
        print("  Incorrect. The answer is A -- Total Dissolved Solids.\n")

    # Q3
    print("  Question 3:")
    print("  How many E. coli bacteria per 100mL are acceptable")
    print("  in drinking water?")
    print("    A) Less than 10")
    print("    B) Less than 100")
    print("    C) Zero (0)")
    print("    D) Less than 1000")
    answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
    if answer == "C":
        print("  Correct! The acceptable level is ZERO. Any E. coli means\n"
              "  the water is unsafe.\n")
        score += 1
    else:
        print("  Incorrect. The answer is C -- Zero. Any amount is unsafe.\n")

    # Q4
    print("  Question 4:")
    print("  Which waterborne disease can kill a person within HOURS")
    print("  if untreated?")
    print("    A) Typhoid fever")
    print("    B) Cholera")
    print("    C) Leptospirosis")
    print("    D) Legionnaires' disease")
    answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
    if answer == "B":
        print("  Correct! Cholera causes severe dehydration and can kill\n"
              "  within hours without treatment.\n")
        score += 1
    else:
        print("  Incorrect. The answer is B -- Cholera.\n")

    # Q5
    print("  Question 5:")
    print("  Can clear, odorless water still be unsafe to drink?")
    print("    A) No -- if it looks and smells fine, it's safe")
    print("    B) Yes -- bacteria and chemicals can be invisible")
    print("    C) Only if it comes from a river")
    print("    D) Only in developing countries")
    answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
    if answer == "B":
        print("  Correct! Many contaminants are invisible. That's exactly\n"
              "  why scientific testing (like AquaGuard) is needed.\n")
        score += 1
    else:
        print("  Incorrect. The answer is B -- invisible contaminants exist.\n")

    return score


def main():
    print("\n" + "*" * 60)
    print("  AQUAGUARD LEARNING MODULE 4")
    print("  Water Quality: Standards, Indicators & Safety")
    print("*" * 60)
    pause()

    introduction()
    ph_section()
    ec_tds_section()
    standards_table()
    waterborne_bacteria()
    safe_vs_unsafe()

    score = quiz()

    print_header("MODULE COMPLETE!")
    print(f"  Module complete! You scored {score}/5")
    print()
    if score == 5:
        print("  PERFECT SCORE! You're a water quality expert!")
    elif score >= 3:
        print("  Great work! You understand the basics of water safety.")
    else:
        print("  Review the standards and try again -- clean water matters!")
    print()


if __name__ == "__main__":
    main()
