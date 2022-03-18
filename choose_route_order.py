# This script reads all of the specified .txt files 
# and parses their contents for keywords.  Then it 
# figures out the files that have the fewest words 
# in common and prints out the file names in that 
# order.
#
# The intent is to create a route-slips ordering
# that avoids having two similar rides next to each
# other, so that people don't complain about riding
# nearly-the-same-ride two weeks in a row.
#
# Usage: 
#
#   python choose_route_order.py *.txt
#
# or (better yet):
#
#   python choose_route_order.py `cat Active_Rides.txt`

import sys
from itertools import permutations

def distance(point1, point2):
    """ Returns the distance between the nodes with the given names """
    return transitionToDistance[point1 + " -> " + point2]

# Returns the total length of the specified path through our route-slips-graph
def CalculatePathLength(nodesList, transitionToDistance):
   ret = 0.0
   for i in range(1, len(nodesList)):
      ret += transitionToDistance[nodesList[i-1] + " -> " + nodesList[i]]
   return ret

def SimplifyToken(t):
   t = t.lower()
   if (len(t) < 3):
      return ""
   if ("north" in t) or ("east" in t) or ("south" in t) or ("west" in t):
      return ""
   if (t.endswith("txt")) or (t.startswith("http")):
      return ""
   return t

def ParseLine(line, words):
   curStr = ""
   for c in line:
      if str.isalpha(c):
         curStr += c
      elif len(curStr) > 0:
         curStr = SimplifyToken(curStr)
         if (len(curStr) > 0):
            words[curStr] = ""
            curStr = ""

   curStr = SimplifyToken(curStr)
   if (len(curStr) > 0):
      words[curStr] = ""

def ParseRouteSlip(fileName):
   words = {}
   fp = open(fileName)
   if (fp != None):
      print("Reading route slip [%s]..." % fileName)
      lines = fp.readlines()
      for line in lines:
         ParseLine(line, words)
      fp.close()
   return words

# Returns the number of unique words that are present in both sets, 
# divided by the unique words in at least one set.
# Thus, if we return 0.0, the two sets are completely disjoint
# or if we returns 1.0 the two sets are identical
# Although in most cases it will be some value in between those two
def CalculateSimilarityPercentage(words1, words2):
   unionOfWords = {}
   intersectionOfWords = {}
   for w1 in words1.keys():
      unionOfWords[w1] = ""
      if (w1 in words2):
         intersectionOfWords[w1] = ""
   for w2 in words2.keys():
      unionOfWords[w2] = ""
      if (w2 in words1):
         intersectionOfWords[w2] = ""
    
   # Paranoia: Avoid potential divide-by-zero
   if (len(unionOfWords) == 0):
      return 1.0    
   return float(len(intersectionOfWords)) / len(unionOfWords)

# Construct a dictionary of type filename -> {words -> ""}
nameToWords = {}
if len(sys.argv) <= 1:
   fileName = "Active_Rides.txt"
   print("No arguments specified, reading %s to get route filenames to use" % fileName)
   fp = open(fileName)
   if (fp != None):
      lines = fp.readlines()
      for line in lines:
         routeFileName = line.strip();
         if len(routeFileName) > 0:
            nameToWords[routeFileName] = ParseRouteSlip(routeFileName)
      fp.close()
   else:
      print("Couldn't open routes file %s" % fileName)
else:
   # If any arguments were specified, we'll assume they are a list of route-slip file names
   for fileName in sys.argv[1:]:
      nameToWords[fileName] = ParseRouteSlip(fileName)

# Calculate the similarity of each route slip to the other route slips
transitionToDistance = {}   # keyStr -> percentage
for fileName1,fileContents1 in nameToWords.items():
   for fileName2,fileContents2 in nameToWords.items():
      if (fileName1 != fileName2):
         transitionToDistance[fileName1 + " -> " + fileName2] = CalculateSimilarityPercentage(fileContents1, fileContents2)
   
print("\nComputing the best sequence for %i route slips..." % len(nameToWords))

# And finally we'll compute the shortest path through all the nodes
# based on the various similarity-percentages between each pair of nodes
minDist  = None
bestPath = None

# Brute force implementation -- guaranteed to find the optimal result
# but will also take way to long to complete if the number of route
# slips is more than 5-10!
# Disabled for now because we usually have 30+ routes to consider.
#for nextPath in permutations(nameToWords.keys()):
#   pathDist = CalculatePathLength(nextPath, transitionToDistance)
#   if ((minDist == None) or (pathDist < minDist)):
#      minDist  = pathDist
#      bestPath = nextPath 

# Greedy implementation -- not guaranteed to return the optimal
# result, but close enough and will finish before the universe ends.
for start in nameToWords.keys():
   remainsToBeVisited = list(nameToWords.keys())
   nextPath = [start]
   remainsToBeVisited.remove(start)
   while len(remainsToBeVisited) > 0:
       nearestNeighbor = min(remainsToBeVisited, key=lambda x: distance(nextPath[-1], x))
       nextPath.append(nearestNeighbor)
       remainsToBeVisited.remove(nearestNeighbor)
   pathDist = CalculatePathLength(nextPath, transitionToDistance)
   if ((minDist == None) or (pathDist < minDist)):
      minDist  = pathDist
      bestPath = nextPath 

# Print out our best result/sequence
print()
if (bestPath != None):
   print("Recommended route-sequence is:")
   for node in bestPath:
      print("   " + node)
else:
   print("No best path found!?")

