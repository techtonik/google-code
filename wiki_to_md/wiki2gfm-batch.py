#!/usr/bin/env python

# Converts Google Code wiki pages to GitHub flavored Markdown. Unlike
# convert-repo.sh shell script, this doesn't remove or commit files.
USAGE="""Bulk converter for wiki pages.

wiki2gfm-batch.py <path-to-dir>
"""

import glob
import sys

import wiki2gfm


if not sys.argv[1:]:
  sys.exit(USAGE)

ROOT=sys.argv[1]

for wikifile in glob.glob("{}/*.wiki".format(ROOT)):
  mdfile = wikifile[:-5] + ".md"

  print("**************************\n"
        "Converting wiki: {}\n"
        "To Markdown    : {}\n"
        "**************************\n".format(wikifile, mdfile))

  wiki2gfm.main(['--input_file='+wikifile, '--output_file='+mdfile])

  print("done\n\n")
