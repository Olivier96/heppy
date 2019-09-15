import os, sys
import ROOT

#creer chain object
ch = ROOT.TChain("events","events") # de naam van de tree is belangrijk! Dat is hoe root die in the file vindt!

# voeg de files toe
ch.Add("tree.root")

# print wat er in die tree zit
ch.Print()

# Draw a distribution
ch.Draw("misenergy_pt")
