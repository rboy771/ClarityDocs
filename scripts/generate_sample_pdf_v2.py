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

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "sample_ukvi_further_evidence_v2.pdf"

INK = colors.HexColor("#0b0c0c")
GREY = colors.HexColor("#505a5f")
RULE = colors.HexColor("#b1b4b6")


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GREY)
    canvas.drawString(20 * mm, 12 * mm, "SAMPLE DOCUMENT FOR SOFTWARE TESTING ONLY. Not a real Home Office letter. All names and numbers are fictional.")
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
        title="Request for further evidence",
    )

    base = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=base["Normal"], fontName="Helvetica", fontSize=10, leading=14.5, textColor=INK, spaceAfter=7)
    small = ParagraphStyle("small", parent=body, fontSize=8.5, leading=12, textColor=GREY, spaceAfter=0)
    org = ParagraphStyle("org", parent=body, fontName="Helvetica-Bold", fontSize=15, leading=18, spaceAfter=1)
    heading = ParagraphStyle("heading", parent=body, fontName="Helvetica-Bold", fontSize=11, leading=15, spaceBefore=9, spaceAfter=4)
    title = ParagraphStyle("title", parent=body, fontName="Helvetica-Bold", fontSize=12.5, leading=16, spaceBefore=6, spaceAfter=8)
    item = ParagraphStyle("item", parent=body, leftIndent=14, spaceAfter=5)
    label = ParagraphStyle("label", parent=body, fontName="Helvetica-Bold", fontSize=9.5, spaceAfter=0)
    value = ParagraphStyle("value", parent=body, fontSize=9.5, spaceAfter=0)

    s = []

    header = Table(
        [[
            [Paragraph("Home Office", org), Paragraph("UK Visas and Immigration", body)],
            Paragraph("Evidence and Enquiry Team<br/>Sheffield<br/>Email: via your online account", small),
        ]],
        colWidths=[105 * mm, 65 * mm],
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

    addressee = Paragraph(
        "Mr Sam Example<br/>Flat 4, 18 Sample Road<br/>Manchester<br/>M1 1AA",
        body,
    )
    refs = Table(
        [
            [Paragraph("Date of letter", label), Paragraph("10 November 2026", value)],
            [Paragraph("Our reference", label), Paragraph("GWF012345678", value)],
            [Paragraph("Application ID", label), Paragraph("1212-0001-9988-7766", value)],
            [Paragraph("National Insurance no.", label), Paragraph("QQ 12 34 56 C", value)],
            [Paragraph("Contact number held", label), Paragraph("07700 900123", value)],
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
    block.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    s.append(block)
    s.append(Spacer(1, 6))

    s.append(Paragraph("Dear Mr Example", body))
    s.append(Paragraph("Request for further evidence: application for permission to stay as a Student", title))

    s.append(Paragraph(
        "We have received your application to extend your permission to stay in the UK as a Student, "
        "made on 28 October 2026. We cannot make a decision yet because some of the evidence we need is "
        "missing or does not meet the requirements of the Immigration Rules.",
        body,
    ))

    s.append(Paragraph("What you need to send us", heading))
    s.append(Paragraph("You must provide all of the following:", body))

    s.append(Paragraph(
        "<b>1. Bank statements showing your funds.</b> You told us you would support yourself using personal "
        "savings. The statements you sent show the balance fell below the required amount on 3 days in the "
        "period. You must send official bank statements showing the required maintenance funds were held for a "
        "consecutive 28-day period. The closing balance date must be no earlier than 31 days before the date of "
        "your application. Each statement must show your full name, your account number, the bank's name and logo, "
        "and the date of each transaction. Printouts that do not show these details, and ATM receipts, will not be accepted.",
        item,
    ))
    s.append(Paragraph(
        "<b>2. Tuberculosis test certificate.</b> Our records show you have been in the UK for fewer than 6 "
        "months and have not provided a valid tuberculosis (TB) test certificate. You must send a TB certificate "
        "issued by a clinic on the Home Office approved list for the country where you took the test. The certificate "
        "must be less than 6 months old on the date of your application.",
        item,
    ))
    s.append(Paragraph(
        "<b>3. Evidence of your English language ability.</b> The English language certificate you uploaded does "
        "not include a unique reference number (URN). You must send a Secure English Language Test (SELT) result at "
        "level B2 from an approved provider, or a letter from Ecctis confirming your degree was taught in English. "
        "We need the reference number so we can check the result online.",
        item,
    ))

    s.append(Paragraph("When we need it by", heading))

    deadline = Table(
        [[Paragraph(
            "<b>You must reply by 24 November 2026.</b><br/>"
            "This is 14 days from the date of this letter. Send the documents listed above through your online "
            "account. Upload each document as a separate file in PDF, JPG or PNG format, under 6MB each.",
            body,
        )]],
        colWidths=[170 * mm],
    )
    deadline.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1, INK),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f3f2f1")),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    s.append(KeepTogether(deadline))
    s.append(Spacer(1, 8))

    s.append(PageBreak())

    s.append(Paragraph("What happens if you do not reply", heading))
    s.append(Paragraph(
        "If we do not receive the evidence by the date above, we will make a decision on your application using "
        "the information we already hold. This is likely to mean your application is refused. Application fees "
        "and the Immigration Health Surcharge are not refunded where an application is refused.",
        body,
    ))

    s.append(Paragraph("If you need more time", heading))
    s.append(Paragraph(
        "If you cannot get a document in time because of circumstances outside your control, tell us before "
        "the deadline and explain why. We will consider your reasons but we cannot guarantee an extension. "
        "You should keep evidence of the problem, such as an email from your bank or clinic.",
        body,
    ))

    s.append(Paragraph("Your permission to stay while we decide", heading))
    s.append(Paragraph(
        "Your current permission to stay continues until we make a decision on your application, as long as you "
        "applied before it expired. You must keep following the conditions of your current permission, including any "
        "limit on the number of hours you can work.",
        body,
    ))

    s.append(Paragraph("Getting help", heading))
    s.append(Paragraph(
        "You can get free, independent advice from your university international student advice service or from "
        "an immigration adviser regulated by the Office of the Immigration Services Commissioner (OISC). "
        "We cannot give legal advice about your application.",
        body,
    ))

    s.append(Spacer(1, 10))
    s.append(Paragraph("Yours sincerely", body))
    s.append(Spacer(1, 14))
    s.append(Paragraph("<b>Caseworker 4417</b><br/>Evidence and Enquiry Team<br/>UK Visas and Immigration", body))

    doc.build(s, onFirstPage=footer, onLaterPages=footer)
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    build()
