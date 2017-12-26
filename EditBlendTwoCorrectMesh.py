#!/user/bin.evn python
#-*- coding: UTF-8 -*-


__author__  = 'Zhang Shengxin '
__version__ = '2.1'
__status__  = "beta"
__date__    = "2013/11/12"
__using__   = '''from EditBlendShapeTool import EditBlendTwoCorrectMesh
reload(EditBlendTwoCorrectMesh)
EditBlendTwoCorrectMesh.editBlendTwoCorrectMesh().ui()
'''
__updata__ = '多层叠加 2017/12/26 environ 2017'


import maya.cmds as cmds
import maya.OpenMaya as om
import maya.mel as mel
import functools 
from EditBlendShapeTool import replaceOraddBlendShapeItem as reBlendshape
reload(reBlendshape)
import os

mayaEnviron = cmds.about(q=True, v=True)

#import vertSnapDeformer as vsd
#reload(vsd)
#vsd.create()

class editBlendTwoCorrectMesh():
    def __init__(self):
        self.win='buildCorrectShape V%s' % (str(__version__))
        self.mesh = None
        self.BlendNode = None
        self.targetM = None
        self.SculptM = None
        self.tempMesh = None
        self.item = []
        
        self.currSelItemL = None
        self.currSelItemR = None
        self.currSelItemCor = None
        self.mirrM = None
        self.widow = {}
        
        self.mirrUi = mirrMeshShapeUI()
    #----------------------------------------------------------------------
    def ui(self):
        for x in [x for x in cmds.lsUI(wnd=True) if 'buildCorrectShape' in x]:
            cmds.deleteUI(x)
        self.widow['window'] = cmds.window(self.win, menuBar = True, mainMenuBar=True,wh = [300,400], sizeable =1,t=self.win)
        cmds.menu( label='help', tearOff=True )
        ss =  u'选择1stTerm 2stTerm 执行 Sculpt进行雕刻 最后Building创建'
        cmds.menuItem(l= ss, annotation=ss)
        cmds.menu(label = 'Tools', tearOff = True) 
        cmds.menuItem(l = 'MirrMeshTool', c = lambda *args:self.mirrUi.Ui(), annotation = '>> MirrMeshTool >>')
        self.createui()
        self.callBackeCammand('add')
        cmds.showWindow( self.widow['window'] )
    #----------------------------------------------------------------------
    def createui(self):
        """"""
        self.widow['clumnlayout'] = cmds.columnLayout(adj = 1) 
        self.textFieldButton()
        
        self.widow['fam'] = cmds.columnLayout(adj=1)
        self.widow['columnLayout1'] =  cmds.columnLayout( adj=1,bgc =[0.266667, 0.266667 ,0.266667],w = 360)
        cmds.separator(vis = 1,style='in',w = 300,h=5)
        cmds.separator(vis = 1,style='in',w = 300,h=5)
        cmds.setParent('..')
        
        self.widow['columnLayoutM'] =  cmds.columnLayout(adj=1)
        self.TextScrollListPanel = cmds.paneLayout('TextScrollListPanel',configuration='vertical3', enable =False)
        
        self.createTreeViewL()
        self.createTreeViewR()
        self.createTreeViewCorrect()
        cmds.setParent('..')

        
        self.craeteButton_()
        cmds.setParent('..')
        cmds.columnLayout(adj=1)
        self.widow['textScrollWeightIDE'] = cmds.textScrollList(numberOfRows =5,numberOfSelectedItems=False, append = '',popupMenuArray = 1, vis=0)
        
        
        cmds.checkBox(self.widow['checkBoxL'], e=1, onc=lambda *args:self.checkBoxChangeOn(self.widow['checkBoxL'], self.widow['1stTerm']), ofc=lambda *args:self.checkBoxChangeOff(self.widow['checkBoxL'], self.widow['1stTerm']))
        cmds.checkBox(self.widow['checkBoxR'], e=1, onc=lambda *args:self.checkBoxChangeOn(self.widow['checkBoxR'], self.widow['2stTerm']), ofc=lambda *args:self.checkBoxChangeOff(self.widow['checkBoxR'], self.widow['2stTerm']))
        
        #self.callBackeCammand('add')
        #cmds.showWindow( self.widow['window'] )
        #print self.checkBoxQuary()
        
    #----------------------------------------------------------------------
    def getwindow(self):
        '''返回窗口元素'''
        return self.widow
    #----------------------------------------------------------------------
    def setMesh(self):
        '''设置mesh'''
        m =  cmds.ls(sl=True,l=1)
        if m != []:
            mesh = [x for x in m if cmds.nodeType(cmds.listRelatives(x,c=1,s=1, f = True)[0]) == 'mesh'][0]
            nm = mesh.split('|')[-1]
            cmds.textFieldButtonGrp(self.widow['textFieldButtonGrp'],e=1,text=nm)
            self.mesh = mesh
        else:
            self.mesh = ''
            cmds.textFieldButtonGrp(self.widow['textFieldButtonGrp'],e=1,text='')
    #----------------------------------------------------------------------
    def setMirrMesh(self, mirrMesh):
        """设置镜像物体"""
        #item = cmds.textScrollList( Targetlist, q=True,selectItem = 1)[0]
        self.mirrM = mirrMesh
        
    #----------------------------------------------------------------------
    def getMesh(self, *arge):
        '''返回 几何体'''
        return self.mesh
    #----------------------------------------------------------------------
    def setTextScrListCmd(self):
        """设置列表框显示元素"""
        mesh = self.getMesh()
        if mesh != "":
            cmds.paneLayout(self.TextScrollListPanel, e = True, enable=True)
            if cmds.listHistory(mesh,pdo=1):
                BlendNode = [a for a in cmds.listHistory(mesh,pdo=1) if cmds.nodeType(a) == 'blendShape']
            else:
                BlendNode = []
            if BlendNode != []:
                self.BlendNode = BlendNode[0]
            else:
                self.BlendNode = None
            try:
                #self.BlendNode = [a for a in cmds.listHistory(mesh,pdo=1) if cmds.nodeType(a) == 'blendShape'][0]
                #self.item = [x for x in cmds.listAttr(self.BlendNode,m=1,k=1,hd=1) if 'targetWeights' not in x]
                #print self.BlendNode
                self.item = cmds.listAttr('%s.weight'%(self.BlendNode), m=True)
                
                if cmds.checkBox(self.widow['checkBoxL'], q = True, v = 1):
                    corItemL = self.getValuveList(self.BlendNode)
                else:
                    corItemL = self.item
                if cmds.checkBox(self.widow['checkBoxR'], q = True, v = 1):
                    corItemR = self.getValuveList(self.BlendNode)
                else:
                    corItemR = self.item                
                #self.item.pop(0)
                try:
                    index1 =  cmds.textScrollList( self.widow['1stTerm'], q=True, sii = True)
                    index2 =  cmds.textScrollList( self.widow['2stTerm'], q=True, sii = True)
                    index3 =  cmds.textScrollList( self.widow['textScrListCor'], q=True, sii = True)
                    
                        
                    if cmds.checkBox(self.widow['checkBoxL'], q = True, v = 1):
                        corItemL = self.getValuveList(self.BlendNode)
                    else:
                        corItemL = self.item
                    if cmds.checkBox(self.widow['checkBoxR'], q = True, v = 1):
                        corItemR = self.getValuveList(self.BlendNode)
                    else:
                        corItemR = self.item
                    cmds.textScrollList( self.widow['1stTerm'], e=True,ra=1)
                    cmds.textScrollList( self.widow['2stTerm'], e=True,ra=1)
                    cmds.textScrollList( self.widow['textScrListCor'], e=True,ra=1)
                    #corItem = self.item
                    #print "reun here"
                    cmds.textScrollList( self.widow['1stTerm'], e=True, append = corItem)
                    cmds.textScrollList( self.widow['2stTerm'], e=True, append = corItemR)
                    cmds.textScrollList( self.widow['1stTerm'], e=True, sii = index1)
                    cmds.textScrollList( self.widow['1stTerm'], e=True, sii = index2)
                    cmds.textScrollList( self.widow['textScrListCor'], e=True, sii = index3)
                
                except:
                    cmds.textScrollList( self.widow['1stTerm'], e=True,ra=1)
                    cmds.textScrollList( self.widow['2stTerm'], e=True,ra=1)
                    cmds.textScrollList( self.widow['textScrListCor'], e=True,ra=1)
                    #corItem = self.item  
                    cmds.textScrollList( self.widow['1stTerm'], e=True, append = corItemL)
                    cmds.textScrollList( self.widow['2stTerm'], e=True, append = corItemR)
                    cmds.checkBox(self.widow['checkBoxC'], e=True, v=0)
                    
                corS =  []
                v = cmds.checkBox(self.widow['checkBoxCor'], q = True, v = 1)
                for i in self.item:
                    if '_cor' in i:
                        if v:
                            if cmds.getAttr(self.BlendNode+"."+i) >= 0.001 or cmds.getAttr(self.BlendNode+"."+i) <= -0.001:
                                corS.append(i)
                        else:
                            corS.append(i)
                        #corS.append(i)
                
                if corS != []:
                    cmds.textScrollList( self.widow['textScrListCor'], e=True, append = corS)
                else:
                    pass
                cmds.refresh()
            except:
                cmds.textFieldButtonGrp(self.widow['textFieldButtonGrp'],e=1,text='')
                cmds.textScrollList(self.widow['1stTerm' ], e=1 , ra=True)
                cmds.textScrollList(self.widow['2stTerm' ], e=1 , ra=True)
                cmds.textScrollList( self.widow['textScrListCor'], e=True,ra=True)
                cmds.refresh()
                cmds.paneLayout(self.TextScrollListPanel, e = True, enable=False)
                cmds.warning("Mesh  %s hase No blendShape exists ."%mesh)
                
        else:
            cmds.paneLayout(self.TextScrollListPanel, e = True, enable=False)
            cmds.textScrollList(self.widow['1stTerm' ], e=1 , ra=True)
            cmds.textScrollList(self.widow['2stTerm' ], e=1 , ra=True)
            cmds.textScrollList( self.widow['textScrListCor'], e=True,ra=True)
            cmds.refresh()
            cmds.warning('%s No selections mesh '%mesh)
    #----------------------------------------------------------------------
    def getValuveList(self, blendShapeNode = None, state=True):
        """"""
        checkFilteredList = []
        toleranceValue = 0.000001
        listBlendTarget = cmds.listAttr(blendShapeNode+".weight", m=True)
        if state == True:
            for bt in listBlendTarget:
                if cmds.getAttr(blendShapeNode + "."+bt) >=  toleranceValue:
                    checkFilteredList.append(bt)
            return checkFilteredList
        else:
            return None
    #----------------------------------------------------------------------
    def textFieldButtonCommand(self):
        """按钮命令 ，激活building，createSclupt 状态，以及滑块属性"""
        self.setMesh()
        self.setTextScrListCmd()
        cmds.button(self.widow['createSculpt'], e =1, enable = 1 )
        cmds.button(self.widow['building'], e =1, enable = 0 )
        cmds.menuItem(self.widow['menuS'], e=1, enable =1)
        cmds.menuItem(self.widow['menuB'], e=1, enable =0)
        cmds.floatSliderGrp(self.widow['floatSliderGrpL'], e=1, enable=1, value = 0)
        cmds.floatSliderGrp(self.widow['floatSliderGrpR'], e=1, enable=1, value = 0)
        cmds.floatSliderGrp(self.widow['floatSliderGrpCor'], e=1, enable=1, value = 0)
        cmds.textScrollList(self.widow['textScrollWeightIDE'], e=1, ra=1)
        cmds.textScrollList(self.widow['textScrollWeightIDE'], e=1, append=self.item)
    #----------------------------------------------------------------------
    def treeClick(self, textScrollListN, sliderN):
        """点击textScrollList命令"""
        item = cmds.textScrollList( textScrollListN, q=True,selectItem = 1)
        self.inputTargetIDWin(textScrollListN)
        self.eidtTree(textScrollListN,sliderN,item) 
    #----------------------------------------------------------------------
    def eidtTree(self, textScrollListN, sliderN, *args):
        """"""
        if args != []:
            self.itemDblClickCommand_(args[0][0])
            self.changeValue(textScrollListN,sliderN )        
    def changeValue(self, textScrollListN, sliderN):
        """输入textScrollList名字 和划条控件名字，改变划条控件值"""
        nm =  cmds.textScrollList(textScrollListN, q= 1, selectItem=1)
        #print nm
        if nm :
            value =  cmds.getAttr('%s.%s'%(self.BlendNode, nm[0]))
            #print value
            cmds.floatSliderGrp(sliderN, e= 1, value=value)
    #----------------------------------------------------------------------
    def changeCmd(self, SliderGrp, currSelItem, *args):
        """"""
        attr = self.getConnectInfo(currSelItem)
        #print "changeCmd:", attr
        if "_cor" not in  currSelItem:
            cmds.connectControl(SliderGrp, attr)
        else:
            pass
            
        
    #----------------------------------------------------------------------
    def textFieldButton(self):
        """创建文本按钮控件"""
        cmds.separator(vis = 1,style='in',w = 300,h=5)
        self.widow['rowLayout']  =  cmds.rowLayout( numberOfColumns=1, columnWidth=(1, 300), adjustableColumn=1, columnAlign=(1, 'left'),columnOffset1=-300 )
        self.widow['textFieldButtonGrp'] = cmds.textFieldButtonGrp(l = '>>>mesh',bl = '<<',cw3=[50, 260,50], adjustableColumn= 2, numberOfPopupMenus=True, bc = self.textFieldButtonCommand) #
        cmds.popupMenu()
        self.widow['menuItemSel'] =  cmds.menuItem( 'Select Mesh', c=lambda *args: self.selCmd())
        self.widow['menuItemSelBs'] =  cmds.menuItem('Select BlendShapeNode', c=lambda *args: self.selBsCmd())
        cmds.setParent('..')
    #----------------------------------------------------------------------
    def createTreeViewL(self):
        """创建控件"""
        self.widow['rowColumnLayout1L'] = cmds.columnLayout(adj=1)
        self.widow['rowLayout'] =  cmds.rowColumnLayout(numberOfColumns = 2)
        self.widow['checkBoxL'] =  cmds.checkBox( label='1stTerm' ,ed=1)
        self.widow['checkBoxMirr'] =  cmds.checkBox( label='Mirr' ,ed=0, onCommand = lambda *args:self._mirrViewMesh(), offCommand = lambda *args:self._mirrViewMesh())
        cmds.setParent('..')
        self.widow['1stTerm' ]=  cmds.textScrollList( numberOfRows=10, h=250, w =25, allowMultiSelection=False,popupMenuArray = 1, 
                                append='', annotation = '1stTerm', 
                                selectItem='', showIndexedItem=4, doubleClickCommand=lambda *args:self.getItemMesh(1), selectCommand =  self.initLItem)    
        cmds.popupMenu()
        cmds.menuItem('refresh', c = lambda *args: self.refechItem())
        self.widow['menuAddShape'] = cmds.menuItem('AddShape', c = lambda *args:self._addShape())
        self.widow['menuS1'] =  cmds.menuItem('Sculpt', sm=True, c=functools.partial(self.createSculptCmd, 1), ddc=functools.partial(self.createSculptCmd, 1))
        cmds.setParent('..', menu=True)
        self.widow['menuB1'] =  cmds.menuItem('Building',enable=0, c=functools.partial(self.buidingCmd, 1))
        self.widow['menuNameL'] = cmds.menuItem('Rename', c = functools.partial(self.rename, 1))
        self.widow['menuDeletL'] = cmds.menuItem('Delete', sm=1, c = functools.partial(self.DeleShapeItem, 1))
        cmds.setParent('..', menu=True)
        cmds.menuItem(d=True)
        self.widow['menuGetMesh'] =  cmds.menuItem('GetItemMesh', sm=1, c=functools.partial(self.getItemMesh, 1))
        cmds.setParent('..', menu=True)        
        cmds.menuItem('MirrCorrectShape', c = self.mirrCmd)
        cmds.menuItem(optionBox=True, c = lambda *args:self.mirrUi.Ui())

        cmds.setParent('..', menu=True)
        #cmds.menuItem('seeInputTargetId',c= lambda *args: self.inputTargetIDWin(self.widow['1stTerm' ]))
        self.widow['floatSliderGrpL'] =  cmds.floatSliderGrp( field=True, minValue=-1.000, maxValue=1.000,columnWidth2= [50, 50], fieldMinValue=-1.000, fieldMaxValue=1.000, value = 0, fieldStep=0.001, sliderStep = 0.001)
        cmds.floatSliderGrp(self.widow['floatSliderGrpL'], e=1, changeCommand=lambda *args : self.changeCmd(self.widow['floatSliderGrpL' ], self.currSelItemL))
        
        cmds.setParent('..')
    #----------------------------------------------------------------------
    def createTreeViewR(self):
        """创建控件"""
        self.widow['rowColumnLayout1R'] = cmds.columnLayout( adj=1)
        #self.widow['TargetlistR'] = cmds.text(l='2stTerm')
        self.widow['checkBoxR'] =  cmds.checkBox( label='2stTerm' ,ed=1)
        self.widow['2stTerm' ]=  cmds.textScrollList( numberOfRows=10, h=250, w=25, allowMultiSelection=False,popupMenuArray = 1, 
                                append='',annotation = '2stTerm', 
                                selectItem='', showIndexedItem=4, doubleClickCommand=lambda *args:self.treeClick(self.widow['2stTerm' ], self.widow['floatSliderGrpR']), selectCommand =  self.initRItem)
        cmds.popupMenu()
        cmds.menuItem('refresh', c = lambda *args: self.refechItem())
        self.widow['menuS2'] =  cmds.menuItem('Sculpt', c=functools.partial(self.createSculptCmd, 2))
        self.widow['menuB2'] =  cmds.menuItem('Building', enable = 0, c=functools.partial(self.buidingCmd, 2))
        self.widow['menuNameR'] = cmds.menuItem('Rename', c = functools.partial(self.rename, 2))
        self.widow['menuDeletR'] = cmds.menuItem('Delete', c = functools.partial(self.DeleShapeItem, 2))
        cmds.menuItem('MirrCorrectShape', c = self.mirrCmd)
        #cmds.menuItem('seeInputTargetId',c= lambda *args: self.inputTargetIDWin(self.widow['2stTerm' ]))        
        self.widow['floatSliderGrpR'] =  cmds.floatSliderGrp( field=True, minValue=-1.000, maxValue=1.000,columnWidth2= [50, 50], fieldMinValue=-1.000, fieldMaxValue=1.000, value =0, fieldStep = 0.001, sliderStep = 0.001)
        cmds.floatSliderGrp(self.widow['floatSliderGrpR'], e=1, changeCommand=lambda *args : self.changeCmd(self.widow['floatSliderGrpR' ], self.currSelItemR))
        cmds.setParent('..')
    
    #----------------------------------------------------------------------
    def createTreeViewCorrect(self):
        """创建控件"""
        self.widow['rowColumnLayoutCorrect'] = cmds.columnLayout(adj=1, vis=1)
        #self.widow['TargetlistCorrect'] = cmds.text(l='CorrectShapes')
        self.widow['checkBoxCor'] =  cmds.checkBox( label='CorrectShapes' ,ed=1, onc=self.checkBoxOnCmd, ofc=self.checkBoxOffCmd, vis=1)
        self.widow['textScrListCor' ]=  cmds.textScrollList( numberOfRows=10, h=250, w =25, allowMultiSelection=False,popupMenuArray = 1, vis=1, 
                                append='',annotation = 'textScrListCor', 
                                selectItem='', showIndexedItem=4, doubleClickCommand =  lambda *args:self.treeClick(self.widow['textScrListCor'], self.widow['floatSliderGrpCor']) , selectCommand =  self.initCorItem)    
        cmds.popupMenu()
        cmds.menuItem('refresh', c = lambda *args: self.refechItem())
        self.widow['menuS'] =  cmds.menuItem('Sculpt', c=functools.partial(self.createSculptCmd, 3))
        self.widow['menuB'] =  cmds.menuItem('Building', c=functools.partial(self.buidingCmd, 3))
        self.widow['menuNameC'] = cmds.menuItem('Rename', c = functools.partial(self.rename, 3))
        self.widow['menuDeletC'] = cmds.menuItem('Delete', c = functools.partial(self.DeleShapeItem, 3))          
        cmds.menuItem('MirrCorrectShape', c = self.mirrCmd)
        
        #cmds.menuItem('seeInputTargetId', c= lambda *args: self.inputTargetIDWin(self.widow['textScrListCor' ]))
        self.widow['floatSliderGrpCor'] =  cmds.floatSliderGrp(field=True, minValue=-1.000, maxValue=1.000,columnWidth2= [50, 50], fieldMinValue=-1.000, fieldMaxValue=1.000, value =0, fieldStep = 0.001, sliderStep = 0.001, vis=1)
        cmds.floatSliderGrp(self.widow['floatSliderGrpCor'], e=1, changeCommand=lambda *args : self.changeCmd(self.widow['floatSliderGrpCor'], self.currSelItemCor))  
        cmds.setParent('..')
    #----------------------------------------------------------------------
    def createInbtweenMenu(self, Targetlist="self.widow['1stTerm']", *args):
        """"""
        na =  cmds.textScrollList(Targetlist, q=True, si=True)[0]
        #print na
        inbetweens = getCrGrpItem(self.BlendNode)
        index =  None
        menu =  None
        deltMenu =  None
        getMMenu = None
        if Targetlist == self.widow['1stTerm']:
            index = 1
            menu =  self.widow['menuS1']
            deltMenu =  self.widow['menuDeletL']
            getMMenu =  self.widow['menuGetMesh']
        elif Targetlist == self.widow['2stTerm']:
            index = 2
            menu =  self.widow['menuS2']
            deltMenu =  self.widow['menuDeletL']
        else :
            index = 3
            menu =  self.widow['menuS']
            deltMenu =  self.widow['menuDeletL']
        its =  cmds.menu(menu, q=1, ia=True)
        itsd =  cmds.menu(deltMenu, q=1, ia=True)
        itsM =  cmds.menu(getMMenu, q=1, ia=True)
        if its != None:
            for it in zip(its, itsd, itsM):
                #print it
                cmds.deleteUI(it[0], mi=True)
                cmds.deleteUI(it[1], mi=True)
                cmds.deleteUI(it[2], mi=True)
        for i in inbetweens[na][1]:
            self.widow['between%dMenu'%i] =  cmds.menuItem('between%dMenu'%i,  l=self.itemToValue(i), c=functools.partial(self.createSculptCmd, index, 'between%dMenu'%i), p = menu)
            self.widow['delte%dMenu'%i] =  cmds.menuItem('delete%dMenu'%i,  l=self.itemToValue(i), c=functools.partial(self.DeleShapeItem, index, 'delete%dMenu'%i), p = deltMenu)
            self.widow['getM%dMenu'%i] =  cmds.menuItem('getMesh%dMenu'%i,  l=self.itemToValue(i), c=functools.partial(self.getItemMesh, index, 'getMesh%dMenu'%i), p = getMMenu)
            
            if i == inbetweens[na][1][-1]:
                cmds.menuItem( divider=True , p=menu)
                self.widow['between%dMenu'%i] =  cmds.menuItem('betweenMenu',  l='Sculpt', c=functools.partial(self.createSculptCmd, index), p = menu)
                cmds.menuItem( divider=True , p=deltMenu)
                self.widow['delte%dMenu'%i] =  cmds.menuItem('delete%dMenu'%i,  l='Delete', c=functools.partial(self.DeleShapeItem, index), p = deltMenu)
                cmds.menuItem( divider=True , p=getMMenu)
                self.widow['getM%dMenu'%i] =  cmds.menuItem('getMesh%dMenu'%i,  l='getItemMesh', c=functools.partial(self.getItemMesh, index), p = getMMenu)        
            #print 'run here', self.widow['between%dMenu'%i]
    #---------------------------------------------------------------------- 
    def itemToValue(self,item):
        '''转化items权重值'''
        if item == 6000:
            value = 6000/6000.0
        else:
            value = (item-5000)/1000.0
        return value
    #----------------------------------------------------------------------
    def __checkInbetween(self, itemName , value):
        """"""
        for i in getCrGrpItem(self.BlendNode)[itemName][1]:
            if self.itemToValue(i) == value:
                print value  
                return True
            else:
                print None
                return False
    #----------------------------------------------------------------------
    def inputTargetIDWin(self, Targetlist="self.widow['1stTerm']"):
        """创建目标体ID控件"""
        if cmds.window('inputTargetID',ex=1):
                    cmds.deleteUI('inputTargetID')        
        self.widow['win'] = cmds.window('inputTargetID', t = 'inputTargetID', vis=False)
        cl = cmds.columnLayout(adj =1)
        self.widow['textScrollID'] = cmds.textScrollList( numberOfSelectedItems=False,  append = self.inputTargetIdList(),popupMenuArray = 1)#, doubleClickCommand = lambda *args:self.inputTargetIDWinDoubleClickCmd(self.widow['textScrollID']))
        self.widow['textScrollWeightID'] = cmds.textScrollList(numberOfSelectedItems=False, append = self.inputWeightIdList(),popupMenuArray = 1) # doubleClickCommand = lambda *args:self.inputTargetIDWinDoubleClickCmd(self.widow['textScrollWeightID']))
        self.setpoptextScrolIndex(Targetlist)
        #cmds.showWindow(self.widow['win'])
    #----------------------------------------------------------------------
    def inputTargetIdList(self):
        """找出目标体ID，放回ID"""
        return  [x for x in cmds.listAttr('%s.inputTarget'%self.BlendNode,m=1,hd=1) if 'inputGeomTarget' in x]
    #----------------------------------------------------------------------
    def inputWeightIdList(self):
        """找出目标体名字，放回名字"""
        weightA =  [x for x in cmds.listAttr('%s'%self.BlendNode,k=1, m=1, hd=1) if 'targetWeights' not in x]
        weightA.pop(0)
        return weightA
    #----------------------------------------------------------------------
    def inputTargetIDWinDoubleClickCmd(self, idlist = "self.widow['textScrollID']" ):
        """目标体Id控件双击命令"""
        selStr =  cmds.textScrollList(idlist, q=1, si=1)[0]
        #print self.BlendNode + '.' + selStr

    #----------------------------------------------------------------------
    def setpoptextScrolIndex(self, Targetlist="self.widow['1stTerm'"):
        """"""
        self.setpoptextScrolselect(Targetlist)
        self.getpoptextScrolIndex(Targetlist)
 
    #----------------------------------------------------------------------
    def setpoptextScrolselect(self, Targetlist="self.widow['1stTerm'"):
        """设置选择的Id名字"""
        selectStr =  cmds.textScrollList( Targetlist , q=1,  selectItem=1)[0]
        cmds.textScrollList( self.widow['textScrollWeightID'] , e=1,  selectItem=selectStr)        
    #----------------------------------------------------------------------
    def getpoptextScrolIndex(self, Targetlist="self.widow['1stTerm'"):
        """设置选择的Id号"""
        indexA =  cmds.textScrollList( self.widow['textScrollWeightID'] , q=1,  selectIndexedItem=1)
        cmds.textScrollList(self.widow['textScrollID'] , e=1, selectIndexedItem = indexA)        
    #----------------------------------------------------------------------
    def craeteButton_(self):
        """创建按钮命令"""
        self.widow['clumnlayoutB'] = cmds.columnLayout( adj=1,bgc =[0.266667, 0.266667 ,0.266667],w=300 )
        self.widow['reset'] = cmds.button('Reset', c=self.resetCmd)
        self.widow['rowLayoutB'] =  cmds.rowLayout( numberOfColumns=2, columnWidth2=(60, 70), adjustableColumn=1, columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0)] )
        self.widow['createSculpt'] = cmds.button('Sculpt', c = functools.partial(self.createSculptCmd, 3))
        self.widow['checkBoxC'] =  cmds.checkBox( label='Combine' ,ed=1)
        cmds.setParent('..')
        self.widow['building'] = cmds.button('Building', enable = 0 , c = functools.partial(self.buidingCmd, 3))
        #self.widow['mirr'] = cmds.button('MirrCorrectShape', enable = True, c=self.mirrCmd)
    #----------------------------------------------------------------------
    def itemDblClickCommand_(self, *args):
        """双击命令"""
        #print args
        for i in args:
            if cmds.objExists(i):
                cmds.select(i)
            else:
                string = 'No object matches name:' + ' %s'%i
                #cmds.warning(string )
                self.createTargetCmd(self.mesh, args[0])
            
    #----------------------------------------------------------------------
    def initLItem(self):
        """初始化L"""
        # clear variable
        self.currSelItemL = cmds.textScrollList( self.widow['1stTerm'], q=True, si=1)[0]
        
        # set weight value
        self.changeValue(self.widow['1stTerm'],self.widow['floatSliderGrpL'] )
        self.changeCmd(self.widow['floatSliderGrpL'], self.currSelItemL)
        self.setMirrMesh(self.currSelItemL)
        self.createInbtweenMenu(self.widow['1stTerm'])
        #om.MGlobal.displayInfo(self.currSelItemL)
        if mayaEnviron != '2017':
            if cmds.objExists(self.currSelItemL + '_sculpt'):
                cmds.menuItem(self.widow['menuS1'], e=True, en = False)
                cmds.menuItem(self.widow['menuB1'] , e = True, en = True)
                cmds.button(self.widow['createSculpt'] , e=True, en = False)
                cmds.button(self.widow['building'] , e=True, en = True)
                self.SculptM =  self.currSelItemL + '_sculpt'
                if cmds.menuItem(self.widow['menuB1'] , e = True, en = True):
                    cmds.checkBox(self.widow['checkBoxMirr'], e = True, ed = True)
                else:
                    cmds.checkBox(self.widow['checkBoxMirr'], e = True, ed = False)
            else:
                cmds.menuItem(self.widow['menuS1'], e=True, en = True)
                cmds.menuItem(self.widow['menuB1'] , e = True, en = False)
                cmds.button(self.widow['createSculpt'] , e=True, en = True)
                cmds.button(self.widow['building'] , e=True, en = False)            
                if cmds.menuItem(self.widow['menuB1'] , q = True, en = True):
                    cmds.checkBox(self.widow['checkBoxMirr'], e = True, ed = False)
                else:
                    if self.targetM != None:
                        cmds.checkBox(self.widow['checkBoxMirr'], e = True, ed = True)
                    else:
                        cmds.checkBox(self.widow['checkBoxMirr'], e = True, ed = False)
        else:
            tgtName = self.__getBlendShapeEidtHUd()
            if self.currSelItemL == tgtName:
                cmds.menuItem(self.widow['menuS1'], e=True, en = False)
                cmds.menuItem(self.widow['menuB1'] , e = True, en = True)
                cmds.button(self.widow['createSculpt'] , e=True, en = False)
                cmds.button(self.widow['building'] , e=True, en = True)
                if cmds.menuItem(self.widow['menuB1'] , e = True, en = True):
                    cmds.checkBox(self.widow['checkBoxMirr'], e = True, ed = True)
                else:
                    cmds.checkBox(self.widow['checkBoxMirr'], e = True, ed = False)
            else:
                cmds.menuItem(self.widow['menuS1'], e=True, en = True)
                cmds.menuItem(self.widow['menuB1'] , e = True, en = False)
                cmds.button(self.widow['createSculpt'] , e=True, en = True)
                cmds.button(self.widow['building'] , e=True, en = False)
                if cmds.menuItem(self.widow['menuB1'] , q = True, en = True):
                    cmds.checkBox(self.widow['checkBoxMirr'], e = True, ed = False)
                else:
                    if self.targetM != None:
                        cmds.checkBox(self.widow['checkBoxMirr'], e = True, ed = True)
                    else:
                        cmds.checkBox(self.widow['checkBoxMirr'], e = True, ed = False)
    #----------------------------------------------------------------------
    def initRItem(self):
        """初始化R"""
        # clear variable
        self.currSelItemR = cmds.textScrollList( self.widow['2stTerm'], q=True, si=1)[0]
        
        # set weight value
        self.changeValue(self.widow['2stTerm'], self.widow['floatSliderGrpR'])
        self.changeCmd(self.widow['floatSliderGrpR'], self.currSelItemR)
        self.setMirrMesh(self.currSelItemR)
        if self.currSelItemR != None and self.currSelItemL != None:
            cmds.checkBox(self.widow['checkBoxC'], e=True, v=1)
    #----------------------------------------------------------------------
    def initCorItem(self):
        """初始化Cor"""
        # clear variable
        self.currSelItemCor = cmds.textScrollList( self.widow['textScrListCor'], q=True, si=1)[0]
        # set weight value
        self.changeValue(self.widow['textScrListCor'], self.widow['floatSliderGrpCor'])
        self.changeCmd(self.widow['floatSliderGrpCor'], self.currSelItemCor)
        self.resetCmd()
        self.setselectItemCmd()
        '''self.treeClick(self.widow['textScrListCor'], self.widow['floatSliderGrpCor'])'''
        self.initLItem()
        self.initRItem()
        cmds.checkBox(self.widow['checkBoxC'], e=True, v=1)
        #self.setMirrMesh(self.currSelItemCor.replace('cor', 'sculpt'))
        if cmds.objExists(self.currSelItemCor + '_sculpt'):
            cmds.menuItem(self.widow['menuS'], e=True, en = False)
            cmds.menuItem(self.widow['menuB'] , e = True, en = True)
            cmds.button(self.widow['createSculpt'], e = 1, en = 0)
            cmds.button(self.widow['building'], e =1 , enable=1)
            self.SculptM =  self.currSelItemCor + '_sculpt'
            cmds.checkBox(self.widow['checkBoxC'], e=True, v=1)
        else:
            cmds.menuItem(self.widow['menuS'], e=True, en = True)
            cmds.menuItem(self.widow['menuB'] , e = True, en = False)
            cmds.button(self.widow['createSculpt'], e = 1, en = 1)
            cmds.button(self.widow['building'], e =1 , enable=0)            
    def refechItem(self):
        """刷新列表"""
        self.currSelItemR = None
        self.currSelItemL = None
        
        self.setTextScrListCmd()

    #----------------------------------------------------------------------
    def refreshStaice(self):
        """"""
        if self.SculptM != None:
            if cmds.objExists(self.SculptM):
                if '_cor' in self.SculptM:
                    cmds.button(self.widow['createSculpt'], e = 1, en = 0)
                    cmds.button(self.widow['building'], e =1 , enable=1)
                    cmds.menuItem(self.widow['menuS'], e = 1, en = 0)
                    cmds.menuItem(self.widow['menuB'], e = 1, en = 1)                    
                else:
                    cmds.menuItem(self.widow['menuS1'], e=True, en = False)
                    cmds.menuItem(self.widow['menuB1'] , e = True, en = True)                    
            else:
                cmds.button(self.widow['createSculpt'], e = 1, en = 1)
                cmds.button(self.widow['building'], e =1 , enable=0)
                cmds.menuItem(self.widow['menuS1'], e=True, en = True)
                cmds.menuItem(self.widow['menuB1'] , e = True, en = False)
                cmds.menuItem(self.widow['menuS'], e = 1, en = 1)
                cmds.menuItem(self.widow['menuB'], e = 1, en = 0)
    #----------------------------------------------------------------------
    def selCmd(self):
        """选择命令"""
        cmds.select(self.mesh, r=True)
    def selBsCmd(self):
        """选择命令"""
        cmds.select(self.BlendNode, r=True)
    #----------------------------------------------------------------------
    def resetCmd(self, *args):
        """还原命令"""
        
        resetObj =  cmds.textScrollList(self.widow['1stTerm'], q=1, allItems=True)
        if resetObj != None:
            resetObj.extend(cmds.textScrollList(self.widow['2stTerm'], q=1, allItems=True))
        else:
            resetObj = (cmds.textScrollList(self.widow['2stTerm'], q=1, allItems=True))
        #print resetObj
        if resetObj != None:
            for obj in resetObj:
                try:
                    if cmds.getAttr('%s.%s'%(self.BlendNode, obj)) != 0 :
                        atr = self.getConnectInfo(obj)
                        #print 'queryAttr:', atr
                        if atr:
                            cmds.setAttr(atr, 0)
    
                        else:
                            if cmds.getAttr('%s.%s'%(self.BlendNode, obj), l = True):
                                pass
                            else:
                                cmds.setAttr(self.BlendNode + "." + obj, 0)
                except:
                    #print "pass", self.BlendNode
                    pass
        self.refechItem()
    #----------------------------------------------------------------------
    def createSculptCmd(self, listType= 1, *arge):
        """创建雕刻体"""
        #print arge
        if arge[0] != () and arge[0] != False:
            v = cmds.menuItem(arge[0], q = 1, l = True)
            #print v
            self.targetSculptMesh(listType, float(v))
            
        else:
            self.targetSculptMesh(listType)
    #----------------------------------------------------------------------
    def createSculptMesh(self, name):
        """"""
        if cmds.objExists(name+'_sculpt') == True:
            Sculpt =  name+'_sculpt'
        else:
            Sculpt =  cmds.duplicate(self.mesh, name=name+'_sculpt')[0]
        
        cmds.connectAttr(cmds.listRelatives(self.mesh, s = True, c=True)[0]+'.outMesh', cmds.listRelatives(Sculpt, s = True, c=True)[0]+'.inMesh', f = True)
        #print name, Sculpt
        return Sculpt
    #----------------------------------------------------------------------
    def targetSculptMesh(self, listType = 3, *args):
        """创建雕刻体函数"""
        cmds.undoInfo(openChunk=True)
        mesh =  self.getMesh()
        na =  self.getSelectTreeName()
        print args
        check = cmds.checkBox(self.widow['checkBoxC'], q = 1, v = 1)
        if check:
            listType = 3
        else:
            listType = 1
        if listType == 1:
            om.MGlobal.displayInfo('targetSculptMesh:listTypeL')
            ty = cmds.menuItem(self.widow['menuS1'], q = True, enable= True)
            name = cmds.textScrollList(self.widow['1stTerm'], q=1, si=1)[0]
            
            if mayaEnviron != '2017':
                if args != ():
                    if '_cor' not in name:
                        cmds.floatSliderGrp(self.widow['floatSliderGrpL'], e= 1, value= args[0])
                        cmds.setAttr(self.BlendNode + '.' + name, args[0])
                    else:
                        pass
                    
                if cmds.objExists(name+'_sculpt'):
                    self.SculptM =  name+'_sculpt'
                else:
                    self.SculptM = self.createSculptMesh(name)
                cmds.setAttr(self.SculptM + '.visibility', 1)
                cmds.setAttr(self.mesh + '.visibility', 0)
                cmds.select(self.SculptM)
            else:
                #sculptTarget -e -target 0 blendShape1;
                ID = getCrGrpItem(self.BlendNode)[name][0]
                if args != ():
                    cmds.floatSliderGrp(self.widow['floatSliderGrpL'], e= 1, value= args[0])
                    cmds.setAttr(self.BlendNode + '.' + name, args[0])
                    cmds.sculptTarget(self.BlendNode, e=True, target = ID, ibw = args[0])
                else:
                    value = cmds.floatSliderGrp(self.widow['floatSliderGrpL'] , q = True, v = True)
                    #print value
                    if value < 1.0 and 0.0 < value:
                        #blendShape -e  -ib -t pCube1 0 pCube2 0.5 blendShape1;
                        if  self.__checkInbetween(name, value) == False:
                            #print "run __checkInbetween"
                            #@checkTopo - If check topology;
                            #@heroTargetIndex - Hero target index to add the in-between target;
                            #@inBetweenWeight - Maximum influence weight of the in-between target;
                            #@inBetweenType   - The type of in-between target to create, relative/absolute to hero target;
                            #                   0 absolute, 1 relative;                            
                            Melstring = "string $targetShapes[]; doBlendShapeAddInBetweenTarget {blendShape} {checkTopo} {targetIndex} {inBetweenWeight} {inBetweenType} $targetShapes;".format(blendShape = self.BlendNode, checkTopo = 1, targetIndex = ID,inBetweenWeight = value, inBetweenType = 0)
                            mel.eval(Melstring)
                            cmds.sculptTarget(self.BlendNode, e=True, target = ID, ibw = value)
                    if value != 0.0:
                        cmds.sculptTarget(self.BlendNode, e=True, target = ID, ibw = value)
            cmds.button(self.widow['createSculpt'], e =1 , enable=0)
            cmds.button(self.widow['building'], e =1 , enable=1)
            cmds.menuItem(self.widow['menuS1'], e=True, en = False)
            cmds.menuItem(self.widow['menuB1'] , e = True, en = True)
        elif listType == 2:
            om.MGlobal.displayInfo('targetSculptMesh:listTypeR')
            cmds.menuItem(self.widow['menuS2'], e=True, en = False)
            cmds.menuItem(self.widow['menuB2'] , e = True, en = True)
        else:
            
            listL =  cmds.textScrollList(self.widow['1stTerm'], q=1 ,  si=1)
            listR =  cmds.textScrollList(self.widow['2stTerm'], q=1 ,  si=1)
            corrList =  cmds.textScrollList(self.widow['textScrListCor'], q=1 ,  si=1)
            v1 =  cmds.floatSliderGrp(self.widow['floatSliderGrpL'], q= 1, value=True)
            v2 =  cmds.floatSliderGrp(self.widow['floatSliderGrpR'], q= 1, value=True)
            #print na
            if na[0] != None and na[1] != None and na[0] != na[1]:
                if na[0][0].replace('_', '') +  na[1][0].replace('_', '') + '_cor' not in self.item:
    
                    name =  na[0][0].replace('_', '') + '_' + na[1][0].replace('_', '')
                    if v1 != 0 and v2 != 0:
                        #self.tempMesh, self.SculptM, self.targetM =  correctMesh(mesh, name)
                        self.targetM = name + '_cor'
                        self.SculptM = self.createSculptMesh(self.targetM )
                        #addBlendShape(self.targetM, self.BlendNode)

                        cmds.setAttr('%s.visibility'%mesh, 0)
                        #cmds.setAttr('%s.visibility'%self.targetM, 0)
                        #cmds.setAttr('%s.visibility'%self.tempMesh, 0)
                        cmds.button(self.widow['createSculpt'], e =1 , enable=0)
                        cmds.menuItem('refresh', e=1, en=0)
                        cmds.button(self.widow['building'], e =1 , enable=1)
                        #SetParent_('sculptShapeGrp', [self.tempMesh , self.SculptM])
                        cmds.select(self.SculptM)
                        self.setTextScrListCmd()
                        cmds.textScrollList(self.widow['1stTerm'], e=1 ,  deselectAll=True)
                        cmds.textScrollList(self.widow['2stTerm'], e=1 ,  deselectAll=True)
                        cmds.textScrollList(self.widow['1stTerm'], e=1 ,  si=listL)
                        cmds.textScrollList(self.widow['2stTerm'], e=1 ,  si=listR)
                        cmds.menuItem(self.widow['menuB'], e=1, enable =1)
                        cmds.menuItem(self.widow['menuS'], e=1, enable =0)
                        cmds.checkBox(self.widow['checkBoxC'], e=True, v=1)
                        #cmds.select(cl=1)
                    else:
                        cmds.warning('attrubute value must not 0 ')
                elif  na[0][0].replace('_', '') +  na[1][0].replace('_', '') + '_cor' in self.item:
                    name =  na[0][0].replace('_', '') +  na[1][0].replace('_', '') + '_sculpt'
                    if cmds.objExists(name):
                        if v1 != 0 and v2 != 0:
                            if cmds.connectionInfo("%s.%s" %(self.BlendNode,name.replace('_sculpt', '_cor')),sourceFromDestination=True):
                                self.setTextScrListCmd()
                                cmds.setAttr('%s.visibility'%name, 1)
                                cmds.select(name)
                                cmds.setAttr('%s.visibility'%mesh, 0)
                                cmds.button(self.widow['createSculpt'], e =1 , enable=0)
                                cmds.menuItem('refresh', e=1, en=0)
                                cmds.button(self.widow['building'], e =1 , enable=1)
                                cmds.menuItem(self.widow['menuS'], e=1, enable =0)
                                cmds.menuItem(self.widow['menuB'], e=1, enable =1)
                                cmds.select(cl=1)
                                cmds.textScrollList(self.widow['1stTerm'], e=1 ,  deselectAll=True)
                                cmds.textScrollList(self.widow['2stTerm'], e=1 ,  deselectAll=True)
                                cmds.textScrollList(self.widow['1stTerm'], e=1 ,  si=listL)
                                cmds.textScrollList(self.widow['2stTerm'], e=1 ,  si=listR)
                                cmds.checkBox(self.widow['checkBoxC'], e=True, v=1)
                            else:
                                cmds.connectAttr('%s.outputX'%name.replace('_sculpt', '_DV'), '%s.%s'%(self.BlendNode, name.replace('_sculpt', '_cor')), f=True )
                                self.setTextScrListCmd()
                                cmds.textScrollList(self.widow['1stTerm'], e=1 ,  deselectAll=True)
                                cmds.textScrollList(self.widow['2stTerm'], e=1 ,  deselectAll=True)                        
                                cmds.textScrollList(self.widow['1stTerm'], e=1 ,  si=listL)
                                cmds.textScrollList(self.widow['2stTerm'], e=1 ,  si=listR)
                                cmds.setAttr('%s.visibility'%name, 1)
                                cmds.select(name)
                                cmds.setAttr('%s.visibility'%mesh, 0)
                                cmds.button(self.widow['createSculpt'], e =1 , enable=0)
                                cmds.menuItem('refresh', e=1, en=0)
                                cmds.button(self.widow['building'], e =1 , enable=1)
                                cmds.menuItem(self.widow['menuS'], e=1, enable =0)
                                cmds.menuItem(self.widow['menuB'], e=1, enable =1)
                                cmds.select(cl=1)
                                cmds.checkBox(self.widow['checkBoxC'], e=True, v=1)
                    else:
                        if v1 != 0 and v2 != 0:
                            bsNode =  self.getBlendShape()
                            nam =  na[0][0].replace('_', '') +  na[1][0].replace('_', '')
                            cmds.textScrollList( self.widow['textScrListCor'] , e=1, si=nam+'_cor')
                            
                            #获得id号
                            self.inputTargetIDWin( self.widow['textScrListCor'])
                            index =  cmds.textScrollList(self.widow['textScrollID'], q=1,  si=1)[0]
                            cmds.deleteUI('inputTargetID')
                            #cmds.textScrollList( self.widow['1stTerm'] , e=1, deselectItem=nam+'_cor')
                            
                            name =  na[0][0].replace('_', '') +  na[1][0].replace('_', '') + "_cor"
                            self.SculptM = self.createSculptMesh(name)
                            
                            cmds.setAttr('%s.visibility'%mesh, 0)
                            #cmds.setAttr('%s.template'%mesh, 1)
                            cmds.button(self.widow['createSculpt'], e =1 , enable=0)
                            cmds.menuItem('refresh', e=1, en=0)
                            cmds.button(self.widow['building'], e =1 , enable=1)
                            cmds.select(self.SculptM)
                            self.setTextScrListCmd()
                            cmds.textScrollList(self.widow['1stTerm'], e=1 ,  deselectAll=True)
                            cmds.textScrollList(self.widow['2stTerm'], e=1 ,  deselectAll=True)
                            cmds.textScrollList(self.widow['1stTerm'], e=1 ,  si=listL)
                            cmds.textScrollList(self.widow['2stTerm'], e=1 ,  si=listR)
                            cmds.menuItem(self.widow['menuS'], e=1, enable =0)
                            cmds.menuItem(self.widow['menuB'], e=1, enable =1)
                            #cmds.select(cl=1)
                            cmds.checkBox(self.widow['checkBoxC'], e=True, v=1)
                        else:
                            cmds.warning( ' Attributes value must not 0  ')
            else :
                cmds.warning( ' must select object that form 1stTerm and 2stTerm ,and secections 1stTerm difference 2stTerm .')
        
        cmds.undoInfo(closeChunk=False)
    def __addInbetween(self, targetMesh, ID, value):
        #blendShape -e  -ib -t pCube1 0 pCube2 0.5 blendShape1;
        #print targetMesh, ID, value
        cmds.blendShape(self.BlendNode, e=True, ib=True, t=(self.mesh, ID, targetMesh, value))
    #----------------------------------------------------------------------
    def __getBlendShapeEidtHUd(self):
        """"""
        attr = "%s.inputTarget" % self.BlendNode
        tgts =  cmds.getAttr(attr, mi=True)
        nbEdit = 0
        for i in xrange(len(tgts)):
            attr = '%s.inputTarget[%d].sculptTargetIndex' % (self.BlendNode, i)
            idx =  cmds.getAttr(attr)
            if idx != -1:
                attr =  '%s.weight[%s]' % (self.BlendNode, idx)
                tgtName = cmds.aliasAttr(attr, q=True)
                return tgtName
                    
    #----------------------------------------------------------------------
    def createTargetSculptCmd(self, bsNode='', name='', ID=''):
        """创建雕刻体命令"""
        attr = bsNode + '.' + name + '_cor'
        if cmds.connectionInfo(attr,isExactDestination=1):
            sourceAttr =  cmds.connectionInfo(attr,sourceFromDestination=1)
            cmds.disconnectAttr(sourceAttr, attr)
            cmds.setAttr(attr, 0)
            
            inputMesh = self.getMesh()
            #tempBase, Sculpt, target =  correctMesh(inputMesh, name)
            tempBase, Sculpt, target =  self.correctMesh_(inputMesh, name, attr)
            try:
                cmds.connectAttr('%s.worldMesh[0]'%cmds.listRelatives(target, c=1)[0], bsNode+'.'+ID, f=1)
            except:
                pass
            cmds.connectAttr(sourceAttr, attr)
            return tempBase, Sculpt, target
        else:return None
    #----------------------------------------------------------------------
    def getItemMesh(self, listType, *args):
        """"""
        inbetween =  False
        if listType == 1:
            om.MGlobal.displayInfo('getItemMesh %s'%listType)
            #cmds.undoInfo(openChunk=True)
            corName = cmds.textScrollList( self.widow['1stTerm'] , q=1,  selectItem=1)[0]
            if args != () and args[0] != False:
                v = cmds.menuItem(args[0], q = 1, l = True)
                #print 'return label v:', v
                if v != 'getItemMesh':
                    if float(v) != 0.0 and float(v) != 1.0:
                        inbetween = True
                    else:
                        #print 'run here v 1.0'
                        inbetween =  False
        if listType == 2:
            om.MGlobal.displayInfo('DeleShapeItem %s'%listType)
            #cmds.undoInfo(openChunk=True)
            corName = cmds.textScrollList( self.widow['2stTerm'] , q=1,  selectItem=1)[0]
        if listType == 3:
            om.MGlobal.displayInfo('DeleShapeItem %s'%listType)
            #cmds.undoInfo(openChunk=True)
            corName = cmds.textScrollList( self.widow['textScrListCor'] , q=1,  selectItem=1)[0]
        bsData = getCrGrpItem(self.BlendNode)
        #print bsData
        item = None
        meshAttr = None
        point = None
        vexter = None
        
        if inbetween == True:
            if float(v) != 0.0 and float(v) != 1.0:
                item =  int(float(v) * 1000 + 5000)
                meshAttr =  '%s.inputTarget[0].inputTargetGroup[%s].inputTargetItem[%d].inputGeomTarget' % (self.BlendNode, bsData[corName][0], item)
                point =  cmds.getAttr('%s.inputTarget[0].inputTargetGroup[%s].inputTargetItem[%d].inputPointsTarget' % (self.BlendNode, bsData[corName][0], item))
                vexter =  cmds.getAttr('%s.inputTarget[0].inputTargetGroup[%s].inputTargetItem[%d].inputComponentsTarget'% (self.BlendNode, bsData[corName][0], item))
                cmds.setAttr(self.BlendNode+'.'+corName, float(v))
                
            else:
                item = ''
                meshAttr =  '%s.inputTarget[0].inputTargetGroup[%s].inputTargetItem[%d].inputGeomTarget' % (self.BlendNode, bsData[corName][0], bsData[corName][1][-1])
                point =  cmds.getAttr('%s.inputTarget[0].inputTargetGroup[%s].inputTargetItem[%d].inputPointsTarget' % (self.BlendNode, bsData[corName][0], bsData[corName][1][-1]))
                vexter =  cmds.getAttr('%s.inputTarget[0].inputTargetGroup[%s].inputTargetItem[%d].inputComponentsTarget'% (self.BlendNode, bsData[corName][0], bsData[corName][1][-1]))
                cmds.setAttr(self.BlendNode+'.'+corName, 1)
        else:
            meshAttr =  '%s.inputTarget[0].inputTargetGroup[%s].inputTargetItem[%d].inputGeomTarget' % (self.BlendNode, bsData[corName][0], bsData[corName][1][-1])
            point =  cmds.getAttr('%s.inputTarget[0].inputTargetGroup[%s].inputTargetItem[%d].inputPointsTarget' % (self.BlendNode, bsData[corName][0], bsData[corName][1][-1]))
            vexter =  cmds.getAttr('%s.inputTarget[0].inputTargetGroup[%s].inputTargetItem[%d].inputComponentsTarget'% (self.BlendNode, bsData[corName][0], bsData[corName][1][-1]))
            cmds.setAttr(self.BlendNode+'.'+corName, 1)
        #print meshAttr
        inMesh =  getConnection(meshAttr)
        if inMesh[0] != None:
            itemMesh =  cmds.listRelatives(inMesh[0].split('.')[0], p=True, f=True)
            cmds.select(itemMesh, r=True)
        else:
            if inbetween:
                itemMesh =  cmds.duplicate(self.mesh, name=corName+'_'+str(item)+'_d')[0]
            else:
                itemMesh =  cmds.duplicate(self.mesh, name=corName)[0]
            cmds.DeleteHistory(itemMesh)
            #print len(vexter), vexter, '\n', len(point), point
            cmds.select(cl=True, r=True)
            vexters =  []
            for vex in vexter:
                vexters.append(itemMesh+'.'+vex)
            vextersList =  cmds.ls(sl=True, fl=True, r=True)
            for p,vexs in zip(point,vextersList):
                vex =  vexs.split('.')[1]
                cmds.setAttr(itemMesh+'.pnts%s.pntx'%vex.replace('vtx',''),p[0])
                cmds.setAttr(itemMesh+'.pnts%s.pnty'%vex.replace('vtx',''),p[1])
                cmds.setAttr(itemMesh+'.pnts%s.pntz'%vex.replace('vtx',''),p[2])
            cmds.connectAttr('%s.worldMesh[0]'%cmds.listRelatives(itemMesh, s=True, ni=True)[0], meshAttr, f=True)
            cmds.select(itemMesh, r=True)
            cmds.parent(itemMesh, w=True)
            
    #----------------------------------------------------------------------
    def getTempMesh(self):
        """返回temp"""
        return self.tempMesh
    #----------------------------------------------------------------------
    def getTargetM(self):
        """返回目标体"""
        return self.targetM
    #----------------------------------------------------------------------
    def getBlendShape(self):
        """放回Blendshape"""
        return self.BlendNode
    #----------------------------------------------------------------------
    def getSculptM(self):
        """返回雕刻体"""
        return self.SculptM
    #----------------------------------------------------------------------
    
    def setTempBase(self, name):
        """返回temp基础"""
        self.tempBase = name
        
    #----------------------------------------------------------------------
    def setSculptM(self, name):
        """设置雕刻体"""
        self.SculptM = name
    #----------------------------------------------------------------------
    def setTargetM(self, name):
        """设置目标体"""
        self.targetM =  name
    #----------------------------------------------------------------------
    def callBackeCammand(self, cmd):
        """"""
        if cmd == 'add':
            undoID = cmds.scriptJob(event = ['Undo', self.refreshStaice], p = self.widow["window"])
            redoID = cmds.scriptJob(event = ['Redo', self.refreshStaice], p = self.widow["window"])
            
            self.callBackeID = (undoID, redoID)
        elif cmd == 'remove':
            for i in self.callBackeID:
                cmds.scriptJob(k=i, f = True)
    #----------------------------------------------------------------------
    def buidingCmd(self, listType = 3 , args=None):
        """创建命令"""
        baseM =  self.getMesh()
        targetM =  self.getTargetM()
        bsNode =  self.getBlendShape()
        na =  self.getSelectTreeName()
        menS1 = cmds.menuItem(self.widow['menuS1'], q = True, en = True)
        menS2 = cmds.menuItem(self.widow['menuS2'], q = True, en = True)
        menS3 = cmds.menuItem(self.widow['menuS'], q = True, en = True)
        check = cmds.checkBox(self.widow['checkBoxC'], q = 1, v = 1)
        if check:
            listType = 3
        else:
            listType = 1        
        if listType == 1:
            om.MGlobal.displayInfo('buidingCmd: ListL')
            name = cmds.textScrollList(self.widow['1stTerm'], q = 1, si=1)[0]
            coritem = getCrGrpItem(self.BlendNode, name)[name][0]
            #cmds.setAttr(self.BlendNode +'.' + name, 1)
            if mayaEnviron != '2017':
                if self.SculptM == None:
                    self.SculptM =  name + '_sculpt'
                #print self.BlendNode, self.mesh, self.SculptM, name, coritem
                reBlendshape.replaceOrAddBlendShapeItem(self.BlendNode, self.mesh, self.SculptM, name, coritem)
                if menS1 != True:
                    cmds.menuItem(self.widow['menuS1'], e = True, en = True)
                    cmds.menuItem(self.widow['menuB1'], e = True, en = False)
                    cmds.setAttr(self.mesh + '.visibility', 1)
                    cmds.setAttr(self.SculptM + '.visibility', 0)
                    cmds.delete(self.SculptM)
                    self.SculptM = None
                    cmds.select(cl = True)
                    cmds.button(self.widow['createSculpt'], e =1 , enable=1)
                    #cmds.menuItem('refresh', e=1, en=1)
                    cmds.button(self.widow['building'], e =1 , enable=0)
                else:
                    pass
            else:
                value = cmds.floatSliderGrp(self.widow['floatSliderGrpL'] , q = True, v = True)
                cmds.sculptTarget(self.BlendNode, e=True, target = coritem, ibw = value)
                cmds.button(self.widow['createSculpt'], e =1 , enable=1)
                cmds.button(self.widow['building'], e =1 , enable=0)
        elif listType == 2:
            om.MGlobal.displayInfo('buidingCmd: ListR')
            if menS2 != True:
                cmds.menuItem(self.widow['menuS2'], e = True, en = True)
                cmds.menuItem(self.widow['menuB2'], e = True, en = False)
            else:
                pass
        elif listType == 3:
            om.MGlobal.displayInfo('buidingCmd: corListR')       
            name =  na[0][0].replace('_', '') + '_' + na[1][0].replace('_', '') + '_cor'
            if name not in self.item:
                #n =  cmds.blendShape(bsNode, q= 1 , wc =1)
                #num = [x for x in cmds.listAttr('%s.inputTarget'%bsNode,m=1,hd=1,lf=1) if 'inputTargetGroup' in x][-1]
                #n =  int(num.split("[")[1][:-1]) + 1           
                #cmds.blendShape(bsNode, e=1, t = [baseM, n,targetM, 1 ])
                addBlendShape(name, self.BlendNode)
                coritem = getCrGrpItem(self.BlendNode, name)[name][0]
                #print coritem
                cmds.refresh()
                cmds.setAttr(self.BlendNode +'.' + name, 1)
                reBlendshape.replaceOrAddBlendShapeItem(self.BlendNode, self.mesh, self.SculptM, name, coritem)
    
                #SetParent_('correctShapeGrp', [self.targetM])
                cmds.setAttr('%s.visibility'%baseM, 1)
                #cmds.setAttr('%s.visibility'%targetM, 0)
                
                cmds.setAttr('%s.visibility'%self.SculptM, 0)
                cmds.button(self.widow['createSculpt'], e =1 , enable=1)
                cmds.menuItem('refresh', e=1, en=1)
                cmds.button(self.widow['building'], e =1 , enable=0)
                cmds.menuItem(self.widow['menuS'], e=1, enable =1)
                cmds.menuItem(self.widow['menuB'], e=1, enable =0)
                cmds.checkBox(self.widow['checkBoxC'], e = 1, v = 0)
                cmds.select(cl=1)
                self.item.append(targetM)
                
                self.connect_()
                #self.deletMesh_()
                
                #self.refechItem()
                self.setTextScrListCmd()
                #cmds.duplicate(self.SculptM)
                cmds.delete(self.SculptM)
                
            elif name in self.item :
                SculptM =  na[0][0].replace('_', '') + '_' + na[1][0].replace('_', '') + '_cor_sculpt'
                coritem = getCrGrpItem(self.BlendNode)[name][0]
                print '>>>>>>>', coritem
                reBlendshape.replaceOrAddBlendShapeItem(self.BlendNode, self.mesh, SculptM, name, coritem)
                
                cmds.setAttr('%s.visibility'%SculptM, 0)
                cmds.setAttr('%s.visibility'%self.mesh, 1)
                cmds.button(self.widow['createSculpt'], e =1 , enable=1)
                cmds.menuItem('refresh', e=1, en=1)
                cmds.button(self.widow['building'], e =1 , enable=0)
                cmds.menuItem(self.widow['menuS'], e=1, enable =1)
                cmds.menuItem(self.widow['menuB'], e=1, enable =0)
                cmds.checkBox(self.widow['checkBoxC'], e = 1, v = 0)
                #cmds.duplicate(self.SculptM)
                cmds.delete(self.SculptM)
                cmds.select(cl=1)
    #----------------------------------------------------------------------
    def getSelectTreeName(self):
        '''获取列表1，2的名字，返回列表名字'''

        nameIn = cmds.textScrollList(self.widow['1stTerm'], q=1 ,  si=1)
        nameIn1 = cmds.textScrollList(self.widow['2stTerm'], q=1 ,  si=1)
        return nameIn, nameIn1
    #----------------------------------------------------------------------
    def getConnectInfo(self, correctName):
        """"""
        try:
            attr = cmds.listConnections(self.BlendNode+"."+correctName, type ='animCurveUU')[0]
            if attr:
                resultAttr = cmds.listConnections(attr.split(".")[0],scn=True,s=True,d=False,plugs=True)[0]
            else:
                pass            
        except:
            if self.BlendNode in correctName:
                resultAttr = correctName
            else:
                resultAttr = self.BlendNode + "." + correctName
        #print 'getConnectInfo:', resultAttr

        return resultAttr
    #----------------------------------------------------------------------
    def getKeyframeValueList(self, correctName):
        """"""
        inputValue = cmds.keyframe(self.BlendNode+"."+correctName,q=1,fc=1,iv=1)
        #keyframCuont = cmds.keyframe(self.BlendNode+"."+correctName,q=1,keyframeCount=1)
        outValue = cmds.keyframe(self.BlendNode+"."+correctName,q=1,iv=1,vc=1)
        #print 'getKeyframeValueList>>------------>>', outValue
        if outValue != None:
            result = zip(inputValue[1::2], outValue[1::2])
        else:
            result = None
        return result
        
    #----------------------------------------------------------------------
    def connect_(self):
        """连接属性"""
        na =  self.getSelectTreeName()
        Dvname =  na[0][0].replace('_', '') + "_" +  na[1][0].replace('_', '') + '_DV'
        bsnode =  self.getBlendShape()
        Dvnode =  cmds.createNode('multiplyDivide', n = Dvname)
        cmds.connectAttr('%s.%s'%(bsnode, na[0][0]), '%s.input1X'%Dvnode, f=True)
        cmds.connectAttr('%s.%s'%(bsnode, na[1][0]), '%s.input2X'%Dvnode, f=True)
        cmds.connectAttr('%s.outputX'%Dvnode, '%s.%s'%(bsnode, self.targetM), f=True )
    #----------------------------------------------------------------------    
    def deletMesh_(self):
        """删除mesh"""
        cmds.delete(self.SculptM, self.targetM)
        cmds.delete()
    #----------------------------------------------------------------------
    def DeleShapeItem(self, listType=None, *args):
        """"""
        if listType == 1:
            om.MGlobal.displayInfo('DeleShapeItem %s'%listType)
            #cmds.undoInfo(openChunk=True)
            corName = cmds.textScrollList( self.widow['1stTerm'] , q=1,  selectItem=1)[0]
            if args != () and args[0] != False:
                print args[0]
                v = cmds.menuItem(args[0], q = 1, l = True)
            cmds.connectControl(self.widow['floatSliderGrpL'], self.BlendNode+".envelope", po = True)
        if listType == 2:
            om.MGlobal.displayInfo('DeleShapeItem %s'%listType)
            #cmds.undoInfo(openChunk=True)
            corName = cmds.textScrollList( self.widow['2stTerm'] , q=1,  selectItem=1)[0]
            cmds.connectControl(self.widow['floatSliderGrpR'], self.BlendNode+".envelope", po = True)
        if listType == 3:
            om.MGlobal.displayInfo('DeleShapeItem %s'%listType)
            #cmds.undoInfo(openChunk=True)
            corName = cmds.textScrollList( self.widow['textScrListCor'] , q=1,  selectItem=1)[0]
            cmds.connectControl(self.widow['floatSliderGrpCor'], self.BlendNode+".envelope", po = True)
        if cmds.confirmDialog( title='DeleteShape',
                               message='Are you sure?',
                               button=['Yes','No'],
                               defaultButton='Yes',
                               cancelButton='No',
                               dismissString='No') == 'Yes':
            if args != () and args[0] != False:
                v = cmds.menuItem(args[0], q = 1, l = True)
                itemData = getCrGrpItem(self.BlendNode)
                if int(float(v)* 1000 + 5000) != 5000 and int(float(v)* 1000 + 5000) != 6000:
                    mesh, attr = getConnection('{0}.inputTarget[0].inputTargetGroup[{1}].inputTargetItem[{2}].inputGeomTarget' .format (self.BlendNode, itemData[corName][0], int(float(v)* 1000 + 5000)))
                    try:
                        cmds.disconnectAttr(mesh, att, na = 1)
                    except:
                        pass
                    cmds.removeMultiInstance('{0}.inputTarget[0].inputTargetGroup[{1}].inputTargetItem[{2}]' .format (self.BlendNode, itemData[corName][0], int(float(v)* 1000 + 5000)), b=True)
                else:
                    deleteItem(self.BlendNode, corName)
            else:
                deleteItem(self.BlendNode, corName)
        else:
            pass
        cmds.refresh()
        self.refechItem()

    #----------------------------------------------------------------------
    def rename(self, listType, args =None):
        """"""
        if listType == 1:
            om.MGlobal.displayInfo('rename %s'%listType)
            corName = cmds.textScrollList( self.widow['1stTerm'] , q=1,  selectItem=1)[0]
            newName = promptDialogWin(titleDialog='EditBlesnShapeItemName', instrunctions='NewName', 
                                     text=corName, 
                                     arg=None)
            cmds.aliasAttr(newName, self.BlendNode + '.' + corName)
            self.refechItem()
        elif listType == 2:
            om.MGlobal.displayInfo('rename %s'%listType)
        else:
            om.MGlobal.displayInfo('rename %s'%listType)
            
        
        
    #--------------------------------------------------------------------------
    def correctMesh_(self, inputMesh, name, attr):
        """创建修正体"""
        if cmds.objExists(name+'_tempBase') == True:
            tempBase  =  name+'_tempBase'
        else:
            tempBase = createTarget(inputMesh,name+'_tempBase')
        
        if cmds.objExists(name+'_sculpt') == True:
            Sculpt =  name+'_sculpt'
        else:
            cmds.setAttr(attr, 1)
            Sculpt =  createTarget(inputMesh,name+'_sculpt')
        
        orgShape = [x for x in cmds.listRelatives(inputMesh, c=1) if 'Orig' in x][0]
        
        if cmds.objExists(name+'_cor') == True:
            target =  name + '_cor'
        else:
            cmds.setAttr ("%s.intermediateObject" %orgShape, 0)
            shape =  [x for x in cmds.listRelatives(inputMesh, c=1) if 'Orig' not in x][0]
            cmds.setAttr ("%s.intermediateObject" %shape, 1)
            target = createTarget(inputMesh,name+'_cor')
            
            cmds.setAttr ("%s.intermediateObject" %orgShape, 1)
            cmds.setAttr ("%s.intermediateObject" %shape, 0)
        if cmds.objExists(name+'BS') !=  True:
            corrBs =  cmds.blendShape(tempBase, Sculpt, target, n = name+'BS')
            cmds.blendShape(corrBs, e=1, w= [(0, -1), (1, 1)])
        elif cmds.objExists(name+'BS') ==  True:
            tempShape = cmds.listRelatives(tempBase, c=1)[0]
            SculptShape = cmds.listRelatives(Sculpt, c=1)[0]
            try:
                cmds.connectAttr ('%s.worldMesh[0]'%tempShape, '%s.inputTarget[0].inputTargetGroup[0].inputTargetItem[6000].inputGeomTarget'%(name+'BS'), f=1)
                cmds.connectAttr ('%s.worldMesh[0]'%SculptShape, '%s.inputTarget[0].inputTargetGroup[1].inputTargetItem[6000].inputGeomTarget'%(name+'BS'), f=1)
            except:
                pass
        
        return [tempBase, Sculpt, target]
    #----------------------------------------------------------------------
    def queryAttr(self, object , selectItemCor ):
        """查找属性"""
        #print 'run here'
        a =  cmds.listConnections('%s.%s'%(object, selectItemCor),source=1 )
        #print a
        inputAttrlist =  []
        if a:
            if a !=  self.BlendNode:
                input = cmds.listConnections(a,source=1 , connections=1)
                
                #print input
                if input:
                    for num in range(0, len(input), 2):
                        inputAttr =  cmds.connectionInfo(input[num], sourceFromDestination=1)
                        if inputAttr != '':
                            inputAttrlist.append(inputAttr)
                else:pass
                return inputAttrlist
        else:
            return inputAttrlist
    
    #----------------------------------------------------------------------
    def setselectItemCmd(self):
        """选择item命令"""
        attrlist = self.queryAttr(self.BlendNode,self.currSelItemCor)
        attr =  []
        om.MGlobal.displayInfo( 'setselectItemCmd: %s' % attrlist)
        if attrlist:
            for a in attrlist:
                attr.append(a.split('.')[-1])
        else:pass
        if attr:
            cmds.textScrollList( self.widow['1stTerm'], e=True, si = attr[0])
            cmds.textScrollList( self.widow['2stTerm'], e=True, si = attr[1])
            resultAttrA = self.getConnectInfo(attr[0])
            resultAttrB = self.getConnectInfo(attr[1])
            #print resultAttrA, resultAttrB
            resultAttrAValueList = self.getKeyframeValueList(attr[0])
            resultAttrBValueList = self.getKeyframeValueList(attr[1])
            if resultAttrA != None:
                #print ">>>>>setAttr1>>>", resultAttrA
                if resultAttrAValueList:
                    for v in  resultAttrAValueList:
                        if v[1] != 0.0:
                            cmds.setAttr(resultAttrA, v[0])
                else:
                    #print ">>>>>setAttr1"
                    cmds.setAttr(resultAttrA,1)
            if resultAttrB != None:
                #print ">>>>>setAttrB>>>", resultAttrB
                if resultAttrBValueList:
                    for v in  resultAttrBValueList:
                        if v[1] != 0.0:
                            cmds.setAttr(resultAttrB, v[0])
                else:
                    #print ">>>>>setAttrB"
                    cmds.setAttr(resultAttrB,1)    
        else:
            om.MGlobal.displayInfo( '%S.%s No connect' % (self.BlendNode,self.currSelItemCor))
        

    #----------------------------------------------------------------------
    def createTargetCmd(self,inputMesh, name, *args):
        """创建雕刻体命令"""
        bsNode = self.BlendNode
        #value = cmds.getAttr('%s.%s'%(bsNode, name))
        cmds.undoInfo(openChunk=True)
        #获得ID号
        bsData =  getCrGrpItem(bsNode)
        #ID =  bsData[name][0]
        ID = cmds.textScrollList( self.widow['textScrollID'] , q=1,  selectItem=1)[0]
        print ID
        attrlist = cmds.textScrollList( self.widow['textScrollWeightID'] , q=1,  allItems=1)
        valueDir = self.getAttrValue(bsNode, attrlist)
        for i in attrlist:
            if i != name and '_cor' not in i:
                try:
                    cmds.setAttr('%s.%s'%(bsNode, i), 0)
                except:
                    pass
            else:
                pass
                #cmds.setAttr('%s.%s'%(bsNode, name), 1)
    
        temp = createTarget(inputMesh, name)
        #cmds.setAttr('%s.%s'%(bsNode, name), 0)
        attr = self.getConnectInfo(name)
        cmds.setAttr(attr, 0)        
        for k, v in valueDir.items():
            try:
                cmds.setAttr('%s.%s'%(bsNode, k), v)
            except:
                pass
        cmds.connectAttr('%s.worldMesh[0]'%cmds.listRelatives(temp, c=1)[0], bsNode+'.'+ID, f=1)
        cmds.setAttr('%s.tx'%name, abs(cmds.xform(inputMesh,q=1,bb=1)[0]) + cmds.xform(inputMesh,q=1,bb=1)[3] + 1)
        cmds.undoInfo(closeChunk=True)
    #----------------------------------------------------------------------
    def getAttrValue(self, bsNode, attrlist):
        """获得属性值，返回值"""
        valueDir = {}
        for attr in attrlist:
            value = cmds.getAttr('%s.%s'%(bsNode, attr))
            if value != 0:
                valueDir[attr] = value
        return valueDir
    #----------------------------------------------------------------------
    def mirrCmd(self, *args):
        """镜像命令"""
        #attrlist = cmds.textScrollList( self.widow['textScrollWeightID'] , q=1,  allItems=1)
        attrlist = cmds.listAttr(self.BlendNode+".weight", m=True)
        valueDir =  self.getAttrValue(self.BlendNode, attrlist)
        #self.resetCmd()
        
        delteM = False
        mirr =  mirrBlendShape()
        org =  getOrigMesh(self.mesh, newName=None, offset=[0, 0, -10])
        mirr.setBase(org)
        if cmds.objExists(self.mirrM) == True:
            print '>>>>>', self.mirrM
            mirr.setShapeToMirr(self.mirrM)
            
        else:
            
            cmds.setAttr(self.BlendNode+'.'+self.mirrM, 1)
            self.mirrM = cmds.duplicate(self.mesh, n=self.mirrM)[0]
            #self.resetCmd()
            mirr.setShapeToMirr(self.mirrM)
            delteM = True
            
            print '//////////', self.mirrM
            
        mirr.mirrBlendShape()
        cmds.delete(org)
        #for k, v in valueDir.items():
            #try:
                #cmds.setAttr('%s.%s'%(bsNode, k), v)
            #except:
                #pass
        if delteM == True:
            cmds.delete(self.mirrM)
    #----------------------------------------------------------------------
    def _mirrViewMesh(self):
        """"""
        om.MGlobal.displayInfo('mirrViewMesh')
        print cmds.checkBox(self.widow['checkBoxMirr'], q = 1, v = True)
        if cmds.checkBox(self.widow['checkBoxMirr'], q = 1, v = True):
            print '>>>>', self.SculptM, 'mesh'
            self.viewMesh  =  getOrigMesh(self.mesh, self.SculptM + '_view', [0, 0, 0])
            self.mirrViewMesh =  cmds.duplicate(self.viewMesh, n = 'mirr_%s'%self.viewMesh)[0]
            cmds.move( -10, 0, 0, self.mirrViewMesh)
            self.mirrViewWarpMesh =  cmds.duplicate(self.mirrViewMesh, n = 'mirr_%s_wrap'%self.viewMesh)[0]
            cmds.setAttr(self.mirrViewWarpMesh + '.sx', -1)
            cmds.select(self.mirrViewMesh, self.mirrViewWarpMesh)
            cmds.CreateWrap()
            cmds.move(10, 0, 0, self.SculptM)
            cmds.blendShape(self.SculptM, self.mirrViewMesh, self.viewMesh, n = 'mirrBs', w = [(0, 1), (1, 1)])
            cmds.blendShape(self.SculptM, self.mirrViewWarpMesh, n = 'briegeBS', w = [(0, 1)])
            cmds.setAttr(self.mirrViewWarpMesh + '.visibility', 0)
            cmds.setAttr(self.viewMesh + '.visibility', 1)
            cmds.setAttr(self.mirrViewMesh + '.visibility', 1)
            
        else:
            if cmds.objExists(self.viewMesh) :
                cmds.delete(self.viewMesh , self.mirrViewMesh, self.mirrViewWarpMesh)
            if cmds.objExists(self.SculptM):
                cmds.move(-10, 0, 0, self.SculptM)
        
        
        
    #----------------------------------------------------------------------
    def checkBoxQuary(self):
        """"""
        if cmds.checkBox(self.widow['checkBoxCor'] ,q = 1, v=1):
            return True
        else :return False
    #----------------------------------------------------------------------
    def checkBoxOnCmd(self, *args):
        """"""
        #print args
        #cmds.checkBox(self.widow['checkBoxL'] ,e = 1, en=1)
        #cmds.checkBox(self.widow['checkBoxR'] ,e = 1, en=1)
        v = cmds.checkBox(self.widow['checkBoxCor'], q=True, v=True)
        corItem = self.getValuveList(self.BlendNode)
        correctNamelist = []
        for cor in  corItem:
            if '_cor' in cor:
                correctNamelist.append(cor)
        #print correctNamelist
        if correctNamelist != ["None"]:
            cmds.textScrollList(self.widow['textScrListCor'], e=True,ra=1)
            cmds.textScrollList( self.widow['textScrListCor'], e=True, append=correctNamelist)
        else:
            cmds.textScrollList(self.widow['textScrListCor'], e=True,ra=1)
            cmds.textScrollList( self.widow['textScrListCor'], e=True, append=["None"])        
        #om.MGlobal.displayInfo('checkBoxOnCmd')
    def checkBoxOffCmd(self, *args):
        """"""
        #print args
        #cmds.checkBox(self.widow['checkBoxL'] ,e = 1, en=0)
        #cmds.checkBox(self.widow['checkBoxR'] ,e = 1, en=0)
        v = cmds.checkBox(self.widow['checkBoxCor'], q=True, v=True)
        correctNamelist = cmds.listAttr('%s.weight'%(self.BlendNode), m=True)
        corlist = []
        for cor in correctNamelist:
            if "_cor" in cor:
                corlist.append(cor)
            
        if corlist:
            cmds.textScrollList(self.widow['textScrListCor'], e=True,ra=1)
            cmds.textScrollList( self.widow['textScrListCor'], e=True, append=corlist)
        else:
            cmds.textScrollList(self.widow['textScrListCor'],e=True,ra=1)
            cmds.textScrollList(self.widow['textScrListCor'], e=True, append=["None"])        
        #om.MGlobal.displayInfo('checkBoxOffCmd')
    #----------------------------------------------------------------------
    def checkBoxChangeOff(self, checkBoxNmae, textScrollList, *args):
        """"""
        #cmds.checkBox(checkBoxNmae,e = 1, v=0)
        #cmds.checkBox(checkBoxNmae1 ,e = 1, en=1)
        
        correctNamelist = cmds.listAttr('%s.weight'%(self.BlendNode), m=True)
        
        if correctNamelist:
            cmds.textScrollList(textScrollList, e=True,ra=1)
            cmds.textScrollList( textScrollList, e=True, append=correctNamelist)
        else:
            cmds.textScrollList(textScrollList, e=True,ra=1)
            cmds.textScrollList( textScrollList, e=True, append=["None"])
        om.MGlobal.displayInfo('checkBoxChangeOff') 
        cmds.refresh()
        
    def checkBoxChangeOn(self, checkBoxNmae, textScrollList, *args):
        """"""
        #cmds.checkBox(checkBoxNmae1 ,e = 1, v=0)
        #cmds.checkBox(checkBoxNmae1 ,e = 1, en=0)
        v = cmds.checkBox(checkBoxNmae, q=True, v=True)
        if v:
            correctNamelist = self.getValuveList(self.BlendNode)
            if correctNamelist:
                
                cmds.textScrollList(textScrollList, e=True,ra=1)
                cmds.textScrollList( textScrollList, e=True, append=correctNamelist)
            else:
                cmds.textScrollList(textScrollList, e=True,ra=1)
                cmds.textScrollList( textScrollList, e=True, append=['None'])                
        else:
            correctNamelist = cmds.listAttr('%s.weight'%(self.BlendNode), m=True)
            cmds.textScrollList(textScrollList, e=True,ra=1)
            cmds.textScrollList( textScrollList, e=True, append=['None'])
        cmds.refresh()
        #print 'checkBoxChangeOn', textScrollList, 'value' , v
    #----------------------------------------------------------------------
    #----------------------------------------------------------------------
    def _addShape(self,  *args):
        """"""
        addBlendShape(newItemName=None, blendShapeNode=self.BlendNode)
        self.refechItem()
 
