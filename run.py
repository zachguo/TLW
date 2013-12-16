import re
import glob
from collections import defaultdict
from math import log

# load TELL lexicon
citationDict = {}
for rawHTML in glob.glob('TELL_html_raw/*.txt'):
	with open(rawHTML, 'r') as f:
		s = f.read()
		s = re.subn(r'<TR>', '\n', s)[0]
		s = re.subn(r'</TD><TD>', '\t', s)[0]
		s = re.subn(r'(</?TABLE>|<?TD>|</?STRONG>)', '', s)[0]
		pairs = s.split('\n')
		for p in pairs:
			if p:
				citation,lexeme = p.split('\t')
				if lexeme not in citationDict:
					citationDict[lexeme] = citation
				else:
					if citation != citationDict[lexeme]:
						print rawHTML, citation, citationDict[lexeme] # none

# load word frequency
freqDict = {}
with open('frequencylist/tr-2011/tr.txt', 'r') as f:
	for line in f:
		if line:
			word,freq = line.strip().split(' ')
			freqDict[word] = int(freq)
with open('frequencylist/tr-2012/tr.txt', 'r') as f:
    for line in f:
        if line:
            word,freq = line.strip().split(' ')
            if word not in freqDict:
                freqDict[word] = int(freq)
            else:
                freqDict[word] += int(freq)

# intersection of two sources
useful_words = set(citationDict.keys())&set(freqDict.keys())
print 'TELL:',len(citationDict),'FREQ:',len(freqDict),'Intersection:',len(useful_words)

# calculate well-formedness
def get_ngramIC(useful_words, citationDict, freqDict):
    unigramDict = defaultdict(float)
    bigramDict = defaultdict(float)
    for word in useful_words:
        citation = "#"+citationDict[word]+"#"
        for i in range(len(citation)):
            if i < len(citation)-1 and i:
                unigramDict[citation[i]] += freqDict[word]
                bigramDict[citation[i]+citation[i+1]] += freqDict[word]
            else:
                unigramDict[citation[i]] += freqDict[word]
    print "Finished generating Ngram dictionaries."
    ## smoothing for bigram and trigram: add-one
    gramset = unigramDict.keys()
    for u1 in gramset:
        for u2 in gramset:
            bigramDict[u1+u2] += 0.01
    print "Finished smoothing."
    ICunigramDict = {}
    ICbigramDict = {}
    s = sum(unigramDict.values())
    for unigram in unigramDict:
        ICunigramDict[unigram] = - log(float(unigramDict[unigram])/s,2)
    print " Finished Unigram IC ..."
    s = sum(bigramDict.values())
    for bigram in bigramDict:
        ICbigramDict[bigram] = - log(float(bigramDict[bigram])/s,2)
    print " Finished Bigram IC ..."
    print "Finished calculation of information content."
    return ICunigramDict, ICbigramDict

def cal_wellformedness(target, ICunigramDict, ICbigramDict):
    target = "#"+target+"#" # target should be citation, not lexeme
    wordICunigram = sum([ICunigramDict[char] for char in target])/float(len(target))
    wordICbigram = sum([ICbigramDict[target[i:i+2]] for i in range(len(target)-1)])/float(len(target)-1)
    return wordICunigram, wordICbigram

ICunigramDict, ICbigramDict = get_ngramIC(useful_words, citationDict, freqDict)
wordICunigramDict = {}
wordICbigramDict = {}
for word in useful_words:
	wordICunigram, wordICbigram = cal_wellformedness(citationDict[word], ICunigramDict, ICbigramDict)
	wordICunigramDict[word] = wordICunigram
	wordICbigramDict[word] = wordICbigram

# print out
outUnigram = wordICunigramDict.items()
outBigram = wordICbigramDict.items()
outUnigram.sort(key=lambda x:x[1])
outBigram.sort(key=lambda x:x[1])
with open('output/ICunigram.txt','w') as f:
	for word in outUnigram:
		f.write(word[0]+'\t'+str(word[1])+'\n')
with open('output/ICbigram.txt','w') as f:
	for word in outBigram:
		f.write(word[0]+'\t'+str(word[1])+'\n')
with open('output/TopBottom50.txt','w') as f:
	f.write('Unigram Top 50\tUnigram Bottom 50\tBigram Top 50\tBigram Bottom 50\n')
	for i in range(50):
		f.write(outUnigram[i][0]+'\t'+outUnigram[-(i+1)][0]+'\t'+outBigram[i][0]+'\t'+outBigram[-(i+1)][0]+'\n')
with open('example_korpu.txt', 'r') as f:
    for line in f:
        if line:
            print line.strip(), cal_wellformedness(line.strip(), ICunigramDict, ICbigramDict)[1]