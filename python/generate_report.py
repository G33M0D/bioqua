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
PDF Report Generator (FEATURE_PDF_REPORTS)
============================================
Generates a printable PDF report from test log data.
Includes sensor readings, bacteria classifications, risk levels,
and trend charts.

REQUIRES: pip install fpdf2 matplotlib

HOW TO RUN:
  python generate_report.py                    # Report for today
  python generate_report.py --date 2026-04-04  # Report for specific date
  python generate_report.py --all              # Report for all data

OUTPUT: results/reports/aquaguard_report_YYYY-MM-DD.pdf
"""

import os
import sys
import csv
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import LOG_FILE, PROJECT_ROOT

REPORTS_DIR = os.path.join(PROJECT_ROOT, "results", "reports")


def load_entries(date_filter=None):
    """Load test log entries, optionally filtered by date."""
    if not os.path.exists(LOG_FILE):
        print(f"ERROR: No test log found at {LOG_FILE}")
        print("Run some tests first using: python controller.py")
        return []

    entries = []
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if date_filter and row.get("date") != date_filter:
                continue
            entries.append(row)
    return entries


def generate_report(date_filter=None):
    """Generate a PDF report."""
    try:
        from fpdf import FPDF
    except ImportError:
        print("ERROR: fpdf2 not installed. Run: pip install fpdf2")
        return

    entries = load_entries(date_filter)
    if not entries:
        print("No data to report.")
        return

    os.makedirs(REPORTS_DIR, exist_ok=True)

    if date_filter:
        date_str = date_filter
        filename = f"aquaguard_report_{date_str}.pdf"
    else:
        date_str = time.strftime("%Y-%m-%d")
        filename = f"aquaguard_report_{date_str}_all.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ── Cover Page ──
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 28)
    pdf.cell(0, 40, "AquaGuard", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 16)
    pdf.cell(0, 10, "AI-Powered Bacteria Detection", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 10, "for Safe Drinking Water", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(20)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Water Quality Report", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 8, f"Date: {date_str}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 8, f"Total Tests: {len(entries)}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(30)
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 8, "Original Author: Guillanne Marie Agreda", new_x="LMARGIN", new_y="NEXT", align="C")

    # ── Summary Page ──
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "Test Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Count risks
    risk_counts = {"LOW": 0, "MODERATE": 0, "HIGH": 0}
    bacteria_counts = {}
    locations = set()
    ph_values = []
    ec_values = []

    for entry in entries:
        risk = entry.get("risk_level", "")
        if risk in risk_counts:
            risk_counts[risk] += 1

        bacteria = entry.get("bacteria_class", "Unknown")
        bacteria_counts[bacteria] = bacteria_counts.get(bacteria, 0) + 1

        locations.add(entry.get("location", "Unknown"))

        try:
            ph_val = float(entry.get("ph", ""))
            ec_val = float(entry.get("ec_us_cm", ""))
            ph_values.append(ph_val)
            ec_values.append(ec_val)
        except (ValueError, TypeError):
            pass  # Skip rows with missing/invalid sensor data

    # Risk summary
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Risk Level Distribution", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)

    for risk, count in risk_counts.items():
        pct = (count / len(entries) * 100) if entries else 0
        pdf.cell(0, 8, f"  {risk}: {count} tests ({pct:.0f}%)", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)

    # Sensor ranges
    if ph_values or ec_values:
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Sensor Readings", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 12)
        if ph_values:
            pdf.cell(0, 8, f"  pH range: {min(ph_values):.1f} - {max(ph_values):.1f} (normal: 6.5-8.5)", new_x="LMARGIN", new_y="NEXT")
        if ec_values:
            pdf.cell(0, 8, f"  EC range: {min(ec_values):.0f} - {max(ec_values):.0f} uS/cm (normal: <1500)", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)

    # Bacteria found
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Bacteria Classifications", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    for bacteria, count in sorted(bacteria_counts.items(), key=lambda x: -x[1]):
        pdf.cell(0, 8, f"  {bacteria}: {count} detections", new_x="LMARGIN", new_y="NEXT")

    # ── Detailed Results Table ──
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "Detailed Results", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Table header
    pdf.set_font("Helvetica", "B", 9)
    col_widths = [30, 20, 20, 35, 30, 20, 35]
    headers = ["Time", "pH", "EC", "Location", "Bacteria", "Conf.", "Risk"]

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1)
    pdf.ln()

    # Table rows
    pdf.set_font("Helvetica", "", 8)
    for entry in entries:
        row_data = [
            entry.get("time", ""),
            entry.get("ph", ""),
            entry.get("ec_us_cm", ""),
            entry.get("location", "")[:15],
            entry.get("bacteria_class", "")[:15],
            entry.get("confidence_pct", ""),
            entry.get("risk_level", ""),
        ]
        for i, val in enumerate(row_data):
            pdf.cell(col_widths[i], 7, str(val), border=1)
        pdf.ln()

    # ── Trend Chart ──
    if len(entries) >= 2:
        chart_path = filepath.replace('.pdf', '_chart.png')
        chart_file = generate_chart(entries, chart_path)
        if chart_file:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 18)
            pdf.cell(0, 12, "Trend Chart", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(5)
            try:
                pdf.image(chart_file, x=10, w=190)
            except Exception:
                pdf.set_font("Helvetica", "", 12)
                pdf.cell(0, 8, "(Chart could not be embedded)", new_x="LMARGIN", new_y="NEXT")

    # ── Save ──
    pdf.output(filepath)
    print(f"Report saved: {filepath}")
    return filepath


def generate_chart(entries, output_path):
    """Generate a pH/EC trend chart (requires matplotlib)."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    times = []
    phs = []
    ecs = []

    for entry in entries:
        try:
            times.append(entry.get("time", ""))
            phs.append(float(entry.get("ph", 0)))
            ecs.append(float(entry.get("ec_us_cm", 0)))
        except ValueError:
            continue

    if not times:
        return None

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    ax1.plot(range(len(phs)), phs, 'b-o', markersize=4)
    ax1.axhline(y=6.5, color='r', linestyle='--', alpha=0.5, label='Normal min')
    ax1.axhline(y=8.5, color='r', linestyle='--', alpha=0.5, label='Normal max')
    ax1.set_ylabel('pH')
    ax1.set_title('AquaGuard - Water Quality Over Time')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(range(len(ecs)), ecs, 'g-o', markersize=4)
    ax2.axhline(y=1500, color='r', linestyle='--', alpha=0.5, label='Normal max')
    ax2.set_ylabel('EC (uS/cm)')
    ax2.set_xlabel('Test Number')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path


if __name__ == "__main__":
    date_filter = None
    if len(sys.argv) >= 3 and sys.argv[1] == "--date":
        date_filter = sys.argv[2]
    elif len(sys.argv) >= 2 and sys.argv[1] == "--all":
        date_filter = None
    else:
        date_filter = time.strftime("%Y-%m-%d")

    generate_report(date_filter)
