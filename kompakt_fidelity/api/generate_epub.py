import os
import base64
from uuid import uuid4
from ebooklib import epub
from ebooklib.utils import create_pagebreak
from barcode import Code128, EAN13
from barcode.writer import ImageWriter
import qrcode
from .convert import convert

image_style = "display: block; margin-left: auto; margin-right: auto;"

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
    code = str(card["code"])

    if settings["uppercase"]:
      code = code.upper()

    chapter_file = name + ".xhtml"
    filename = str(uuid4()) + ".png"
    files.append(filename)

    card_chapter = epub.EpubHtml(title=name, file_name=chapter_file)

    card_chapter.content = ''

    if settings["includeNames"]:
      card_chapter.content = '<h2 style="text-align: center; margin-bottom: 0;">' + name + "</h2>"

    if card["image"]:
      image_content = base64.b64decode(card["image"].split(',')[1])
      image_filename = str(uuid4()) + ".png"
      files.append(image_filename)

      with open(image_filename, "wb") as f:
        f.write(image_content)
      
      card_chapter.content += '<img alt="[' + name + ']" src="static/' + image_filename + '" style="' + image_style + '"/>'

      with open(image_filename, "rb") as f:
        book.add_item(
          epub.EpubImage(
            uid=(name + "_image"),
            file_name="static/" + image_filename,
            media_type="image/png",
            content=f.read()
          )
        )
      
    card_chapter.content += '<img alt="[' + name + ']" src="static/' + filename + '" style="' + image_style + ' margin-top: 1cm; width: 8cm;"/>'

    if settings["includeCodes"]:
      card_chapter.content += '<p style="text-align: center;">' + code + '</p>'

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