#--------------------------------------------------------------------------
def createTarget(inputMesh,name):
    shape = cmds.createNode('mesh')
    transform = cmds.listRelatives(shape,p=1)
    cmds.connectAttr('%s.worldMesh'%inputMesh,'%s.inMesh'%shape,f = True)
    cmds.sets(transform ,e = 1 ,forceElement = 'initialShadingGroup')
    transformT = cmds.duplicate(transform,rr =1 )[0]
    #cmds.move(0,0,0,transformT,r=1,os=1,wd = True,)
    newname = cmds.rename(transformT,name)
    cmds.delete(transform)
    cmds.select(newname)
    #inputTransform =  cmds.pickWalk(d='up')
    pos=cmds.xform(inputMesh,q=1,ws=1,rp=1)
    pos1=cmds.xform(inputMesh,q=1,ws=1,t=1)
    cmds.xform(newname,ws=1,t=pos1)
    cmds.xform(newname,ws=1,rp=pos)    
    return newname
#--------------------------------------------------------------------------
def correctMesh(inputMesh, name):
    if cmds.objExists(name+'_tempBase') == True:
        tempBase  =  name+'_tempBase'
    else:
        tempBase = createTarget(inputMesh,name+'_tempBase')
    
    if cmds.objExists(name+'_sculpt') == True:
        Sculpt =  name+'_sculpt'
    else:
        Sculpt =  createTarget(inputMesh,name+'_sculpt')
    
    orgShape = [x for x in cmds.listRelatives(inputMesh, c=1) if 'Orig' in x][0]
    
    if cmds.objExists(name+'_cor') == True:
        target =  name + '_cor'
    else:
        cmds.setAttr ("%s.intermediateObject" %orgShape, 0)
        shape =  [x for x in cmds.listRelatives(inputMesh, c=1) if 'Orig' not in x][0]
        cmds.setAttr ("%s.intermediateObject" %shape, 1)
        target = createTarget(inputMesh,name+'_cor')
        
        cmds.setAttr ("%s.intermediateObject" %orgShape, 1)
        cmds.setAttr ("%s.intermediateObject" %shape, 0)
