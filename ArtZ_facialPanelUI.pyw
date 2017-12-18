#!/usr/bin/env python
#-*- coding: UTF-8 -*-
# Author:   Zhang Shengxin --<EMail: 360418420@qq.com || zsxaa--12@163.com>
# Purpose: 
# Created: 2016/7/5

__version__ = '1.4'
__status__  = "beta"
__date__    = "2015/08/13"
__using__   = '''

'''
__scriptName__ =  'ArtZ_facialPanelUI'


import sys
import unittest
import  maya.cmds as mc
import ArtZ_facial.BlendShapesObject

mainWin =  'FacialPanelWin'
########################################################################
class ArtZ_facailPanelUi():
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.CreateTargets=ArtZ_facial.BlendShapesObject.GenerateAllTargets()
        #self.TargetsCheckOnCommand1 = 'CreateTargets=ArtZ_facial.BlendShapesObject.GenerateAllTargets()\nCreateTargets.AllTargets(1)'
        
        #self.TargetsCheckOnCommand2 = 'CreateTargets=ArtZ_facial.BlendShapesObject.GenerateAllTargets()\nCreateTargets.AllTargets(2)'
        
        #self.TargetsCheckOnCommand3 = 'CreateTargets=ArtZ_facial.BlendShapesObject.GenerateAllTargets()\nCreateTargets.AllTargets(3)'
        
        #self.TargetsCheckOnCommand4 = 'CreateTargets=ArtZ_facial.BlendShapesObject.GenerateAllTargets()\nCreateTargets.AllTargets(4)'
        
        #self.ImportPanelCommand = 'ImportPanel=ArtZ_facial.BlendShapesObject.GloImportPanel()\nImportPanel.GloImportTem()'
        
        #self.ConnectBlendToPanelCommand = 'ConnectBlend=ArtZ_facial.BlendShapesObject.DriverAllToDrivenAll()\nConnectBlend.DriverAllToAll()'                
        pass
    def deleteUI(self):
        """"""
        if mc.window(mainWin, ex=1):
            mc.deleteUI(mainWin, window=1)
        if mc.windowPref(mainWin, ex=1):
            mc.windowPref(mainWin, r=1)
    #----------------------------------------------------------------------
    def installSystemUi(self):
        """"""
        self.deleteUI()
        self.mainWin =  mc.window(mainWin, t=mainWin, wh = (100, 110))
        self.createUi()
        mc.showWindow(self.mainWin)
    #----------------------------------------------------------------------
    def createUi(self):
        """"""

        self.com =  mc.columnLayout(adj = True, w = 300)
        self.text =  mc.text(l = 'CreateTarget:')
        self.separator01 =  mc.separator(st = 'in', h=5)
        self.checkBoxGrp =  mc.checkBoxGrp('TargetsCheckBox',ncb = 4, la4 = ['Brow', 'Eye', 'Nose', 'Mouth'], columnWidth4 =  [70, 70, 70, 70],onCommand1=self.TargetsCheckOnCommand1,onCommand2=self.TargetsCheckOnCommand2,onCommand3=self.TargetsCheckOnCommand3,onCommand4=self.TargetsCheckOnCommand4)
        self.separator02 =  mc.separator(st = 'in', h=5)
        self.separator03 =  mc.separator(st = 'in', h=5)
        self.Import =  mc.button(l = 'Import FacialPanel',c = self.ImportPanelCommand)
        self.separator04  =  mc.separator(st = 'in', h=5)
        self.separator05  =  mc.separator(st = 'in', h=5)        
        self.Connect =  mc.button(l = 'Connect Target To Panel',c =self.ConnectBlendToPanelCommand)
    #----------------------------------------------------------------------
    def TargetsCheckOnCommand1(self,*arges):
        """"""
        CreateTargets=ArtZ_facial.BlendShapesObject.GenerateAllTargets()
        CreateTargets.AllTargets(1)
    #----------------------------------------------------------------------
    def TargetsCheckOnCommand2(self,*arges):
        """"""
        CreateTargets=ArtZ_facial.BlendShapesObject.GenerateAllTargets()
        CreateTargets.AllTargets(2)
    #----------------------------------------------------------------------
    def TargetsCheckOnCommand3(self,*arges):
        """"""
        CreateTargets=ArtZ_facial.BlendShapesObject.GenerateAllTargets()
        CreateTargets.AllTargets(3)
    #----------------------------------------------------------------------
    def TargetsCheckOnCommand4(self,*arges):
        """"""
        CreateTargets=ArtZ_facial.BlendShapesObject.GenerateAllTargets()
        CreateTargets.AllTargets(4)    
    #----------------------------------------------------------------------
    def ImportPanelCommand(self,*arges):
        """"""
        ImportPanel=ArtZ_facial.BlendShapesObject.GloImportPanel()
        ImportPanel.GloImportTem()
        
    #----------------------------------------------------------------------
    def ConnectBlendToPanelCommand(self,*arges):
        """"""
        ConnectBlend=ArtZ_facial.BlendShapesObject.DriverAllToDrivenAll()
        ConnectBlend.DriverAllToAll()
if __name__=='__main__':
    unittest.main()
