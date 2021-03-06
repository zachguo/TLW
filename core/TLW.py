#!usr/bin/python2.7

import re, glob
from collections import defaultdict
from math import log
try:
    import cPickle as pickle
except:
    import pickle

class TLW():
    # 'TLW' = 'Turkish Lexicon Wellformedness'

    def __init__(self, isToken):
        self.isToken = isToken
        self.citationDict, self.freqDict = self.load_data()
        self.ICunigramDict, self.ICbigramDict = self.get_ngramIC()

    def load_data(self):
        # try loading from cache first
        try:
            addon = '_token' if self.isToken else '_type'
            with open("core/cache/citationDict"+addon, "r") as f:
                citationDict = pickle.load(f)
            with open("core/cache/freqDict"+addon, "r") as f:
                freqDict = pickle.load(f)

        except:
            # load TELL lexicon
            # citationDict maps pronunciations to orthographies
            citationDict = {}
            for rawHTML in glob.glob('core/TELL_html_raw/*.txt'):
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
            						print rawHTML, citation, citationDict[lexeme] # none should exist

            freqDict = {}
            if self.isToken:
                # load word frequency
                # freqDict maps frequency to orthographies
                with open('core/frequencylist/tr-2011/tr.txt', 'r') as f:
                	for line in f:
                		if line:
                			word,freq = line.strip().split(' ')
                			freqDict[word] = int(freq)
                with open('core/frequencylist/tr-2012/tr.txt', 'r') as f:
                    for line in f:
                        if line:
                            word,freq = line.strip().split(' ')
                            if word not in freqDict:
                                freqDict[word] = int(freq)
                            else:
                                freqDict[word] += int(freq)

                # intersection of two sources
                useful_words = set(citationDict.keys())&set(freqDict.keys())

                # reduce citationDict and freqDict to only useful_words
                citationDict = {word:citationDict[word] for word in useful_words}
                freqDict = {word:freqDict[word] for word in useful_words}
            else:
                # type-based analysis, each word has same frequency: 1
                freqDict = {word:1 for word in citationDict}

            # print status
            print 'Number of words:',len(citationDict)

            # save to cache
            addon = '_token' if self.isToken else '_type'
            with open("core/cache/citationDict"+addon, "w") as f:
                pickle.dump(citationDict, f)
            with open("core/cache/freqDict"+addon, "w") as f:
                pickle.dump(freqDict, f)

        return citationDict, freqDict

    # calculate well-formedness
    def get_ngramIC(self):
        try:
            addon = '_token' if self.isToken else '_type'
            with open("core/cache/ICunigramDict"+addon, "r") as f:
                ICunigramDict = pickle.load(f)
            with open("core/cache/ICbigramDict"+addon, "r") as f:
                ICbigramDict = pickle.load(f)

        except:
            unigramDict = defaultdict(float)
            bigramDict = defaultdict(float)
            for word in self.citationDict:
                citation = "#"+self.citationDict[word]+"#"
                for i in range(len(citation)):
                    if i < len(citation)-1 and i:
                        unigramDict[citation[i]] += self.freqDict[word]
                        bigramDict[citation[i]+citation[i+1]] += self.freqDict[word]
                    else:
                        unigramDict[citation[i]] += self.freqDict[word]
            print "Finished generating Ngram dictionaries."
            ## smoothing for bigram and trigram: add 0.01
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
            # save to cache
            addon = '_token' if self.isToken else '_type'
            with open("core/cache/ICunigramDict"+addon, "w") as f:
                pickle.dump(ICunigramDict, f)
            with open("core/cache/ICbigramDict"+addon, "w") as f:
                pickle.dump(ICbigramDict, f)

        return ICunigramDict, ICbigramDict

    def cal_wellformedness(self, target, method="citation"): # another method, "lexeme"
        if method == "lexeme":
            if target in citationDict:
                target = citationDict[target]
            else:
                return None, None # lexeme doesn't exist in citationDict
        target = "#"+target+"#" # target should be citation, not lexeme
        wordICunigram = sum([self.ICunigramDict[char] for char in target])/float(len(target))
        wordICbigram = sum([self.ICbigramDict[target[i:i+2]] for i in range(len(target)-1)])/float(len(target)-1)
        return wordICunigram, wordICbigram

    def get_IC_for_all_words(self):
        wordICunigramDict = {}
        wordICbigramDict = {}
        for word in self.citationDict:
        	wordICunigram, wordICbigram = self.cal_wellformedness(self.citationDict[word])
        	wordICunigramDict[word] = wordICunigram
        	wordICbigramDict[word] = wordICbigram
        return wordICunigramDict, wordICbigramDict

    def output_top50(self):
        addon = '_token' if self.isToken else '_type'
        wordICunigramDict, wordICbigramDict = self.get_IC_for_all_words()
        # print out
        outUnigram = wordICunigramDict.items()
        outBigram = wordICbigramDict.items()
        outUnigram.sort(key=lambda x:x[1])
        outBigram.sort(key=lambda x:x[1])
        with open('core/output/ICunigram'+addon+'.csv','w') as f:
        	for word in outUnigram:
        		f.write(word[0]+','+str(word[1])+'\n')
        with open('core/output/ICbigram'+addon+'.csv','w') as f:
        	for word in outBigram:
        		f.write(word[0]+','+str(word[1])+'\n')
        with open('core/output/TopBottom50'+addon+'.csv','w') as f:
        	f.write('Unigram Top 50,Unigram Bottom 50,Bigram Top 50,Bigram Bottom 50\n')
        	for i in range(50):
        		f.write(outUnigram[i][0]+','+outUnigram[-(i+1)][0]+','+outBigram[i][0]+','+outBigram[-(i+1)][0]+'\n')

    def output_customized_wordlist(self, filepath='core/exp/both.txt', method="citation"):
        with open(filepath, 'r') as f:
            for line in f:
                if line:
                    line = line.strip()
                    wordICunigram, wordICbigram = self.cal_wellformedness(line, method=method)
                    print 'Word:', line, ', UIC:', wordICunigram, ', BIC:', wordICbigram

