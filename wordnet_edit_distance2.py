from nltk.corpus import wordnet as wn
from nltk.corpus import semcor
import argparse
import numpy as np
import random
import semcor_chunk as sc

#debug function to print out the matrix
#taken from https://stackoverflow.com/questions/13214809/pretty-print-2d-python-list
def print_matrix(matrix):
	s = [[str(e) for e in row] for row in matrix]
	lens = [max(map(len, col)) for col in zip(*s)]
	fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
	table = [fmt.format(*row) for row in s]
	print ('\n'.join(table))

# Returns the cost of inserting a word
def ins_cost(word):
    return 1

# Returns the cost of deleting a word
def del_cost(word):
    return 1

# Returns the cost of substituting word1 with word2
def sub_cost(word1, word2):
    if sc.semcor_chunk(word1).get_words()[0]==word2:
        return 0
    sw1=sc.semcor_chunk(word1).get_syn_set()
    ss2=wn.synsets(word2)
    if sw1 is None or len(ss2)==0:
        return 1
    maxSimilarity=0
    if sim=='path':
        for ss in ss2:
            similarity=sw1.path_similarity(ss)
#            print(similarity)
            if similarity==None:
                return 1
            elif similarity>maxSimilarity:
                maxSimilarity=similarity
#        print('MS: '+str(maxSimilarity))
        return 1-maxSimilarity
    elif sim=='wup':
        for ss in ss2:
            similarity=sw1.path_similarity(ss)
            if similarity==None:
                return 1
            elif similarity>maxSimilarity:
                maxSimilarity=similarity
#        print(word1+', '+word2+', '+str(maxSimilarity))
        return 1-maxSimilarity
    return 1


#...TODO Parse arguments and load semcor sentences
sents=semcor.sents()
tsents=semcor.tagged_sents(tag='sem')
parser=argparse.ArgumentParser()
parser.add_argument('ndx1', type=int, action='store', default='1')
parser.add_argument('ndx2', type=int, action='store', default='1')
parser.add_argument('-sim', dest='sim', action='store', default='1')
args = parser.parse_args()
sim=args.sim
ndx1=args.ndx1
ndx2=args.ndx2

sent1 = sents[ndx1]
sent2 = tsents[ndx2]
#sent1=sents[random.randint(0,len(sents))]
#sent2=tsents[random.randint(0,len(sents))]
#sent1=['A', 'Z', 'Q', 'R', 'X', 'A']
#sent2=['A', 'Z', 'J', 'Q', 'R', 'Y']


#print(len(sent1))
print(sent1)
#print(len(sent2))
print(sent2)

n = len(sent1)
m = len(sent2)


cmatrix = np.ndarray((n+1,m+1), dtype=float)
cmatrix[:,:]=-1

ematrix = np.ndarray((n+1,m+1),dtype='a256')
ematrix[:,:]=''
ematrix[0,:]='INS 1'
ematrix[:,0]='DEL 1'
ematrix[0,0]=''
# Store the operations: '=' (words match), 'INS', 'DEL', 'SUB'

#TODO Set up row and column 0 in accordance with the algorithm
for i in range(0, n+1):
	cmatrix[i,0]=i

for i in range(0, m + 1):
	cmatrix[0,i]=i
#print(cmatrix)

# Populate the matrices with dynamic programming
for col in range(1, n + 1):
    for row in range(1, m + 1):
#        print(sent1[col-1])
#        print(sent2[row-1])
#        print('\n')
#        print(sub_cost(sent2[row-1],sent1[col-1]))
        value=min(ins_cost(sent2[row-1])+cmatrix[col, row-1],
         del_cost(sent1[col-1])+cmatrix[col-1, row],
         sub_cost(sent2[row-1],sent1[col-1])+cmatrix[col-1, row-1])
        cmatrix[col, row]=value
        op=''
        if sub_cost(sent2[row-1],sent1[col-1])+cmatrix[col-1, row-1]==value and sub_cost(sent2[row-1],sent1[col-1])==0:
            s='= 0 '
#            print('S: '+s)
            op+=s #+ sent1[col-1] + ' ' + sent2[row-1]
        elif sub_cost(sent2[row-1],sent1[col-1])+cmatrix[col-1, row-1]==value and sub_cost(sent2[row-1],sent1[col-1])!=0:
            s='SUB '+str(sub_cost(sent2[row-1],sent1[col-1]))+' '
#            print('S: '+s)
            op+=s #+ sent1[col-1] + ' ' + sent2[row-1]
        elif ins_cost(sent2[row-1])+cmatrix[col, row-1]==value:
            s='INS '+str(ins_cost(sent2[row-1]))+' '
#            print('S: '+s)
            op+=s #+ sent2[row-1]
        elif del_cost(sent1[col-1])+cmatrix[col-1, row]==value:
            s='DEL '+str(del_cost(sent1[col-1]))+' '
#            print('S: '+s)
            op+=s #+ sent1[col-1]
#        print(np.bytes_(op))
        ematrix[col,row]=np.bytes_(op)
		# Your solution should include calls to ins_cost(), del_cost(), and sub_cost()


#for r in ematrix:
#    print(r.tolist())
#print('\n')
#for r in cmatrix:
#    print(r.tolist())
# Output the minimum cost computed by the edit distance algorithm
print(cmatrix[n,m])

# Output the sequence of operation types to be performed on sentence1 that transform 
# it to sentence2 with minimum cost. Each operation should be followed by its individual cost.
# E.g., '= 0 = 0 INS 1 = 0 SUB 1 DEL 1' for the Levenshtein distance 
# if sentence1 is 'A Z Q R X A' and sentence2 is 'A Z J Q R Y'.
col=n
row=m
ops=[ematrix[col,row].decode('UTF-8')]
#print(ematrix[col,row].decode('UTF-8'))
while row!=0 or col!=0:
#    print(str(col)+', '+str(row))
    if ematrix[col,row].decode('UTF-8')[0:3]=='SUB' or ematrix[col,row].decode('UTF-8')[0]=='=':
        row-=1
        col-=1
    elif ematrix[col,row].decode('UTF-8')[0:3]=='INS':
        row-=1
    elif ematrix[col,row].decode('UTF-8')[0:3]=='DEL':
        col-=1
    ops=[ematrix[col,row].decode('UTF-8')]+ops
#    print(ops)
print(' '.join(ops))
