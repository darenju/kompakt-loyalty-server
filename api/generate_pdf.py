from barcode import EAN13, Code128
from barcode.writer import SVGWriter
import qrcode
from fpdf import FPDF, Align
from fpdf.outline import TableOfContents
from io import BytesIO

dpi=212

def convert(cm):
    return (cm / dpi) * 2.54

ean13_width=convert(460)
ean13_height=convert(200)
qrcode_width=convert(300)

document_width=convert(480)
document_height=convert(800)

def generate_pdf(settings, cards):
    pdf = FPDF(format=(document_width, document_height), unit="cm")
    pdf.set_margins(0.5, 0.5)
    pdf.set_font("arial", size=12)
    pdf.add_page()

    if settings["includeTOC"]:
        toc = TableOfContents()
        pdf.insert_toc_placeholder(toc.render_toc, allow_extra_pages=False, pages=1)

    first = True

    for card in cards:
        name = card["name"]
        type = card["type"]
        code = str(card["code"]).upper()
        
        if not first:
            pdf.add_page()

        first = False

        pdf.start_section(name=name, level=0)

        if settings["includeNames"]:
            pdf.cell(text=name, w=(document_width - 1), align=Align.C)

        if type == "EAN13" or type == "Code128":
            bytes = BytesIO()
            if type == "EAN13":
                EAN13(code, writer=SVGWriter()).write(bytes)
            elif type == "Code128":
                Code128(code, writer=SVGWriter()).write(bytes)

            pdf.image(bytes, w=ean13_width, h=ean13_height, y=((pdf.h - ean13_height) / 2), x=convert(10))
            bytes.close()
            
            pdf.set_y(5)
        elif type == "QRCode":
            image = qrcode.make(code)
            pdf.image(image.get_image(), w=qrcode_width, h=qrcode_width, y=((pdf.h - qrcode_width) / 2), x=((pdf.w - qrcode_width) / 2))
            pdf.set_y(6)

        if settings["includeCodes"]:
            pdf.cell(text=code, w=document_width - 1, h=1, align=Align.C)

    return pdf.output()
