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
Learning Module 1: What is Gram Staining?
A step-by-step visual guide to one of microbiology's most important techniques.
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
    print_header("GRAM STAINING: The Microbiologist's Color Code")

    print("""  Imagine you walk into a hospital lab. A patient is sick, and
  doctors need to know WHAT kind of bacteria is causing the infection.
  They can't wait days for a full culture to grow.

  Enter Gram staining -- a technique invented in 1884 by a Danish
  scientist named Hans Christian Gram. In under an hour, it tells
  you one of the most important things about a bacterium:

      Is it Gram-POSITIVE or Gram-NEGATIVE?

  This single piece of information helps doctors choose the right
  antibiotic and can literally save lives.
""")
    pause()


def history():
    print_header("A BRIEF HISTORY")

    print("""  +------------------------------------------------------+
  |  Hans Christian Gram (1853-1938)                     |
  |  Danish bacteriologist working in Berlin             |
  |                                                      |
  |  In 1884, he was trying to make bacteria easier to   |
  |  see under a microscope. He stumbled upon a staining |
  |  method that divided bacteria into two major groups.  |
  |                                                      |
  |  He actually thought his method was a FAILURE because |
  |  it didn't work on all bacteria equally! But that     |
  |  "failure" turned out to be one of the most useful    |
  |  discoveries in all of microbiology.                  |
  +------------------------------------------------------+
""")
    pause()


def step_by_step():
    print_header("THE 4 STEPS OF GRAM STAINING")

    # Step 1
    print_subheader("STEP 1: Crystal Violet (Primary Stain)")
    print("""  First, we spread bacteria on a glass slide and heat-fix them
  (so they stick). Then we flood the slide with CRYSTAL VIOLET dye.

  This dye is dark purple and stains ALL bacteria -- both types.

      +-------------------+
      | @@@@   @@@@  @@@@ |   @ = bacteria (all purple now)
      |  @@@@  @@@@ @@@@  |
      | @@@@   @@@@  @@@@ |   Crystal violet dye soaks into
      +-------------------+   every bacterial cell.
      ~~~~~~~~~~~~~~~~~~~~~~~~  <- purple dye everywhere
""")
    pause()

    # Step 2
    print_subheader("STEP 2: Iodine Mordant (The Lock)")
    print("""  Next, we add IODINE solution (called a "mordant").

  Think of iodine as a LOCK. It reacts with the crystal violet
  inside the cells to form large crystal-violet-iodine (CV-I)
  complexes. These complexes are too big to easily wash out.

      +-------------------+
      | [@@]  [@@]  [@@]  |   [@@] = bacteria with CV-I
      |  [@@]  [@@] [@@]  |          complexes locked inside
      | [@@]  [@@]  [@@]  |
      +-------------------+
      ~~~~~~~~~~~~~~~~~~~~~~~~  <- iodine solution

  At this point, ALL bacteria are still purple.
""")
    pause()

    # Step 3
    print_subheader("STEP 3: Decolorizer (The Big Reveal)")
    print("""  THIS is the critical step. We wash the slide with a
  decolorizer (alcohol or acetone) for just a few seconds.

  Here's where the magic happens:

  GRAM-POSITIVE bacteria have a THICK cell wall made of
  peptidoglycan (like a thick brick wall). The decolorizer
  can't penetrate it, so the purple dye stays TRAPPED inside.

  GRAM-NEGATIVE bacteria have a THIN cell wall with an extra
  outer membrane. The decolorizer dissolves that outer membrane
  and washes the purple dye RIGHT OUT.

      GRAM-POSITIVE              GRAM-NEGATIVE
      (thick wall)               (thin wall)

      +-----------+              +-----------+
      | ########  |              |           |
      | # [@@] #  |  <-- still  |    ( )    |  <-- purple
      | # [@@] #  |     purple  |    ( )    |     washed out!
      | ########  |              |           |
      +-----------+              +-----------+
        # = thick                  Now colorless
        peptidoglycan
""")
    pause()

    # Step 4
    print_subheader("STEP 4: Safranin Counterstain (The Pink Finish)")
    print("""  Finally, we add SAFRANIN -- a light red/pink dye.

  The Gram-POSITIVE bacteria are already purple, so the pink
  doesn't change them much.

  The Gram-NEGATIVE bacteria (now colorless) soak up the pink
  safranin and turn PINK/RED.

      GRAM-POSITIVE              GRAM-NEGATIVE
      RESULT: PURPLE             RESULT: PINK

      +-----------+              +-----------+
      | ########  |              | ////////  |
      | # [@@] #  |  PURPLE!    | / (@@) /  |  PINK!
      | # [@@] #  |             | / (@@) /  |
      | ########  |              | ////////  |
      +-----------+              +-----------+
""")
    pause()


