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
   for i in xrange(1, len(nodesList)):
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
      print "Reading route slip [%s]..." % fileName
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
      if (words2.has_key(w1)):
         intersectionOfWords[w1] = ""
   for w2 in words2.keys():
      unionOfWords[w2] = ""
      if (words1.has_key(w2)):
         intersectionOfWords[w2] = ""
    
   # Paranoia: Avoid potential divide-by-zero
   if (len(unionOfWords) == 0):
      return 1.0    
   return float(len(intersectionOfWords)) / len(unionOfWords)

nameToWords = {}
for fileName in sys.argv[1:]:
   nameToWords[fileName] = ParseRouteSlip(fileName)

transitionToDistance = {}
for fileName1,fileContents1 in map(None, nameToWords.keys(), nameToWords.values()):
   for fileName2,fileContents2 in map(None, nameToWords.keys(), nameToWords.values()):
      if (fileName1 != fileName2):
         transitionToDistance[fileName1 + " -> " + fileName2] = CalculateSimilarityPercentage(fileContents1, fileContents2)
   
print "\nComputing the best sequence for %i route slips..." % len(nameToWords)

# And finally we'll compute the shortest path through all the nodes in the
# network via Sheer Brute Force
minDist  = None
bestPath = None

# Brute force implementation -- will find the optimal result
# but will also take way to long to complete if the number of route
# slips is more than 5-10!

#for nextPath in permutations(nameToWords.keys()):
#   pathDist = CalculatePathLength(nextPath, transitionToDistance)
#   if ((minDist == None) or (pathDist < minDist)):
#      minDist  = pathDist
#      bestPath = nextPath 


# Greedy implementation -- not guaranteed to return the optimal
# result, but close enough and will finish before the universal
# ends.
for start in nameToWords.keys():
   remainsToBeVisited = nameToWords.keys()
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

print
if (bestPath != None):
   #print "Minimum path length was: ", minDist
   print "Best path was: "
   for node in bestPath:
      print "   " + node
else:
   print "No best path found!?"

