# scanmain.py 1.1
#
# the Scandroid
# Copyright (C) 2005 Charles Hartman
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the 
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version. See the accompanying file, gpl.txt, for full
# details.
# OSI Certified Open Source Software
#
# Main module of the Scandroid, the Python version of the verse scanner.
# This module handles the wxPython frame and most of the interface, 
# including the menus and button-presses that control everything. The Frame 
# owns a ScansionMachine that does all the interesting work.


import wx
import string, os, sys, sre
import random
from math import modf
from scanstrings import *				# some global texts & the Explainer
from scanstc import *					# editors for subwindows
from scanfuncs import *				# the Scansion Machine

# global to this module:
FORKSTEP = 3			# in iambics, the step at which the two algorithms divide
dummyevent = wx.MouseEvent(wx.wxEVT_LEFT_UP)		# to call button directly

class ScandroidFrame(wx.Frame):
## - - - - - initializations
    def __init__(self, parent, ID, title):

        # initialize our data members and helpers
        self.SM = ScansionMachine()		# central engine of scansion work
        
        self.Metron = 2				# initial assumption:
        self.LineFeet = 5			#   iambic pentameter
        self.LineFeetSet = True
        self.SM.SetLineFeet(5, True)
        self.SetupScansionSteps()		# inc some more data items
   
       
    def SetupScansionSteps(self, iambic=True, algorithm1=True):
        """Match a sequence of step names with function names.
        
        By default, initialize the sequence as per iambic Algorithm 1. It can 
        be switched to Algorithm 2 for each iambic line any time before 
        FORKSTEP (caller is responsible for checking this): at random, as 
        forced by the user, or as a switch in desperation when an alg fails.
        Steps after 1 can be switched from iambic to anapestic.
        Switch arguments allow these options.
        """
        self.Steps = [('SYLLABLES', self.SM.ShowSyllables), \
                      ('PRELIMINARY MARKS', self.SM.ShowLexStresses)]
        if iambic:
            self.Steps.append(('CHOOSE ALGORITHM', self.SM.ChooseAlgorithm))
            if algorithm1:
                self.Steps.append(('FIRST TESTS', self.SM.WeirdEnds))
                self.Steps.append(('FOOT DIVISION', self.SM.TestLengthAndDice))
            else:
                self.Steps.append(('LONGEST NORMAL', self.SM.TryREs))
                self.Steps.append(('CLEAN UP ENDS', self.SM.CleanUpRE))
            self.Steps.append(('PROMOTIONS', self.SM.PromotePyrrhics))
            self.Steps.append(('ANALYSIS', self.SM.HowWeDoing))
        else:		# anapestic steps
            self.Steps.append(('ADJUST STRESSES', self.SM.GetBestAnapLexes))
            self.Steps.append(('ANAPESTICS: LINE END', self.SM.AnapEndFoot))
            self.Steps.append(('ANAPESTICS: FOOT DIVISION', self.SM.AnapDivideHead))
            self.Steps.append(('ANAPESTICS: ANALYSIS', self.SM.AnapCleanUpAndReport))


    def ShowTextLine(self, txt, num): 

        self.linetext = txt.strip()
        self.lineNum = num			# where to put scansion when done
        self.CurrentStep = 0			# (re)start the procedure
        if self.Metron == 2:			# iambic-only preparations
            if random.randint(0,1): self.whichAlgorithm = 1	# begin at random
            else: self.whichAlgorithm = 2
            self.SetupScansionSteps(iambic=True, algorithm1=(self.whichAlgorithm==1))
            self.OneIambicAlgFailed = False
        try:
            self.SM.ParseLine(self.linetext)



## - - - - - button & other routines for treatment of individual lines
    def OnStepButton(self, evt):
        """Perform next scansion setp in self.Steps (indexed by self.CuurentStep)"""

        (scanline, result) = self.Steps[self.CurrentStep][1]()

        if self.CurrentStep == 2 and self.Metron == 2:
            if result: self.whichAlgorithm = 1			# arbitrary T/F code to put alg.
            else: self.whichAlgorithm = 2			#   into succeed/fail return
            # substitute failure test; only for too-short lines if linefeet not set
            if scanline:
                self.SetupScansionSteps(iambic=True, algorithm1=(self.whichAlgorithm == 1))
                self.ShowScanLine(scanline)
                self.scanMenu.Enable(204, True)
                self.scanMenu.Enable(205, True)
                self.CurrentStep += 1
            else: self.CurrentStep = len(self.Steps)		# stop
        else:				# ALL steps except iambic ChooseAlgorithm
            if scanline: 