##    if cmds.objExists(name+'BS') !=  True:
##        corrBs =  cmds.blendShape(tempBase, Sculpt, target, n = name+'BS')
##        cmds.blendShape(corrBs, e=1, w= [(0, -1), (1, 1)])
##    elif cmds.objExists(name+'BS') ==  True:
##        tempShape = cmds.listRelatives(tempBase, c=1)[0]
##        SculptShape = cmds.listRelatives(Sculpt, c=1)[0]
##        try:
##            cmds.connectAttr ('%s.worldMesh[0]'%tempShape, '%s.inputTarget[0].inputTargetGroup[0].inputTargetItem[6000].inputGeomTarget'%(name+'BS'), f=1)
##            cmds.connectAttr ('%s.worldMesh[0]'%SculptShape, '%s.inputTarget[0].inputTargetGroup[1].inputTargetItem[6000].inputGeomTarget'%(name+'BS'), f=1)
##        except:
##            pass
    
    return [tempBase, Sculpt, target]
#----------------------------------------------------------------------
def getOrigMesh(mesh, newName=None, offset=[0, 0, -10]):
    """"""
    origShape = cmds.ls(cmds.listHistory(mesh), et='mesh', intermediateObjects=True, long=True)[0]
    restoredGeo = cmds.duplicate(origShape, name=newName)[0]
    tmpShape = cmds.pickWalk(restoredGeo,d = 'down')[0]
    restGeoShape = restoredGeo + 'Shape'
    cmds.rename(tmpShape, restGeoShape)
    
    cmds.connectAttr(origShape + '.outMesh', restGeoShape + '.inMesh')
    cmds.refresh()
    cmds.disconnectAttr(origShape + '.outMesh', restGeoShape + '.inMesh')
    
    #Unlock channels
    xyz = 'xyz'
    trs = 'trs'
    for m in trs:
        for a in xyz:
            cmds.setAttr(restoredGeo + '.{0}{1}'.format(m, a), l = False)
    cmds.xform(restoredGeo, t = offset)
    #cmds.select(cl = True)
    print restoredGeo, origShape
    return restoredGeo
