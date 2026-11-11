from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "sample_dwp_pip_decision.pdf"

INK = colors.HexColor("#0b0c0c")
GREY = colors.HexColor("#505a5f")
RULE = colors.HexColor("#b1b4b6")
PALE = colors.HexColor("#f3f2f1")


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GREY)
    canvas.drawString(20 * mm, 12 * mm, "SAMPLE DOCUMENT FOR SOFTWARE TESTING ONLY. Not a real DWP letter. All names and numbers are fictional.")
    canvas.drawRightString(190 * mm, 12 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build(output_path: Path = OUTPUT_PATH) -> None:
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=22 * mm,
        title="Personal Independence Payment decision",
    )

    base = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=base["Normal"], fontName="Helvetica", fontSize=10, leading=14.5, textColor=INK, spaceAfter=7)
    small = ParagraphStyle("small", parent=body, fontSize=8.5, leading=12, textColor=GREY, spaceAfter=0)
    org = ParagraphStyle("org", parent=body, fontName="Helvetica-Bold", fontSize=15, leading=18, spaceAfter=1)
    heading = ParagraphStyle("heading", parent=body, fontName="Helvetica-Bold", fontSize=11, leading=15, spaceBefore=9, spaceAfter=4)
    title = ParagraphStyle("title", parent=body, fontName="Helvetica-Bold", fontSize=12.5, leading=16, spaceBefore=6, spaceAfter=8)
    label = ParagraphStyle("label", parent=body, fontName="Helvetica-Bold", fontSize=9.5, spaceAfter=0)
    value = ParagraphStyle("value", parent=body, fontSize=9.5, spaceAfter=0)
    cell = ParagraphStyle("cell", parent=body, fontSize=9, leading=12, spaceAfter=0)
    cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")

    s = []

    header = Table(
        [[
            [Paragraph("Department for Work and Pensions", org), Paragraph("Personal Independence Payment", body)],
            Paragraph("PIP Centre 7<br/>Leeds<br/>Textphone: 0800 000 0000", small),
        ]],
        colWidths=[110 * mm, 60 * mm],
    )
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, 0), 1.2, INK),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    s.append(header)
    s.append(Spacer(1, 8))

    addressee = Paragraph("Ms Jordan Sample<br/>7 Example Terrace<br/>Leeds<br/>LS1 1AA", body)
    refs = Table(
        [
            [Paragraph("Date of decision", label), Paragraph("5 November 2026", value)],
            [Paragraph("National Insurance no.", label), Paragraph("QQ 98 76 54 A", value)],
            [Paragraph("Claim reference", label), Paragraph("PIP-2026-0048213", value)],
        ],
        colWidths=[38 * mm, 32 * mm],
    )
    refs.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    block = Table([[addressee, refs]], colWidths=[95 * mm, 75 * mm])
    block.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    s.append(block)
    s.append(Spacer(1, 6))

    s.append(Paragraph("Dear Ms Sample", body))
    s.append(Paragraph("Your Personal Independence Payment claim: decision", title))

    s.append(Paragraph(
        "We have looked at your claim for Personal Independence Payment (PIP) and the information from your "
        "assessment on 14 October 2026. We have decided that you are not entitled to PIP. This letter explains "
        "how we reached that decision.",
        body,
    ))

    s.append(Paragraph("How we scored your claim", heading))
    s.append(Paragraph(
        "PIP is based on how your health condition or disability affects you, not on the condition itself. "
        "To get the standard rate of either part of PIP, you need at least 8 points in that part. "
        "To get the enhanced rate you need at least 12 points.",
        body,
    ))

    rows = [
        [Paragraph("Daily living activity", cellb), Paragraph("Descriptor chosen", cellb), Paragraph("Points", cellb)],
        [Paragraph("1. Preparing food", cell), Paragraph("Needs an aid or appliance to prepare or cook a simple meal", cell), Paragraph("2", cell)],
        [Paragraph("2. Taking nutrition", cell), Paragraph("Can take nutrition unaided", cell), Paragraph("0", cell)],
        [Paragraph("3. Managing therapy or monitoring a health condition", cell), Paragraph("Needs an aid to take or manage medication", cell), Paragraph("1", cell)],
        [Paragraph("4. Washing and bathing", cell), Paragraph("Needs an aid or appliance to wash or bathe", cell), Paragraph("2", cell)],
        [Paragraph("5. Managing toilet needs", cell), Paragraph("Can manage toilet needs unaided", cell), Paragraph("0", cell)],
        [Paragraph("6. Dressing and undressing", cell), Paragraph("Can dress and undress unaided", cell), Paragraph("0", cell)],
        [Paragraph("7 to 10. Communicating, reading, mixing with others, budgeting", cell), Paragraph("No difficulty identified", cell), Paragraph("0", cell)],
        [Paragraph("Daily living total", cellb), Paragraph("", cell), Paragraph("5", cellb)],
        [Paragraph("Mobility activity", cellb), Paragraph("Descriptor chosen", cellb), Paragraph("Points", cellb)],
        [Paragraph("11. Planning and following journeys", cell), Paragraph("Can plan and follow the route of a journey unaided", cell), Paragraph("0", cell)],
        [Paragraph("12. Moving around", cell), Paragraph("Can stand and then move more than 50 metres but no more than 200 metres", cell), Paragraph("4", cell)],
        [Paragraph("Mobility total", cellb), Paragraph("", cell), Paragraph("4", cellb)],
    ]
    t = Table(rows, colWidths=[62 * mm, 90 * mm, 18 * mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, RULE),
        ("BACKGROUND", (0, 0), (-1, 0), PALE),
        ("BACKGROUND", (0, 9), (-1, 9), PALE),
        ("BACKGROUND", (0, 8), (-1, 8), colors.HexColor("#e8f0f7")),
        ("BACKGROUND", (0, 12), (-1, 12), colors.HexColor("#e8f0f7")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (2, 0), (2, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    s.append(t)
    s.append(Spacer(1, 6))

    s.append(Paragraph(
        "You scored 5 points for daily living and 4 points for mobility. This is below the 8 points needed "
        "for the standard rate in either part, so we cannot award PIP.",
        body,
    ))

    s.append(PageBreak())

    s.append(Paragraph("If you think this decision is wrong", heading))
    s.append(Paragraph(
        "You can ask us to look at the decision again. This is called a <b>mandatory reconsideration</b>. "
        "You need to do this before you can appeal to the Social Security and Child Support Tribunal.",
        body,
    ))

    box = Table(
        [[Paragraph(
            "<b>You must ask for a mandatory reconsideration within one month of the date of this letter.</b><br/>"
            "The date of this decision is 5 November 2026. You should therefore contact us by 5 December 2026. "
            "You can ask by phone, or by writing to the address at the top of this letter.",
            body,
        )]],
        colWidths=[170 * mm],
    )
    box.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, INK),
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    s.append(KeepTogether(box))
    s.append(Spacer(1, 6))

    s.append(Paragraph("What to include", heading))
    s.append(Paragraph(
        "Say which parts of the decision you disagree with and why. It helps to point to the specific activities "
        "listed above, for example how you manage preparing food or moving around on a bad day. Include any new "
        "evidence, such as a letter from your GP, consultant or specialist nurse, or a medication list.",
        body,
    ))

    s.append(Paragraph("If you ask after the deadline", heading))
    s.append(Paragraph(
        "We can accept a late request if there are good reasons for the delay, such as being in hospital. "
        "The request must still be made within 13 months of the date of this decision. You will need to explain "
        "why it was late.",
        body,
    ))

    s.append(Paragraph("Other support you may be able to get", heading))
    s.append(Paragraph(
        "A decision about PIP does not stop you claiming other benefits such as Universal Credit. "
        "Free advice is available from Citizens Advice and from local welfare rights services.",
        body,
    ))

    s.append(Spacer(1, 10))
    s.append(Paragraph("Yours sincerely", body))
    s.append(Spacer(1, 14))
    s.append(Paragraph("<b>Decision Maker</b><br/>Personal Independence Payment<br/>Department for Work and Pensions", body))

    doc.build(s, onFirstPage=footer, onLaterPages=footer)
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    build()
