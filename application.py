#!usr/bin/python2.7

from flask import Flask, render_template, request, escape
from core import TLW

application = app = Flask(__name__) # AWS mod_wgsi looks for "application"
# app.debug=True # only in dev

@app.route('/', methods=['GET', 'POST'])
def demo():
	if request.method == 'POST':
		tlw = TLW.TLW()
		wordICunigram, wordICbigram, wordICunigram_std, wordICbigram_std, error, lexeme, citation = '','','','','','',''
		if 'lexeme' in request.form:
			lexeme = escape(request.form['lexeme']).strip()
			if lexeme:
				if lexeme.encode('utf-8') in tlw.citationDict:
					citation = tlw.citationDict[lexeme.encode('utf-8')]
					wordICunigram, wordICbigram = tlw.cal_wellformedness(citation)
					citation = citation.decode('utf-8')
				else:
					error = "Sorry, the lexeme you entered doesn't exist in our corpus. Please try its citation instead."
		if 'citation' in request.form:
			citation = escape(request.form['citation']).strip()
			if citation:
				try:
					wordICunigram, wordICbigram = tlw.cal_wellformedness(citation.encode('utf-8'))
				except:
					error = "Invalid citation."
		# if wordICunigram:
		# 	wordICunigram_std = -(wordICunigram - 4.325948)/0.3538684 # standardized value
		if wordICbigram:
			wordICbigram_std = -(wordICbigram - 11.38079)/1.537547 # standardized value
		return render_template("_base.html", wordICbigram=wordICbigram, wordICbigram_std=wordICbigram_std, error=error, lexeme=lexeme, citation=citation)
	else:
	    return render_template("_base.html")

if __name__ == '__main__':
    app.run()