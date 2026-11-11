from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

PDF_OUTPUT_PATH = Path("O:/GITHUB-Repo/ClarityDocs/sample_ukvi_notice.pdf")


def generate_sample_ukvi_pdf(output_path: Path = PDF_OUTPUT_PATH):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles matching UK Government correspondence
    header_style = ParagraphStyle(
        'GovHeader',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0b0c0c'),
        spaceAfter=4
    )
    
    subhead_style = ParagraphStyle(
        'GovSubHeader',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#505a5f'),
        spaceAfter=15
    )

    body_style = ParagraphStyle(
        'GovBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#0b0c0c'),
        spaceAfter=10
    )

    bold_body = ParagraphStyle(
        'GovBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    warning_box_style = ParagraphStyle(
        'GovWarning',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#d4351c')
    )

    story = []

    # UK Government Header Block
    story.append(Paragraph("UK Visas and Immigration", header_style))
    story.append(Paragraph("Home Office — European Casework & Further Evidence Team<br/>Vulcan House, 6 Millsands, Sheffield, S3 8NU", subhead_style))
    story.append(Spacer(1, 10))

    # Case Metadata Table
    meta_data = [
        [Paragraph("<b>Our Reference:</b>", body_style), Paragraph("GWF098765432", body_style)],
        [Paragraph("<b>Case ID:</b>", body_style), Paragraph("1212-0001-9988-7766", body_style)],
        [Paragraph("<b>National Insurance:</b>", body_style), Paragraph("JH112233B", body_style)],
        [Paragraph("<b>Date of Notice:</b>", body_style), Paragraph("10 November 2026", body_style)],
        [Paragraph("<b>Applicant Address:</b>", body_style), Paragraph("124 High Street, Manchester, M1 1AA", body_style)]
    ]
    t = Table(meta_data, colWidths=[130, 370])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # Notice Body
    story.append(Paragraph("Dear Applicant,", body_style))
    story.append(Paragraph("<b>RE: REQUEST FOR FURTHER EVIDENCE IN RELATION TO YOUR APPLICATION</b>", bold_body))
    story.append(Paragraph(
        "We are writing regarding your application for Leave to Remain under the Immigration Rules. "
        "We have conducted an initial assessment of the documents submitted with your application. "
        "At this stage, we do not have sufficient evidence to satisfy the requirements under Appendix Finance "
        "and Appendix EU.",
        body_style
    ))

    story.append(Paragraph(
        "To enable us to make a lawful decision, you must provide the following mandatory documents:",
        body_style
    ))

    # Requirements list
    story.append(Paragraph(
        "<b>1. Bank Statements & Proof of Maintenance Funds:</b><br/>"
        "Official monthly statements from a regulated financial institution covering a consecutive 28-day period. "
        "The closing balance date on your statement must end no more than 31 days prior to your application date. "
        "Statements must show your full name, account number, and official bank logo.",
        body_style
    ))

    story.append(Paragraph(
        "<b>2. Tuberculosis (TB) Medical Clearance Certificate:</b><br/>"
        "A valid medical certificate issued by a designated Home Office approved diagnostic clinic confirming clearance.",
        body_style
    ))

    story.append(Paragraph(
        "<b>3. Proof of Continuous Qualifying Residence:</b><br/>"
        "Official HMRC employment history records or P60 documentation demonstrating continuous residence in the UK.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # Deadline & Statutory Warning Box
    warning_data = [[
        Paragraph(
            "<b>STATUTORY DEADLINE: 14 DAYS</b><br/>"
            "You must provide the requested documentation to this office within 14 days of the date of this letter.<br/>"
            "Failure to provide the requested information within this statutory window will result in your application "
            "being refused on the basis of the information currently available, with no refund of fees paid.",
            warning_box_style
        )
    ]]
    warning_table = Table(warning_data, colWidths=[500])
    warning_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f3f2f1')),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#d4351c')),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(warning_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Yours sincerely,", body_style))
    story.append(Paragraph("<b>Caseworker Operations 04</b><br/>UK Visas and Immigration, Home Office", body_style))

    doc.build(story)
    print(f"Sample PDF successfully generated at: {output_path}")


if __name__ == "__main__":
    generate_sample_ukvi_pdf()