#----------------------------------------------------------------------
def getCrGrpItem(blendShapeNode=None,correctiveName=None,arg=None):
    # BLENDSHAPE PATH

    iTg = '%s.inputTarget[0]' %blendShapeNode
    iTi = '.inputTargetItem'
    dicCrGrp = {}
    allCrName = cmds.listAttr(blendShapeNode + '.weight', m=True)
    allCrGrp = cmds.getAttr(blendShapeNode + '.weight', mi=True)
    for nm in allCrName:
        dicCrGrp[nm] = allCrGrp[allCrName.index(nm)]
    '''
    print 'dicCrGrp --> ', dicCrGrp
    print '---dicCrGrp.keys()> ', dicCrGrp.keys()
    print '---dicCrGrp.values()> ', dicCrGrp.values()
    print '---dicCrGrp["teste"]> ', dicCrGrp['teste']
    '''
    dicCrGrpItem = {}
    for crName in dicCrGrp.keys():
        iTgGr = '.inputTargetGroup[%s]' %dicCrGrp[crName]
        grpItem = cmds.getAttr(iTg + iTgGr + iTi, mi=True)
        if grpItem == None:
            #print '*** corrective: %s has no item, restauring...' %correctiveName
            cmds.getAttr(iTg + iTgGr + '.inputTargetItem[6000].inputGeomTarget')
            cmds.getAttr(iTg + iTgGr + '.inputTargetItem[6000].inputPointsTarget')
            cmds.getAttr(iTg + iTgGr + '.inputTargetItem[6000].inputComponentsTarget')
            grpItem = [6000]
            dicCrGrpItem[crName] = (dicCrGrp[crName], grpItem)
        dicCrGrpItem[crName] = (dicCrGrp[crName], grpItem)
    #print 'dicCrGrpItem----------> ', dicCrGrpItem
    return dicCrGrpItem

