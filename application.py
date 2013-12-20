#!usr/bin/python2.7

from flask import Flask, render_template, request, escape
from core import TLW

application = app = Flask(__name__) # AWS mod_wgsi looks for "application"
app.debug=True # only in dev

@app.route('/', methods=['GET', 'POST'])
def demo():
	if request.method == 'POST':
		tlw = TLW.TLW()
		wordICunigram, wordICbigram, error = '', '', ''
		if 'lexeme' in request.form:
			lexeme = escape(request.form['lexeme']).strip()
			if lexeme:
				if lexeme.encode('utf-8') in tlw.citationDict:
					wordICunigram, wordICbigram = tlw.cal_wellformedness(tlw.citationDict[lexeme.encode('utf-8')])
				else:
					error = "Sorry, the lexeme you entered doesn't exist in our corpus. Please try its citation instead."
		if 'citation' in request.form:
			citation = escape(request.form['citation']).strip()
			if citation:
				try:
					wordICunigram, wordICbigram = tlw.cal_wellformedness(citation.encode('utf-8'))
				except:
					error = "Invalid citation."
		return render_template("_base.html", wordICunigram=wordICunigram, wordICbigram=wordICbigram, error=error)
	else:
	    return render_template("_base.html")

if __name__ == '__main__':
    app.run()