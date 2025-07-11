import os
from uuid import uuid4
from ebooklib import epub
from ebooklib.utils import create_pagebreak
from barcode import Code128, EAN13
from barcode.writer import ImageWriter
import qrcode
from .convert import convert

image_style = "display: block; margin-left: auto; margin-right: auto; margin-top: 2cm;"

def generate_epub(settings, cards):
  book = epub.EpubBook()
  book.set_identifier("kompakt_loyalty_cards")
  book.set_title("My Loyalty Cards")

  toc = []
  spine = ["nav"]
  page = 2
  files = []

  for card in cards:
    name = card["name"]
    type = card["type"]
    code = str(card["code"]).upper()

    chapter_file = name + ".xhtml"
    filename = str(uuid4()) + ".png"
    files.append(filename)

    card_chapter = epub.EpubHtml(title=name, file_name=chapter_file)

    card_chapter.content = ''

    if settings["includeNames"]:
      card_chapter.content = '<h2 style="text-align: center;">' + name + "</h2>"

    card_chapter.content += '<img alt="[' + name + ']" src="static/' + filename + '" style="' + image_style + ' width: ' + str(convert(460)) + 'cm;"/>'

    if settings["includeCodes"]:
      card_chapter.content += '<p style="text-align: center;">' + code + '</p>'

    card_chapter.content += create_pagebreak(str(page))
  
    page += 1

    if type != "QRCode":
      with open(filename, "wb") as f:
        if type == "Code128":
          Code128(code, writer=ImageWriter()).write(f, {"write_text": False})
        elif type == "EAN13":
          EAN13(code, writer=ImageWriter()).write(f, {"write_text": False})
    else:
      code_image = qrcode.make(code)
      code_image.save(filename)

    image_content = open(filename, "rb").read()
    img = epub.EpubImage(
      uid=name,
      file_name="static/" + filename,
      media_type="image/png",
      content=image_content
    )
    book.add_item(card_chapter)
    book.add_item(img)

    toc.append(card_chapter)
    spine.append(card_chapter)

  book.toc = tuple(toc)
  book.spine = spine

  book.add_item(epub.EpubNav())

  if settings["includeTOC"]:
    book.add_item(epub.EpubNcx())

  book_filename = str(uuid4()) + ".pdf"
  epub.write_epub(book_filename, book, {})
  files.append(book_filename)

  ba = bytearray()
  with open(book_filename, "rb") as f:
    ba = bytearray(f.read())

  for file in files:
    os.remove(file)

  return ba