#----------------------------------------------------------------------
def getGeoNameFromNode(blendShapeNode=None):
    """"""
    hist = cmds.listHistory(blendShapeNode, f = True)
    shapeGro = cmds.ls(hist, type = 'mesh')[0]
    geoName = cmds.listRelatives(shapeGro, ap = True)[0]
    shapeGroSplit = shapeGro.split('|')[-1]
    if str(shapeGroSplit) == str(geoName):
        cmds.rename(shapeGro, str(shapeGroSplit) + 'Shape')
    return geoName
#----------------------------------------------------------------------
def addBlendShape(newItemName=None, blendShapeNode = None, *args):
    """"""
    #print blendShapeNode
    geo = getGeoNameFromNode(blendShapeNode)
    if not newItemName:
        #om.MGlobal.displayError('No name')  
        newItemName = promptDialogWin(titleDialog='Add Corrective',instrunctions='Name:')        
    if newItemName != None:
        newCorrectiveGeo =  getOrigMesh(geo, newItemName, offset=[0, 0, 0])
    TargetGroup = []
    dicValues = getCrGrpItem(blendShapeNode).values()
    for grp in  dicValues:
        TargetGroup.append(grp[0])
    itemTargetGroups = list(sorted(set(TargetGroup)))
    #raise 
    if newItemName != None:
        try:
            for correctiveGroup in  itemTargetGroups:
                if correctiveGroup + 1 not in itemTargetGroups:
                    newGroup =  correctiveGroup + 1
                    cmds.blendShape(blendShapeNode, e = True,
                                    t = [str(geo), int(newGroup), newCorrectiveGeo, 1.0])
                    break
                   
        except:
            cmds.blendShape(blendShapeNode, e = True, t = [str(geo), int(0), newCorrectiveGeo, 0.0])
    else:pass
    if newItemName != None:
        cmds.delete(newCorrectiveGeo)
