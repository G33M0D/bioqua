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
Learning Module 2: Bacteria Shapes
Learn the three main morphologies: Cocci, Bacilli, and Spirilla.
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
    print_header("BACTERIA SHAPES: Nature's Tiny Architecture")

    print("""  If you looked at bacteria under a microscope, you'd notice
  something surprising: they don't all look the same!

  Bacteria come in distinct SHAPES, and these shapes are one of
  the first things microbiologists use to identify them. There
  are three main shapes you need to know:

      1. COCCI   -- round (like tiny balls)
      2. BACILLI -- rod-shaped (like tiny capsules)
      3. SPIRILLA -- spiral (like tiny corkscrews)

  Let's explore each one!
""")
    pause()


def cocci_section():
    print_header("SHAPE 1: COCCI (Round / Spherical)")

    print("""  The word "coccus" comes from the Greek word for "berry."
  These bacteria are round or slightly oval, like tiny spheres.

  SINGLE COCCUS:

          @@
         @@@@
         @@@@
          @@

  But cocci rarely hang out alone. They form ARRANGEMENTS
  that help us identify them further:

  DIPLOCOCCI (pairs):         STREPTOCOCCI (chains):

      @@  @@                    @@  @@  @@  @@  @@
     @@@@ @@@@                 @@@@@@@@@@@@@@@@@@@@
     @@@@ @@@@                 @@@@@@@@@@@@@@@@@@@@
      @@  @@                    @@  @@  @@  @@  @@

  STAPHYLOCOCCI (clusters, like grapes):

         @@  @@
        @@@@ @@@@
        @@@@ @@@@@@
       @@@@@@@@ @@@@
        @@@@ @@@@
         @@  @@

  COMMON EXAMPLES:
  +---------------------------+-------------------------------+
  | Bacterium                 | Where It's Found              |
  +---------------------------+-------------------------------+
  | Staphylococcus aureus     | Skin, nose -- causes staph    |
  |                           | infections, food poisoning    |
  +---------------------------+-------------------------------+
  | Streptococcus pyogenes    | Throat -- causes strep throat |
  +---------------------------+-------------------------------+
  | Neisseria meningitidis    | Throat/nose -- can cause      |
  |  (diplococcus)            | meningitis                    |
  +---------------------------+-------------------------------+
  | Enterococcus              | Gut, sewage -- indicates      |
  |                           | fecal contamination in water! |
  +---------------------------+-------------------------------+

  WATER QUALITY NOTE: Finding Enterococcus (a coccus) in water
  is a strong indicator of sewage contamination. BIOQUA
  watches for these!
""")
    pause()


def bacilli_section():
    print_header("SHAPE 2: BACILLI (Rod-Shaped)")

    print("""  The word "bacillus" comes from Latin meaning "little stick."
  These bacteria look like tiny rods or capsules.

  SINGLE BACILLUS:

      +----------+
      |          |
      +----------+

  Like cocci, bacilli can form different arrangements:

  DIPLOBACILLI (pairs):        STREPTOBACILLI (chains):

   +------+ +------+     +------++------++------++------+
   |      | |      |     |      ||      ||      ||      |
   +------+ +------+     +------++------++------++------+

  COCCOBACILLI (short and plump -- almost round):

      +----+
      |    |
      +----+

  COMMON EXAMPLES:
  +---------------------------+-------------------------------+
  | Bacterium                 | Where It's Found              |
  +---------------------------+-------------------------------+
  | Escherichia coli (E.coli) | Intestines -- some strains    |
  |                           | cause severe food poisoning.  |
  |                           | KEY water contamination       |
  |                           | indicator!                    |
  +---------------------------+-------------------------------+
  | Salmonella                | Poultry, eggs, water --       |
  |                           | causes salmonellosis          |
  +---------------------------+-------------------------------+
  | Bacillus anthracis        | Soil -- causes anthrax        |
  +---------------------------+-------------------------------+
  | Vibrio cholerae           | Contaminated water -- causes  |
  |  (curved rod)             | cholera (kills thousands/yr)  |
  +---------------------------+-------------------------------+
  | Clostridium botulinum     | Soil, improperly canned food  |
  |                           | -- causes botulism            |
  +---------------------------+-------------------------------+

  WATER QUALITY NOTE: E. coli is the GOLD STANDARD indicator
  for fecal contamination in drinking water. If BIOQUA finds
  E. coli, that water is NOT safe to drink.
""")
    pause()


def spirilla_section():
    print_header("SHAPE 3: SPIRILLA (Spiral / Corkscrew)")

    print("""  These bacteria are shaped like spirals or corkscrews. The
  spiral shape actually helps them move through thick fluids
  like mucus -- they "drill" through like a corkscrew.

  There are three types of spiral bacteria:

  VIBRIO (comma-shaped / slightly curved):

          ___
         /   \\
        |
         \\

  SPIRILLUM (rigid spiral, like a corkscrew):

         ~~~      ~~~      ~~~
        /   \\    /   \\    /   \\
       /     \\  /     \\  /     \\
              \\/       \\/

  SPIROCHETE (flexible, thin spiral -- can bend and flex):

       ~~~~~~~~~~~~~~~~~~~~~~~~
      /  /  /  /  /  /  /  /  /
     ~~~~~~~~~~~~~~~~~~~~~~~~

  COMMON EXAMPLES:
  +---------------------------+-------------------------------+
  | Bacterium                 | Where It's Found              |
  +---------------------------+-------------------------------+
  | Vibrio cholerae           | Contaminated water -- causes  |
  |  (vibrio/comma shape)     | cholera                       |
  +---------------------------+-------------------------------+
  | Spirillum minus           | Rat saliva -- causes rat-bite |
  |                           | fever                         |
  +---------------------------+-------------------------------+
  | Treponema pallidum        | Human body -- causes syphilis |
  |  (spirochete)             |                               |
  +---------------------------+-------------------------------+
  | Leptospira                | Water contaminated by animal  |
  |  (spirochete)             | urine -- causes leptospirosis |
  +---------------------------+-------------------------------+
  | Campylobacter             | Poultry, untreated water --   |
  |  (spiral/curved rod)      | causes gastroenteritis        |
  +---------------------------+-------------------------------+

  WATER QUALITY NOTE: Leptospira is found in water contaminated
  by animal urine (especially after flooding). Campylobacter is
  one of the most common causes of waterborne illness worldwide.
""")
    pause()