def why_it_matters():
    print_header("WHY DOES THIS MATTER?")

    print("""  The difference between Gram-positive and Gram-negative isn't
  just about color -- it tells us about the bacteria's STRUCTURE:

  +---------------------+-------------------+-------------------+
  |                     | GRAM-POSITIVE     | GRAM-NEGATIVE     |
  +---------------------+-------------------+-------------------+
  | Color after stain   | Purple / Violet   | Pink / Red        |
  | Cell wall thickness | THICK             | THIN              |
  | Outer membrane      | NO                | YES               |
  | Peptidoglycan       | Many layers       | 1-2 layers        |
  | Antibiotic response | Penicillin works  | Often resistant   |
  +---------------------+-------------------+-------------------+

  EXAMPLES:

      Gram-POSITIVE                Gram-NEGATIVE
      - Staphylococcus aureus      - Escherichia coli (E. coli)
      - Streptococcus              - Salmonella
      - Bacillus                   - Vibrio cholerae (cholera)
      - Clostridium                - Pseudomonas

  In water quality testing (like AquaGuard!), knowing the Gram
  type helps identify what kind of contamination you're dealing
  with and how dangerous it might be.
""")
    pause()


def summary_diagram():
    print_header("SUMMARY: The Full Process at a Glance")

    print("""
  BACTERIA ON SLIDE
        |
        v
  [1] Crystal Violet -----> ALL bacteria turn PURPLE
        |
        v
  [2] Iodine Mordant -----> Dye LOCKED inside all cells
        |
        v
  [3] Decolorizer --------> Gram(+) stays PURPLE
        |                    Gram(-) becomes COLORLESS
        v
  [4] Safranin ------------> Gram(+) stays PURPLE
                             Gram(-) turns PINK

  FINAL RESULT:
      Purple = Gram-positive (thick wall, no outer membrane)
      Pink   = Gram-negative (thin wall, outer membrane)
""")
    pause()


def quiz():
    print_header("QUIZ TIME! (5 Questions)")
    print("  Test your knowledge of Gram staining.\n")

    score = 0

    # Q1
    print("  Question 1:")
    print("  Who invented the Gram staining technique?")
    print("    A) Louis Pasteur")
    print("    B) Hans Christian Gram")
    print("    C) Robert Koch")
    print("    D) Alexander Fleming")
    answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
    if answer == "B":
        print("  Correct! Hans Christian Gram developed it in 1884.\n")
        score += 1
    else:
        print("  Incorrect. The answer is B -- Hans Christian Gram (1884).\n")

    # Q2
    print("  Question 2:")
    print("  What color do Gram-POSITIVE bacteria appear after staining?")
    print("    A) Pink")
    print("    B) Green")
    print("    C) Purple")
    print("    D) Blue")
    answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
    if answer == "C":
        print("  Correct! They retain the crystal violet and appear purple.\n")
        score += 1
    else:
        print("  Incorrect. The answer is C -- Purple.\n")

    # Q3
    print("  Question 3:")
    print("  What is the role of iodine in the Gram staining process?")
    print("    A) It kills the bacteria")
    print("    B) It acts as a mordant, locking dye inside cells")
    print("    C) It washes out the primary stain")
    print("    D) It provides the pink color")
    answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
    if answer == "B":
        print("  Correct! Iodine forms complexes that trap the dye.\n")
        score += 1
    else:
        print("  Incorrect. The answer is B -- It acts as a mordant.\n")

    # Q4
    print("  Question 4:")
    print("  WHY do Gram-positive bacteria keep the purple dye?")
    print("    A) They have a thick peptidoglycan cell wall")
    print("    B) They have an outer membrane that traps dye")
    print("    C) They are bigger than Gram-negative bacteria")
    print("    D) They absorb more safranin")
    answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
    if answer == "A":
        print("  Correct! The thick peptidoglycan wall prevents decolorization.\n")
        score += 1
    else:
        print("  Incorrect. The answer is A -- thick peptidoglycan wall.\n")

    # Q5
    print("  Question 5:")
    print("  Which of these is a Gram-NEGATIVE bacterium?")
    print("    A) Staphylococcus aureus")
    print("    B) Streptococcus")
    print("    C) Escherichia coli (E. coli)")
    print("    D) Bacillus")
    answer = input("\n  Your answer (A/B/C/D): ").strip().upper()
    if answer == "C":
        print("  Correct! E. coli is Gram-negative (pink after staining).\n")
        score += 1
    else:
        print("  Incorrect. The answer is C -- E. coli.\n")

    return score


def main():
    print("\n" + "*" * 60)
    print("  AQUAGUARD LEARNING MODULE 1")
    print("  Gram Staining: The Microbiologist's Color Code")
    print("*" * 60)
    pause()

    introduction()
    history()
    step_by_step()
    why_it_matters()
    summary_diagram()

    score = quiz()

    print_header("MODULE COMPLETE!")
    print(f"  Module complete! You scored {score}/5")
    print()
    if score == 5:
        print("  PERFECT SCORE! You're ready to stain some slides!")
    elif score >= 3:
        print("  Great job! You've got a solid understanding of Gram staining.")
    else:
        print("  Keep studying! Try running this module again to review.")
    print()


if __name__ == "__main__":
    main()