def promptDialogWin(titleDialog='None',
                        instrunctions='Default',
                        text=None,
                        arg=None):
      
    #print 'def promptDialogWin'
    dialog = cmds.promptDialog(title=titleDialog,
                               message=instrunctions,
                               tx=text,
                               button=['OK', 'Cancel'],
                               defaultButton='OK',
                               cancelButton='Cancel',
                               dismissString='Cancel')

    if dialog == 'OK':
        text = cmds.promptDialog(query=True, text=True)
    else:
        text = None
        
    return text
#=======================================================================
def deleteItem(blendShapeNode=None,correctiveName=None,arg=None):
        allCr = cmds.listAttr(blendShapeNode + '.weight', m=True)
        # Check to see what InputConnection is..
        if not isinstance(correctiveName, list):
                correctiveName = [correctiveName]
        #=======================================================================
        dicCrGrpItem = getCrGrpItem(blendShapeNode,correctiveName)
        iTg = '%s.inputTarget[0]' %blendShapeNode
        #print allCr
        if len(allCr) >= 2:
            for cr in correctiveName:
                comboNodes = ['blendColors', 'multiplyDivide', 'condition']
                # Check if there is a combo node attatched to it to be deleted
                # Combo correctives
                selCorrective = blendShapeNode + '.' + cr
                try:
                    InputConnection = cmds.listConnections(selCorrective, p=True)[0]
                    blendCrNode = InputConnection.split('.')[0]
                    for nodes in comboNodes:
                        if str(cmds.objectType(blendCrNode)) == nodes:
                            cmds.delete(blendCrNode)
                except:
                    pass

                # ----------- COMBO BLEND COLORS DELETED --------------------------
                correctiveItem = dicCrGrpItem[cr][1]
                #print 'allCrGrp.index(grp) ', dicCrGrpItem[cr][1]
                correctiveGroup = dicCrGrpItem[cr][0]
                #print 'dicCrGrpItem[cr][0] ', dicCrGrpItem[cr][0]
                iTgGr = '.inputTargetGroup[%s]' %correctiveGroup
  
                blendShapeCorrective = blendShapeNode + '.' + cr
                inputAttrCnx = cmds.listConnections(blendShapeCorrective,
                                                    s=True,
                                                    d=True,
                                                    p=True)
                outputAttrCnx = cmds.listConnections(blendShapeCorrective,
                                                     s=False,
                                                     d=True,
                                                     p=True)
  
                try:
                    if inputAttrCnx:
                        cmds.disconnectAttr(inputAttrCnx[0], blendShapeNode + '.' + cr)
                    if outputAttrCnx:
                        cmds.disconnectAttr(outputAttrCnx, blendShapeNode + '.' + cr)
                except:
                    pass
  
                cmds.aliasAttr(blendShapeNode + '.' + cr, rm=True)
                removePath = blendShapeNode + '.weight[' + str(correctiveGroup) + ']'
                cmds.removeMultiInstance(removePath, b=True)

                for item in correctiveItem:
                    iTi = '.inputTargetItem[%s]' %item
                    gatherGroupCorrective = iTg + iTgGr + iTi
                    cmds.removeMultiInstance(gatherGroupCorrective, b=True)
                    
                cmds.removeMultiInstance(iTg + iTgGr, b=True)
                cmds.refresh()
                print 'deleteCorrective'
        else:
            print 'The last corrective cannot be deleted, instead delete the blendShape node specified'  
            
        cmds.refresh()    