def comparison_chart():
    print_header("SIDE-BY-SIDE COMPARISON")

    print("""
      COCCI              BACILLI             SPIRILLA
      (Round)            (Rod)               (Spiral)

       @@              +--------+           ~~~    ~~~
      @@@@             |        |          /   \\  /   \\
      @@@@             |        |         /     \\/     \\
       @@              +--------+

  Size:  0.5-1 um       1-10 um             1-100 um
  Move:  Usually no      Some have           Most can move
         (no flagella)   flagella            (drill motion)
  Wall:  Can be G+ / G-  Can be G+ / G-     Usually G-

  +------------------------------------------------------+
  |  FUN FACT: The smallest bacteria are about 0.2 um.   |
  |  A human hair is about 70 um wide. You could fit     |
  |  350 bacteria side-by-side across a single hair!     |
  +------------------------------------------------------+

  WHY SHAPE MATTERS FOR BIOQUA:
  When our AI analyzes a microscope image, shape is one of
  the first features it uses to classify bacteria. Round blobs?
  Probably cocci. Elongated shapes? Likely bacilli. Curved or
  wavy? Could be spirilla. This is what computer vision does!
""")
    pause()


def quiz():
    print_header("QUIZ TIME! Matching Quiz (5 Questions)")
    print("  Match the bacterium to its shape.\n")

    score = 0

    # Q1
    print("  Question 1:")
    print("  What shape is Staphylococcus aureus?")
    print("    A) Rod (Bacillus)")
    print("    B) Round (Coccus)")
    print("    C) Spiral (Spirillum)")
    answer = input("\n  Your answer (A/B/C): ").strip().upper()
    if answer == "B":
        print("  Correct! 'Staphylo-COCCUS' -- the name gives it away!\n")
        score += 1
    else:
        print("  Incorrect. The answer is B -- Coccus (round). The name\n"
              "  'Staphylococcus' literally tells you the shape.\n")

    # Q2
    print("  Question 2:")
    print("  E. coli is rod-shaped. What is the scientific term for")
    print("  rod-shaped bacteria?")
    print("    A) Cocci")
    print("    B) Spirilla")
    print("    C) Bacilli")
    answer = input("\n  Your answer (A/B/C): ").strip().upper()
    if answer == "C":
        print("  Correct! Bacilli are rod-shaped bacteria.\n")
        score += 1
    else:
        print("  Incorrect. The answer is C -- Bacilli.\n")

    # Q3
    print("  Question 3:")
    print("  Leptospira causes disease through contaminated water.")
    print("  What shape is it?")
    print("    A) Round (Coccus)")
    print("    B) Rod (Bacillus)")
    print("    C) Spiral (Spirochete)")
    answer = input("\n  Your answer (A/B/C): ").strip().upper()
    if answer == "C":
        print("  Correct! Leptospira is a spirochete (flexible spiral).\n")
        score += 1
    else:
        print("  Incorrect. The answer is C -- Spirochete (spiral).\n")

    # Q4
    print("  Question 4:")
    print("  When cocci arrange in CLUSTERS (like grapes), we call them:")
    print("    A) Streptococci")
    print("    B) Diplococci")
    print("    C) Staphylococci")
    answer = input("\n  Your answer (A/B/C): ").strip().upper()
    if answer == "C":
        print("  Correct! 'Staphylo' means cluster, like a bunch of grapes.\n")
        score += 1
    else:
        print("  Incorrect. The answer is C -- Staphylococci.\n"
              "  'Staphylo' = cluster, 'Strepto' = chain, 'Diplo' = pair.\n")

    # Q5
    print("  Question 5:")
    print("  Which shape of bacteria can 'drill' through thick fluids")
    print("  like mucus, thanks to their corkscrew shape?")
    print("    A) Cocci")
    print("    B) Bacilli")
    print("    C) Spirilla")
    answer = input("\n  Your answer (A/B/C): ").strip().upper()
    if answer == "C":
        print("  Correct! Spirilla rotate their spiral body to move forward.\n")
        score += 1
    else:
        print("  Incorrect. The answer is C -- Spirilla.\n")

    return score


def main():
    print("\n" + "*" * 60)
    print("  BIOQUA LEARNING MODULE 2")
    print("  Bacteria Shapes: Cocci, Bacilli, and Spirilla")
    print("*" * 60)
    pause()

    introduction()
    cocci_section()
    bacilli_section()
    spirilla_section()
    comparison_chart()

    score = quiz()

    print_header("MODULE COMPLETE!")
    print(f"  Module complete! You scored {score}/5")
    print()
    if score == 5:
        print("  PERFECT SCORE! You can tell your cocci from your bacilli!")
    elif score >= 3:
        print("  Nice work! You've got a good grasp of bacteria shapes.")
    else:
        print("  Review the shapes and try again -- you'll get it!")
    print()


if __name__ == "__main__":
    main()
