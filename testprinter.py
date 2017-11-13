"""This file will be used to test the textprint package"""
from textprint.section import Section
from textprint.textprinter import TextPrinter

section = Section(None)
printer = TextPrinter([section])

section.print(printer, "hi")