#----------------------------------------------------------------------
def SetParent_(group = 'sculptShapeGrp', *args):

    """"""
    if cmds.objExists(group):
        for i in args:
            if cmds.listRelatives(group, c=1) == None:
                return cmds.parent(i, group)
            elif i[0] not in cmds.listRelatives(group, c=1):
                #print i
                return cmds.parent(i, group)
            else:pass
    else:
        group =  cmds.createNode('transform', n=group)
        for i in args:
            return cmds.parent(i, group)
#----------------------------------------------------------------------
def queryAttrLockOnOff(BlendNode, attr):
    """返回 True，表示lock或者链接且是通过其他属性改变值，返回False，可以编辑属性值"""
    #print 'queryAttrLockOnOff:', attr
    input = cmds.connectionInfo(BlendNode+'.'+attr, sfd=1)
    if input:
        if  cmds.nodeType(input) != 'animCurveUU':
            return True
        if  cmds.nodeType(input) == 'animCurveUU':
            return False
    else:
        return False
def getConnection(destName):
    '''输入：节点属性  功能：获取节点属性的上游输入节点属性'''
    if cmds.connectionInfo( destName, isDestination = True):
        destination = cmds.connectionInfo(destName,getExactDestination=True)
        inputAttr = cmds.listConnections(destination,p=1)
        #print inputAttr[0],destination
        return inputAttr[0],destination
    else:
        return None,destName


