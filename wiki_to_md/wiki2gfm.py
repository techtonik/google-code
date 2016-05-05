# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tool to convert Google Code Wiki files to GitHub-flavored Markdown.

  Reference for Google Code Wiki:
      https://code.google.com/p/support/wiki/WikiSyntax

  Reference for Github-flavored Markdown:
      https://help.github.com/articles/github-flavored-markdown

  The conversion process is not always directly possible; for example,
  wiki pragma statements have no direct equivalent for GFM. In cases
  where no direct conversion can be made, or the input may have unexpected
  output, a warning will be issued.
"""
import argparse

import codecs
import os
import sys

from impl.converter import Converter
from impl.formatting_handler import FormattingHandler
from impl.pragma_handler import PragmaHandler


def PrintWarning(input_line, message):
  """Print a warning.

  When a conversion cannot be done or may be unreliable/inexact,
  a warning will be printed to stdout notifying the user of this.

  Args:
    input_line: The line number this warning occurred on.
    message: The warning message.
  """
  print u"Warning (line {0} of input file):\n{1}\n".format(input_line, message)


def main(args):
  """The main function.

  Args:
     args: The command line arguments.
  """
  parser = argparse.ArgumentParser(
      description="Converts a Google Code wiki page to GitHub-flavored "
      "Markdown.")

  parser.add_argument("--input_file", required=True,
                      help="The input Google Code Wiki file")
  parser.add_argument("--output_file", required=True,
                      help="The output GitHub-flavored Markdown file")
  parser.add_argument("--project", required=False,
                      help="The name of the project for the Wiki")
  parser.add_argument("--wikipages_list", nargs="*",
                      help="The list of wiki pages that are assumed to exist "
                      "for the purpose of auto-linking to other pages")
  parser.add_argument("--wikipages_path", nargs="*",
                      help="The list of paths containing wiki pages that are "
                      "assumed to exist for the purpose of auto-linking to "
                      "other pages")
  symmetric_headers_help = ("Controls if the output of header level "
                            "indicators are made symmetric. E.g. '### Header' "
                            "if disabled, and '### Header ###' if enabled")
  parser.add_argument("--symmetric_headers", dest="symmetric_headers",
                      action="store_true", help=symmetric_headers_help)
  parser.add_argument("--no_symmetric_headers", dest="symmetric_headers",
                      action="store_false", help=symmetric_headers_help)
  parser.add_argument("--summary_italic", dest="summary_italic",
                      action="store_true", help="convert #summary to italic")
  parser.set_defaults(feature=False)

  parsed_args, unused_unknown_args = parser.parse_known_args(args)

  with codecs.open(parsed_args.input_file, "rU", "utf-8") as input_stream:
    with codecs.open(parsed_args.output_file, "wU", "utf-8") as output_stream:
      # Create the master list of wiki pages assumed to exist.
      wikipages = parsed_args.wikipages_list or []
      wikipages.append(parsed_args.input_file)

      if parsed_args.wikipages_path:
        # Add all the .wiki files in all the given paths.
        for path in parsed_args.wikipages_path:
          for f in os.listdir(path):
            if f.endswith(".wiki"):
              wikipages.append(f[:-len(".wiki")])

      # Fill this will a mapping from Google Code issue
      # to GitHub issue to automate that conversion.
      issue_map = {}

      # Prepare the handlers and converter.
      pragma_handler = PragmaHandler(
          PrintWarning,
          parsed_args.summary_italic)
      formatting_handler = FormattingHandler(
          PrintWarning,
          parsed_args.project,
          issue_map,
          parsed_args.symmetric_headers)
      converter = Converter(
          pragma_handler,
          formatting_handler,
          PrintWarning,
          parsed_args.project,
          wikipages)

      # And perform the conversion.
      converter.Convert(input_stream, output_stream)


if __name__ == "__main__":
  main(sys.argv)
