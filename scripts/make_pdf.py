"""Generates me/about_business.pdf, the simulated business profile for Cedar Path Tutoring."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

OUT = Path(__file__).resolve().parent.parent / "me" / "about_business.pdf"
GREEN = colors.HexColor("#1F5F3F")

styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Title"], textColor=GREEN, fontSize=24)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=GREEN, spaceBefore=12)
body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=10.5, leading=15)
sub = ParagraphStyle("sub", parent=body, alignment=1, textColor=colors.grey)


def bullets(items):
    return [Paragraph(f"&bull; {i}", body) for i in items]


def table(rows, widths):
    t = Table(rows, colWidths=widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F6F3")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


cell = ParagraphStyle("cell", parent=body, fontSize=9.5, leading=12)
P = lambda s: Paragraph(s, cell)

story = [
    Paragraph("Cedar Path Tutoring", h1),
    Paragraph("Tutoring &amp; exam preparation for grades 7-12 &middot; Beirut &amp; online", sub),
    Spacer(1, 14),

    Paragraph("Who we are", h2),
    Paragraph(
        "Cedar Path Tutoring was founded in 2022 in Beirut by two teachers who were tired of seeing "
        "capable students walk into their official exams underprepared. We run a small, focused center "
        "on Bliss Street near Hamra and teach the same programs online over Zoom, so students anywhere "
        "in Lebanon can join.", body),

    Paragraph("Our mission", h2),
    Paragraph(
        "To help every student in Lebanon walk into their official exams and university applications "
        "prepared and confident, through small classes, personalized study plans and honest progress "
        "tracking.", body),

    Paragraph("Services and pricing", h2),
    table([
        ["Service", "Details", "Price"],
        [P("One-on-one tutoring"), P("Math, Physics, Chemistry, Biology, English, French, Arabic"),
         P("20 USD/hr (grades 7-9)<br/>25 USD/hr (grades 10-12)")],
        [P("Small-group classes"), P("Maximum 5 students per group, same subjects"), P("12 USD/hr per student")],
        [P("Brevet bootcamp"), P("8-week intensive for the grade 9 official exam"), P("300 USD")],
        [P("Lebanese Bac bootcamp"), P("8-week intensive for the grade 12 official exam"), P("300 USD")],
        [P("SAT preparation"), P("10-week program, includes a free diagnostic test"), P("450 USD")],
        [P("IB support"), P("Math and Physics, HL and SL"), P("35 USD/hr")],
        [P("Placement assessment"), P("30 minutes, matches the student with a tutor and level"), P("Free")],
    ], [4 * cm, 8 * cm, 4.5 * cm]),
    Spacer(1, 6),
    Paragraph("Online sessions cost the same as in-person sessions.", body),

    Paragraph("Our team", h2),
    *bullets([
        "<b>Sara Mansour</b> - Founder and Head of Mathematics. Taught IB and Lebanese-program math for "
        "12 years before founding Cedar Path. Designs every student's study plan.",
        "<b>Ali Hamdan</b> - Co-founder, Physics and SAT Lead. Engineering graduate of the American "
        "University of Beirut; runs the SAT program and the physics track of the Bac bootcamp.",
        "<b>Nadine Khalil</b> - Head of Languages. Teaches English and French and is a certified DELF "
        "examiner.",
    ]),

    Paragraph("Why families choose us", h2),
    *bullets([
        "<b>Progress reports every two weeks</b> - parents receive a written report on attendance, "
        "results and next steps.",
        "<b>Tutor-match guarantee</b> - if a student does not click with their tutor, we switch tutors for free.",
        "<b>Past-paper bank</b> - students get our archive of past official-exam papers with worked solutions.",
        "<b>Small groups, always</b> - our groups never exceed five students.",
    ]),

    Paragraph("Policies", h2),
    *bullets([
        "Sessions can be cancelled or rescheduled free of charge with at least 24 hours' notice; "
        "later cancellations are charged in full.",
        "Payment by cash at the center, bank transfer, or Whish Money. Hourly tutoring is paid monthly; "
        "bootcamps and SAT prep are paid upfront at enrollment.",
        "Siblings enrolled at the same time receive a 10% discount on hourly tutoring.",
    ]),

    Paragraph("How to enroll", h2),
    Paragraph(
        "1) Book the free 30-minute placement assessment. 2) We propose a tutor, format and schedule. "
        "3) Start sessions within the week.", body),

    Paragraph("Visit or contact us", h2),
    *bullets([
        "Address: 3rd floor, Bliss Street, Hamra, Beirut",
        "Hours: Monday-Friday 14:00-21:00, Saturday 09:00-18:00, closed Sunday",
        "Email: info@cedarpath.example &middot; Phone: +961 1 000 000 &middot; Instagram: @cedarpathtutoring",
    ]),
]

SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                  topMargin=2 * cm, bottomMargin=2 * cm,
                  title="About Cedar Path Tutoring").build(story)
print(f"Wrote {OUT}")
