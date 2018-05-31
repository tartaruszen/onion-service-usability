import sys
from Levenshtein import jaro_winkler

f = open(sys.argv[1], 'r')
names = []
for line in f:
    names.append(line.split(",")[0])
f.close()

count = 0
pairs = []
all_pairs = []
for n in names:
    print "Completed: " + str(count)
    for n2 in names:
        x = jaro_winkler(n, n2)
        if x > .90 and n != n2 and ((n,n2) not in pairs) and ((n2,n) not in pairs):
            pairs.append((n,n2))
    count += 1

print len(all_pairs)

f = open(sys.argv[2], 'w')
for p in pairs:
    f.write(p[0] + "," + p[1] + "," + str(jaro_winkler(p[0], p[1])) + "\n")
f.close()