#		self.ShowScanLine(scanline, showAlg=True)		# FOR TESTING ONLY!!
                self.ShowScanLine(scanline)
            if not result:		# some step FAILED
                if self.Metron == 2 and self.OneIambicAlgFailed:
                    self.E.Explain("\n\nAbject failure of both iambic methods!\n")
                    self.ShowScanLine(self.SM.P.GetScanString() + '    ***')
                    self.CurrentStep = len(self.Steps)		# quit
                elif self.Metron == 3:
                    self.ShowScanLine(self.SM.P.GetScanString() + '    ***')
                    self.CurrentStep = len(self.Steps)		# quit
                else:
                    self.OneIambicAlgFailed = True	# orig. set in ShowTextLine
                    scanline = self.SM.RestartNewIambicAlg(self.E, self.whichAlgorithm,
                                                           scanline)
                    self.ShowScanLine(scanline)
                    if self.whichAlgorithm == 1: self.whichAlgorithm = 2
                    else: self.whichAlgorithm = 1
                    self.SetupScansionSteps(iambic=True, algorithm1=(self.whichAlgorithm == 1))
                    self.CurrentStep = FORKSTEP
            else:
                self.scanMenu.Enable(204, False)
                self.scanMenu.Enable(205, False)
                self.CurrentStep += 1

 


## - - - - - establish major context for scansion work
    def DeduceParameters(self, forceiamb=False, forceanap=False):
        """When text is loaded, read multiple lines; find metron and linelength.
        
        Read all lines (up to a dozen); call SM to try a quick scansion of each as 
        iambic (both algorithms, but without stress-resolution options) and as 
        anapestic to decide consistent metron (2 or 3). Guess line-length in feet 
        under each assumption; if close average, declare constant length. 
        Set three flags as distributable globals: Metron, LineFeet, and 
        LineFeetSet (True *or* False). Metron is always set (for better or worse).
        
        Added "force" flags so this will be callable from ForceMetron. With one
        or the other set, skip non-pertinent parts.
        """
        textlines = self.WholeText.GetLineCount()
        iambLens = []
        anapLens = []
        iambCompTotal = anapCompTotal = 0
        linesToSample = 12
        i = 0		# sample min of all lines (textlines) or linesToSample (break)
        self.SM.SetLineFeet(5, False)		# unset "linefeetset" for tests
        for linex in range(textlines):	# parse each line, try various scansions
            if i >= linesToSample: break
            line = self.WholeText.GetLine(linex)
            if len(line) < 5 or line[:1] == '\t': 		# can't use line[0] with or!
                continue	# skip a title or other non-verse
            i += 1	# count of "real" lines
            self.SM.ParseLine(line)
            if not forceanap:
                try:
                    (score, length) = self.SM.ChooseAlgorithm(self.E, deducingParams=True)
                except: self.ErrorMessage(self.SM.ChooseAlgorithm, self.SM.P.GetMarks())
                iambCompTotal += score
                if score < 100: iambLens.append(length)
            if not forceiamb:
                try:
                    (score, length) = self.SM.GetBestAnapLexes(self.E, deducingParams=True)
                except: self.ErrorMessage(self.SM.GetBestAnapLexes, self.SM.P.GetMarks())
                anapCompTotal += score
                if score < 100: anapLens.append(length)
        if not forceiamb and not forceanap:
            if iambCompTotal < anapCompTotal:
                self.Metron = 2
                theLengths = iambLens
            else:
                self.Metron = 3
                theLengths = anapLens
            self.SetupScansionSteps(iambic=(self.Metron==2))
        
        self._setLineLengthIfPossible(theLengths)
        self.SM.SetLineFeet(self.LineFeet, self.LineFeetSet)
        self.UpdateStatusBar(self.Metron, self.LineFeet, self.LineFeetSet)
    
    def _setLineLengthIfPossible(self, theLengths):
        """If there's a clear average, set length and lengthset"""
        total = sum(theLengths)
        (frac, integ) = modf(float(total) / len(theLengths))
        if frac > 0.8:				# probably about right
            self.LineFeet = int(integ) + 1
            self.LineFeetSet = True
        elif frac < 0.2:
            self.LineFeet = int(integ)
            self.LineFeetSet = True
        else: self.LineFeetSet = False

    def ForceAlg(self, evt):
        """Menu-choice to override automatic choice of algorithm for iambics.
        
        This would have no effect (be cancelled out) if chosen before the Choose
        Algorithm step. After just past that step it would produce chaos because
        of conflicting work on the line. To enforce this narrow window, the menu item
        and keypress are disabled except at the end of that crucial step.
        """
        which = evt.GetId()
        if which == 204:
            self.whichAlgorithm = 1
            self.E.Explain("\n\nAlgorithm 1 forced")
        else: 
            self.whichAlgorithm = 2
            self.E.Explain("\n\nAlgorithm 2 forced")
        self.SetupScansionSteps(iambic=True, algorithm1=(self.whichAlgorithm == 1))

    def ForceMetron(self, evt):
        """Menu-only choice to force scansion iambic/anapestic till next Load."""
        self.OnCancelBtn(dummyevent)	# before msg or will be erased
        which = evt.GetId()
        if which == 207:
            self.Metron = 3
            self.DeduceParameters(forceanap=True)
            self.E.Explain("\nForced switch to anapestic scansion\n")
            self.SetupScansionSteps(iambic=False)
        else:
            self.Metron = 2
            self.DeduceParameters(forceiamb=True)
            self.E.Explain("\nForced switch to iambic scansion\n")
            self.SetupScansionSteps(iambic=True)
        if self.LineFeetSet:
            self.E.Explain("implied line length is %s feet\n\n" % self.LineFeet)
        else: self.Explain("implied line length is variable\n\n")

