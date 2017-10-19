from scanfuncs import *
text = "As yet but knock, breathe, shine and seek to mend."

SM = ScansionMachine()

SM.ParseLine(text)
iambic = True
algorithm1=True

Steps = [('SYLLABLES', SM.ShowSyllables), \
              ('PRELIMINARY MARKS', SM.ShowLexStresses)]
if iambic:
    Steps.append(('CHOOSE ALGORITHM', SM.ChooseAlgorithm))
    if algorithm1:
        Steps.append(('FIRST TESTS', SM.WeirdEnds))
        Steps.append(('FOOT DIVISION', SM.TestLengthAndDice))
    else:
        Steps.append(('LONGEST NORMAL', SM.TryREs))
        Steps.append(('CLEAN UP ENDS', SM.CleanUpRE))
    Steps.append(('PROMOTIONS', SM.PromotePyrrhics))
    Steps.append(('ANALYSIS', SM.HowWeDoing))
else:		# anapestic steps
    Steps.append(('ADJUST STRESSES', SM.GetBestAnapLexes))
    Steps.append(('ANAPESTICS: LINE END', SM.AnapEndFoot))
    Steps.append(('ANAPESTICS: FOOT DIVISION', SM.AnapDivideHead))
    Steps.append(('ANAPESTICS: ANALYSIS', SM.AnapCleanUpAndReport))

for step in Steps:
	print step[0]
	(scanline, result) = step[1]()
	print text
	print scanline
	print result

print SM.allSyls	
