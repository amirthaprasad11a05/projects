# python3
import sys
def calculate_overlap(a,b,mer):
    for i in range(len(a)-mer+1):
        if b.startswith(a[i:]):
            return len(a)-i
    return 0
def assemble_genome(reads,mer):
    genome=""
    genome+=reads[0]
    first_read=reads[0]
    cur_index=0
    while len(reads)>1:
        cur_read=reads[cur_index]
        reads.pop(cur_index)
        max_overlap=-1
        for j in range(len(reads)):
            overlap=calculate_overlap(cur_read,reads[j],mer)
            if overlap>max_overlap:
                max_overlap=overlap
                cur_index=j
        genome+=reads[cur_index][max_overlap:]
    genome=genome[len(calculate_overlap(reads[0],first_read,mer)):]
    return genome
reads=[]
for line in sys.stdin:
    s=line.strip()
    if len(reads)==0 or reads[-1]!=s:
        reads.append(s)
print(assemble_genome(reads,12))