########################################################################
class mirrBlendShape():
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.base =  ''
        self.shapeToMirr =  ''
    #----------------------------------------------------------------------
    def mirrBlendShape1(self):
        """"""
        base = self.base
        shapeToMirr = self.shapeToMirr
        #print base, shapeToMirr
        tx = cmds.getAttr('%s.tx'%shapeToMirr)
        ty = cmds.getAttr('%s.ty'%shapeToMirr)
        tz = cmds.getAttr('%s.tz'%shapeToMirr)
        
        cmds.select(base, r=True)
        baseDup =  cmds.duplicate(rr=True, name = 'baseDup')
        cmds.DeleteHistory()
        
        dup =  cmds.duplicate(rr=True, name = 'mBs_rest_neg')
        for x in 'trs':
            for y in 'xyz':
                #print dup+'.%s%s'%(x, y)
                cmds.setAttr(dup[0]+'.%s%s'%(x, y), l=False)
        cmds.setAttr('%s.sx'%dup[0], -1)
        
        absShapePosition = cmds.xform(shapeToMirr, q=True, a=True, t=True)
        
        for x in 'trs':
            for y in 'xyz':
                if cmds.getAttr(shapeToMirr+'.%s%s'%(x, y), l = True)==True:
                    cmds.setAttr(shapeToMirr+'.%s%s'%(x, y), l=False)   
        
        cmds.select(baseDup, shapeToMirr, r=True)
        cmds.delete(cmds.pointConstraint(offset=[0, 0, 0], weight = 1))
        
        cmds.DeleteHistory()
        
        cmds.select(shapeToMirr, r=True)
        
        dupTempNeg = cmds.duplicate(returnRootsOnly=True, n = 'mBs_temp_neg')
        cmds.setAttr('%s.scaleX'%dupTempNeg[0], -1)
        
        cmds.select(dup, dupTempNeg, r=True)
        
        blend = cmds.blendShape(parallel=True)
        
        cmds.setAttr('%s.%s'%(blend[0], dup[0]), 1)
        
        #========================================
        
        cmds.select(baseDup, r=True)
        dupNeg = cmds.duplicate(rr=True, n = 'mBS_neg')
        
        for x in 'trs':
            for y in 'xyz':
                if cmds.getAttr(dupNeg[0]+'.%s%s'%(x, y), l = True)==True:
                    cmds.setAttr(dupNeg[0]+'.%s%s'%(x, y), l=False)
        
        cmds.select(dupNeg, r=True)
        cmds.select(dupTempNeg, add=True)
        
        cmds.CreateWrap()
        

        #vsd.create()
        
        cmds.setAttr('%s.%s'%(blend[0], dup[0]), 0)
        cmds.select(dupNeg, r=True)
        
        cmds.DeleteHistory()
        
        cmds.delete(dup[0], dupTempNeg, '%sBase'%dupTempNeg[0])
        
        cmds.setAttr('%s.tx'%dupNeg[0], tx)
        cmds.setAttr('%s.ty'%dupNeg[0], ty)
        cmds.setAttr('%s.tz'%dupNeg[0], tz)
        
        cmds.setAttr('%s.tx'%shapeToMirr, tx)
        cmds.setAttr('%s.ty'%shapeToMirr, ty)
        cmds.setAttr('%s.tz'%shapeToMirr, tz)
        
        new = cmds.rename(dupNeg[0], 'mirr_%s'%shapeToMirr)
        cmds.delete(baseDup)
        return new
    #----------------------------------------------------------------------
    def mirrBlendShape(self):
        """"""
        base = self.base
        shapeToMirr = self.shapeToMirr
        #print base, shapeToMirr
        tx = cmds.getAttr('%s.tx'%shapeToMirr)
        ty = cmds.getAttr('%s.ty'%shapeToMirr)
        tz = cmds.getAttr('%s.tz'%shapeToMirr)
        
        cmds.select(base, r=True)
        baseDup =  cmds.duplicate(rr=True, name = 'baseDup')
        cmds.DeleteHistory()
        
        dup =  cmds.duplicate(rr=True, name = 'mBs_rest_neg')
        for x in 'trs':
            for y in 'xyz':
                #print dup+'.%s%s'%(x, y)
                cmds.setAttr(dup[0]+'.%s%s'%(x, y), l=False)
        cmds.setAttr('%s.sx'%dup[0], -1)
        
        
        for x in 'trs':
            for y in 'xyz':
                if cmds.getAttr(shapeToMirr+'.%s%s'%(x, y), l = True)==True:
                    cmds.setAttr(shapeToMirr+'.%s%s'%(x, y), l=False)   
        
        cmds.select(shapeToMirr, baseDup, r=True)
        cmds.delete(cmds.pointConstraint(offset=[0, 0, 0], weight = 1))
        
        cmds.DeleteHistory()        
        print shapeToMirr, dup
        
        cmds.select(dup[0], r=True)
        cmds.select(baseDup[0], add=True)
        
        defomer =  vsd.create()
        
        blend = cmds.blendShape(shapeToMirr, dup[0], w=[0, 0])
        cmds.setAttr("%s.initialize"% defomer, 1)
        cmds.blendShape(blend[0] , e=True, w = [0, 1])

        cmds.select(dup[0], r=True)
        
        #cmds.DeleteHistory()
                
        cmds.setAttr('%s.tx'%dup[0], tx)
        cmds.setAttr('%s.ty'%dup[0], ty)
        cmds.setAttr('%s.tz'%dup[0], tz)
        
        cmds.setAttr('%s.tx'%shapeToMirr, tx)
        cmds.setAttr('%s.ty'%shapeToMirr, ty)
        cmds.setAttr('%s.tz'%shapeToMirr, tz)
        
        if '|'in  shapeToMirr:
            new =  cmds.rename(baseDup, 'mirr_%s'%(shapeToMirr.split("|")[-1]))
        else:
            new = cmds.rename(baseDup, 'mirr_%s'%shapeToMirr)
        #cmds.delete(dup[0])
        return new
    #----------------------------------------------------------------------
    def setBase(self, mesh):
        """"""
        self.base = mesh
        return self.base
    #----------------------------------------------------------------------
    def setShapeToMirr(self, mesh):
        """"""
        self.shapeToMirr = mesh
        return self.shapeToMirr
    
#----------------------------------------------------------------------
########################################################################
class mirrMeshShapeUI(mirrBlendShape):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.ui = "mirrShapeUI"
        self.version = '1.0'
        self.orig = None
        self.targst = None
    def deleteUI(self):
        for x in [x for x in cmds.lsUI(wnd=True) if 'mirrShapeUI' in x]:
            cmds.deleteUI(x)
        if  cmds.windowPref(self.ui, ex =True):
            cmds.windowPref(self.ui, r = True)
    #----------------------------------------------------------------------
    def Ui(self, *args):
        """"""
        self.deleteUI()
        self.win = cmds.window(self.ui, t =self.ui + self.version, wh = [300, 100])
        self.layout = cmds.columnLayout(adj=1)
        cmds.separator(vis = 1,style='in',w = 100,h=5)
        self.rowLayout  =  cmds.rowLayout( numberOfColumns=1, columnWidth=(1, 300), adjustableColumn=1, columnAlign=(1, 'left'),columnOffset1=-300 )
        self.textFieldButtonGrp = cmds.textFieldButtonGrp(l = '>>>Orig',bl = '<<',cw3=[50, 260,50], adjustableColumn= 2, numberOfPopupMenus=True, bc = self.setOrigMesh) #
        cmds.popupMenu()
        self.menuItemSel =  cmds.menuItem('selection', c=lambda *args: self.selCmd(1))
        cmds.setParent('..')
        
        self.layout1 = cmds.columnLayout(adj=1)
        cmds.separator(vis = 1,style='in',w = 100,h=5)
        self.rowLayout1  =  cmds.rowLayout( numberOfColumns=1, columnWidth=(1, 300), adjustableColumn=1, columnAlign=(1, 'left'),columnOffset1=-300 )
        self.textFieldButtonGrp1 = cmds.textFieldButtonGrp(l = '>>>Targt',bl = '<<',cw3=[50, 260,50], adjustableColumn= 2, numberOfPopupMenus=True, bc = self.setTargetMesh) #
        cmds.popupMenu()
        self.menuItemSel1 =  cmds.menuItem('selection', c=lambda *args: self.selCmd(2))
        cmds.setParent('..')
        
        cmds.separator(vis = 1,style='in',w = 100,h=5)
        
        cmds.button(l = 'MirrMesh', c = self.mirrCammand)
        
        cmds.showWindow(self.win)
    #----------------------------------------------------------------------
    def setOrigMesh(self, *arfs):
        """"""
        obj = cmds.ls(sl=True, l = True)[0]
        split = obj.split("|")[-1]
        cmds.textFieldButtonGrp(self.textFieldButtonGrp , e = True, text = split)
        self.orig = {split: obj,}
    #----------------------------------------------------------------------
    def setTargetMesh(self, *args):
        """"""
        obj = cmds.ls(sl=True, l = True)[0]
        split = obj.split("|")[-1]
        cmds.textFieldButtonGrp(self.textFieldButtonGrp1, e = True, text = split)
        self.targst = {split: obj,}
    #----------------------------------------------------------------------
    def setBaseMesh(self, *args):
        """"""
        
        self.setBase(self.orig.values()[0])
    #----------------------------------------------------------------------
    def setMeshToMirr(self, *args):
        """"""
        self.setShapeToMirr(self.targst.values()[0])
    #----------------------------------------------------------------------
    def mirrCammand(self, *args):
        """"""
        self.setBaseMesh()
        self.setMeshToMirr()
        self.mirrBlendShape()
    #----------------------------------------------------------------------
    def selCmd(self, mun = None):
        """"""
        if mun == 1:
            cmds.select(self.orig.values()[0])
        elif mun == 2:
            cmds.select(self.targst.values()[0])
        else:
            pass
