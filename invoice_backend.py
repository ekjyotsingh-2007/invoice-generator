from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from num2words import num2words
import os

# ---------------- ENSURE FOLDERS ----------------
os.makedirs("fonts", exist_ok=True)
os.makedirs("invoices", exist_ok=True)

# ---------------- FONT REGISTRATION ----------------
pdfmetrics.registerFont(TTFont("Calibri", "fonts/calibri.ttf"))
pdfmetrics.registerFont(TTFont("Calibri-Bold", "fonts/calibrib.ttf"))
pdfmetrics.registerFont(TTFont("Calibri-Italic", "fonts/calibrii.ttf"))
pdfmetrics.registerFont(TTFont("Calibri-BoldItalic", "fonts/calibriz.ttf"))

# ---------------- PDF GENERATOR ----------------
def generate_invoice_pdf(filename, info, rows, gst_rate):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    x = 25 * mm
    y = height - 25 * mm

    # -------- HEADER --------
    c.setFillColor(colors.darkblue)
    c.setFont("Calibri-BoldItalic", 26)
    c.drawCentredString(width / 2, y, info["company_name"])

    y -= 6
    text_width = c.stringWidth(info["company_name"], "Calibri-BoldItalic", 26)
    c.line((width - text_width) / 2, y, (width + text_width) / 2, y)
    c.setFillColor(colors.black)

    y -= 22
    c.setFont("Calibri", 11)
    c.drawCentredString(width / 2, y, info["company_address"])
    y -= 15
    c.drawCentredString(width / 2, y, info["contact_line"])

    y -= 28
    c.setFont("Calibri-Bold", 16)
    c.drawCentredString(width / 2, y, "BILL")

    y -= 25
    c.setFont("Calibri", 11)
    c.drawString(x, y, f"Ref.No.: {info['bill_no']}")
    c.drawRightString(width - x, y, f"Date: {info['bill_date']}")

    y -= 30
    c.drawString(x, y, "To,")
    y -= 15
    c.drawString(x, y, info["client_name"])

    y -= 20
    c.setFont("Calibri-Bold", 11)
    c.drawString(x, y, f"Sub: {info['subject']}")
    c.setFont("Calibri", 11)

    y -= 25
    c.drawString(x, y, "Dear Sir,")

    # -------- TABLE HEADER --------
    y -= 30
    c.setFont("Calibri-Bold", 11)

    columns = ["Sr.No.", "Description", "Qty.", "Rate", "Amount"]
    col_widths = [35, 260, 60, 60, 80]

    cx = x
    for col, w in zip(columns, col_widths):
        c.drawString(cx, y, col)
        cx += w

    y -= 8
    c.line(x, y, width - x, y)
    y -= 15

    desc_style = ParagraphStyle(
        name="desc",
        fontName="Calibri",
        fontSize=11,
        leading=14,
        alignment=TA_LEFT
    )

    total = 0

    # -------- TABLE ROWS --------
    for sr, desc, qty_disp, rate, amount in rows:
        total += amount
        c.drawString(x, y, str(sr))

        p = Paragraph(desc, desc_style)
        w, h = p.wrap(col_widths[1], 200)
        p.drawOn(c, x + col_widths[0], y - h + 12)

        c.drawString(x + col_widths[0] + col_widths[1], y, qty_disp)
        c.drawString(x + col_widths[0] + col_widths[1] + col_widths[2], y, f"{rate}/-")
        c.drawRightString(width - x, y, f"{amount:.2f}")

        y -= max(h, 18) + 5

    # -------- TOTALS --------
    gst_amount = total * gst_rate / 100
    grand_total = total + gst_amount

    y -= 10
    c.line(x, y, width - x, y)
    y -= 20

    c.setFont("Calibri", 11)
    c.drawRightString(width - x, y, f"Subtotal: ₹ {total:.2f}")
    y -= 15
    c.drawRightString(width - x, y, f"GST @ {gst_rate}%: ₹ {gst_amount:.2f}")

    y -= 20
    c.setFont("Calibri-Bold", 12)
    c.drawRightString(width - x, y, f"Total: ₹ {grand_total:.2f}")

    y -= 25
    words = num2words(grand_total, lang="en_IN").title()
    c.setFont("Calibri", 11)
    c.drawString(x, y, f"Rupees: {words} Only.")

    # -------- FOOTER --------
    y -= 50
    c.drawString(x, y, "Thanking you,")
    y -= 15
    c.drawString(x, y, f"For {info['company_name']}")

    y -= 60
    c.drawString(x, y, "Prop.")

    c.save()
