# This script reads a specified .txt file from stdin
# and outputs a corresponding .csv file to stdout
# 
# The CSV file will contain (N*copies), and represent
# N copies of the route slip.  That way it is possible
# to print extra copies of the route slip without 
# using up an extra sheet of paper for every extra copy.
#
# Usage: 
#
#   python <some_route_slip_file.txt >some_route_slip_file.csv
#

import sys

# Just a cheap hack so we don't have to deal with escaping commas or quotes
def SanitizeString(s):
   if (s.startswith("http")):
      return ""   # including the URLs in the route slips makes them too wide
   return s.replace(',', ';').replace('"', "'")

# Returns the passed-in string, but sanitized and with quotes around it
def SanitizeAndQuoteString(s):
   return SanitizeString(s)

seenBlankLine = False
numCopies     = 3

for inLine in sys.stdin:
   inLine = inLine.strip()
   if seenBlankLine:
      toks = inLine.split()
      if len(toks) > 0:
         theRest = ' '.join(toks[1:])
         outLine = ''
         for copyIdx in range(0, numCopies):
            if len(outLine) > 0:
               outLine += ", "
            outLine += SanitizeAndQuoteString(toks[0][0:7])
            outLine += ', ' + SanitizeAndQuoteString(theRest)
         print outLine
   elif len(inLine) > 0:
      outLine = ''
      for copyIdx in range(0, numCopies):
         if len(outLine) > 0:
            outLine += ', '
         outLine += SanitizeAndQuoteString('') + ', ' + SanitizeAndQuoteString(inLine)
      print outLine
   else:
      seenBlankLine = True
