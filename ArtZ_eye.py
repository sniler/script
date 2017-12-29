#!/user/bin.evn python
#-*- coding: UTF-8 -*-
#Author:   Zhang Shengxin -- <EMail: 360418420@qq.com || zsxaa--12@163.com>


__author__  = 'Zhang Shengxin -- <EMail: 360418420@qq.com || zsxaa--12@163.com> '
__version__ = '2.0'
__status__  = "beta"
__date__    = "2014/8/1"
__using__   = """"""

import os, sys
import  maya.cmds as  mc
import maya.OpenMaya as om
from functools import partial

def createJoint(eyeRoot,name):
    """"""
    selVertexs = mc.ls(sl=True,l=True,fl=True)
    rootpos = mc.xform(eyeRoot,q=True,ws=True,t=True)
    for i in xrange(len(selVertexs)):
        endpos = mc.xform(selVertexs[i],q=True,ws=True,t=True)
        mc.select(cl=True)
        jnt1 = mc.joint(n="{0}.{1}_start".format(name,i),p = rootpos)
        jnt2 = mc.joint(n="{0}.{1}_end".format(name,i),p = endpos)
        mc.joint(jnt1,e=True, zso=True, oj = "xyz", sao = "yup")
        mc.joint(jnt2,e=True, zso=True, oj = "xyz", sao = "yup")
        mc.joint(jnt2,e=True,o = [0,0,0])
#----------------------------------------------------------------------
def getPointOnCurvePosition(curve, point):
    """"""
    # 转化曲线为api对象
    sel = om.MSelectionList()
    sel.add(curve)
    #转化为DAG对象
    dagpath = om.MDagPath()
    sel.getDagPath(0,dagpath)
    #转化为MFnNurbsCurve对象
    cv = om.MFnNurbsCurve(dagpath)
    #转化为MPoint对象
    pos = om.MPoint(point[0],point[1],point[2])
    #获得点在曲线上的dian
    onCurvePos = cv.closestPoint(pos,None,0,om.MSpace.kWorld)
    return onCurvePos.x,onCurvePos.y,onCurvePos.z

#----------------------------------------------------------------------
def createLocatorOnCurve(curve,positionObjectlist):
    """"""
    for x in xrange(len(positionObjectlist)):
        pos = mc.xform(positionObjectlist[x],q=True,ws=True,t=True)
        onCurvePos= getPointOnCurvePosition(curve,pos)
        locator = mc.spaceLocator(n='{0}_loc'.format(positionObjectlist[x]))
        mc.move(onCurvePos[0],onCurvePos[1],onCurvePos[2],locator,r=1)
        
def getParamAtPointOnCurve(curve, point):
    """"""
    # 转化曲线为api对象
    sel = om.MSelectionList()
    sel.add(curve)
    #转化为DAG对象
    dagpath = om.MDagPath()
    sel.getDagPath(0,dagpath)
    #转化为MFnNurbsCurve对象
    cv = om.MFnNurbsCurve(dagpath)
    #转化为MPoint对象
    pos = om.MPoint(point[0],point[1],point[2])
    #获得点在曲线上的dian
    prmate = None
    cv.getParamAtPoint(pos,prmate,om.MSpace.kWorld)
    return prmate


########################################################################
class eyeRig(object):
    """"""
    __metaclass__=type 
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.attributes = [("aimLock" ,  1 ) , 
                           ("eyeUpperX",  0),
                           ("eyeUpperY", 0),
                           ("eyeLowerX" , 0),
                           ("eyeLowerY" , 0),
                           ("setUprlip" , "AboutUprLip"),
                           ("uprlip_dn_limit", -15),
                           ("uprlip_up_limit", 35),
                           ("uprlip_ty_radio", -20),
                           ("uprlip_ry_radio", 0.3),
                           ("uprlip_rz_radio", -20),
                           ("set_lwrlip", "AboutLwrLip"),
                           ("lwrlip_dn_limit", -30),
                           ("lwrlip_up_limit", 15),
                           ("lwrlip_ty_radio", 20),
                           ("lwrlip_ry_radio", 0.3),
                           ("lwrlip_rz_radio", 20),
                           ('uprlip_tyUp_radio', 20),
                           ('lwrlip_tyDn_radio', 10),
                           ('speed', 0.15)
                           ]
        self.locatorList =  []
        self.name =  None
        self.eyeRigGrp =  "eyeRigGrp"
        self.eyeCtrlGrp  =  "eyeCtrlGrp"
        self.eyelipRigGrp =  "eyelipRigGrp"
        self.eyeAim_zero =  "eyeAim_zero"
        self.aimUpObjGrp =  "eyeAimUpObjGrp"
        self.distance = None
        self.aimlist = []
        self.ctrlList =  []
        self.lockAttr =  ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
        self.locatorListRestParent = []#[(None, None), (None, None)]
        self.length =  None
        self.eyeLocatorAim = []
    #----------------------------------------------------------------------
    def setLength(self):
        """"""
        self.length =  mc.getAttr(self.locatorList[0]+'.length')
        return 'setLegth: ', self.length
    #----------------------------------------------------------------------
    def getLength(self):
        """"""
        return self.length
    #----------------------------------------------------------------------
    def createLocator(self, *args):
        """"""
        
        eyeLocatorL =  mc.spaceLocator(n="eye_L_Loc")[0]
        eyeLocatorLAim =  mc.spaceLocator(n="eye_L_Loc_aim")[0]
        mc.move(2, 22, 4.5, eyeLocatorL)
        mc.move(2, 22, 6.5, eyeLocatorLAim)
        eyeLocatorR =  mc.spaceLocator(n="eye_R_Loc")[0]
        eyeLocatorRAim =  mc.spaceLocator(n="eye_R_Loc_aim")[0]
        mc.move(-2, 22, 4.5, eyeLocatorR)
        mc.move(-2, 22, 6.5, eyeLocatorRAim)
        
        #aimConstraint
        for i in [(eyeLocatorL, eyeLocatorLAim), (eyeLocatorR, eyeLocatorRAim)]:
            grp = mc.group(em=True, n='%s_grop' % i[1])
            mc.delete(mc.parentConstraint(i[1], grp, mo=False, w=True))
            mc.parent(i[1], grp)
            
            mc.pointConstraint(i[0], grp, mo=True, w=True)
            mc.aimConstraint(i[1], i[0], offset = (0, 0, 0), aimVector = (0, 0, 1), worldUpType='vector', worldUpVector=(0, 1, 0), w=1)
            mc.setAttr('%s.r' % i[0], k=False, ch=False)
            for x in ['x', 'y', 'z']:
                mc.setAttr('%s.r%s' % (i[0], x), l=True , k=False, channelBox=False)
        
        self.setLoactor([eyeLocatorL, eyeLocatorR])
        self.eyeLocatorAim.append(eyeLocatorLAim)
        self.eyeLocatorAim.append(eyeLocatorRAim)
        mc.addAttr([eyeLocatorL, eyeLocatorR], longName = 'length', k = True, dv = 5, at = 'float')
        
    #----------------------------------------------------------------------
    def createCvCtrl(self, name):
        """"""
        self.setLength()
        #curve -d 1 -p 0 0 0 -p 0 0 7 -p -1 0 6 -p 0 0 7 -p 1 0 6 -p 0 0 7 -p 0 1 6 -p 0 0 7 -p 0 -1 6 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 ;
        cv =  mc.curve(n=name+"_cv", d = 1, p = [(0, 0, 0), (0, 0, self.length), (-(self.length*0.1), 0, (self.length-(self.length*0.1))), (0, 0, self.length), ((self.length*0.1), 0, (self.length-(self.length*0.1))), (0, 0, self.length), (0, (self.length*0.1), (self.length-(self.length*0.1))), (0, 0, self.length), (0, -(self.length*0.1), (self.length-(self.length*0.1)))], k = [0, 1, 2, 3, 4, 5, 6, 7, 8 ])
        shapes =  mc.listRelatives(cv, c=1)
        #shapes =  mc.rename(shapes[0], name+"_cvShape")
        mc.select(cl=True)
        ctrl  =  mc.joint(n=name)
        for i in  xrange(len(shapes)):
            new =  mc.rename(shapes[i], "{0}Shape".format(name))
            mc.parent(new, ctrl, r=True, s=True)
        #curve -d 1 -p 0 0 1 -p 0 0 -1 -p 0 0 0 -p -1 0 0 -p 1 0 0 -p 0 0 0 -p 0 1 0 -p 0 -1 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 ;
        aimCtrl =  mc.curve(n="{0}_aim".format(name), d = 1, p = [(0, 0, (self.length*0.1)), (0, 0, -(self.length*0.1)), (0, 0, 0), (-(self.length*0.1), 0, 0), ((self.length*0.1), 0, 0), (0, 0, 0), (0, -(self.length*0.1), 0), (0, (self.length*0.1), 0)], k = [0, 1, 2, 3, 4, 5, 6, 7])
        shapes =  mc.listRelatives(aimCtrl, c=1)
        for i in  xrange(len(shapes)):
            mc.rename(shapes[i], "{0}_aimShape".format(name))
        mc.delete(cv)
        
        self.distance = (mc.getAttr("{0}.boundingBoxMax".format(ctrl))[0][2]  - mc.getAttr("{0}.boundingBoxMin".format(ctrl))[0][2])
        #self.distance +=  (mc.getAttr("{0}.boundingBoxMax".format(aimCtrl))[0][2]  - mc.getAttr("{0}.boundingBoxMin".format(aimCtrl))[0][2])
         
        print self.distance
        return ctrl, aimCtrl
    #----------------------------------------------------------------------
    def __getCtrlDdiatance(self):
        """"""
        pass
        
    #----------------------------------------------------------------------
    def addAttributes(self, ctrl):
        """"""
        for k in  self.attributes:
            
            if k[0] == "aimLock":
                mc.addAttr(ctrl, longName=k[0], defaultValue=k[1], minValue=0.00000, maxValue=1.0, k=1)
            
            elif  "Upper" in  k[0] or  "Lower" in  k[0] :
                mc.addAttr(ctrl, longName=k[0], defaultValue=k[1], minValue=-1.0, maxValue=1.0 , k=1)
                
            elif  k[0] == "setUprlip" or  k[0] == "set_lwrlip":
                mc.addAttr(ctrl, longName = k[0], at = "enum", enumName = k[1], k=1)
                mc.setAttr("{0}.{1}".format(ctrl, k[0]), l = True )
                
            else:
                mc.addAttr(ctrl, longName=k[0], defaultValue=k[1] , k=1)
    #----------------------------------------------------------------------
    def connectLowEye(self, eyeCtrl, eyeDrv, upperJnt, lowJnt, name):
        """"""
        plusMinusAverages =  []
        multiplyDivides =  []
        clamps =  []
        for x in  xrange(5):
            pma =  mc.createNode("plusMinusAverage", n="plusMinusA{0}eyeLow_{1}".format(x, name))
            mc.setAttr("{0}.operation".format(pma), 1)
            plusMinusAverages.append(pma)
        for x in  xrange(6):
            mult =  mc.createNode("multiplyDivide", n = "multiplyDv{0}eyelow{1}".format(x, name))
            mc.setAttr("{0}.operation".format(mult), 1)
            multiplyDivides.append(mult)
        for x in  xrange(3):
            clamp =  mc.createNode("clamp", n="clamp{0}eyeLow{1}".format(x, name))
            clamps.append(clamp)        
        
        # lowJnt rx
        mc.connectAttr("{0}.rx".format(eyeCtrl), "{0}.input1D[0]".format(plusMinusAverages[0]), f=True)
        mc.connectAttr("{0}.rx".format(eyeDrv), "{0}.input1D[1]".format(plusMinusAverages[0]), f=True)        
        mc.connectAttr("{0}.output1D".format(plusMinusAverages[0]), "{0}.input1X".format(multiplyDivides[0]), f=True)
        
        mc.connectAttr("{0}.rx".format(eyeCtrl), "{0}.input1D[0]".format(plusMinusAverages[1]), f=True)
        mc.connectAttr("{0}.rx".format(eyeDrv), "{0}.input1D[1]".format(plusMinusAverages[1]), f=True)
        mc.connectAttr("{0}.output1D".format(plusMinusAverages[1]), "{0}.input1X".format(multiplyDivides[1]), f=True)
        mc.connectAttr("{0}.outputX".format(multiplyDivides[1]), "{0}.inputR".format(clamps[0]), f=True)
        
        mc.connectAttr("{0}.outputX".format(multiplyDivides[0]), "{0}.input1D[0]".format(plusMinusAverages[2]), f=True)
        mc.connectAttr("{0}.outputR".format(clamps[0]), "{0}.input1D[1]".format(plusMinusAverages[2]), f=True)
        
        mc.connectAttr("{0}.output1D".format(plusMinusAverages[2]),"{0}.inputR".format(clamps[1]), f=True)
        mc.connectAttr("{0}.lwrlip_dn_limit".format(eyeCtrl), "{0}.minR".format(clamps[1]), f=True)
        mc.connectAttr("{0}.lwrlip_up_limit".format(eyeCtrl),  "{0}.maxR".format(clamps[1]), f=True)
        
        mc.connectAttr("{0}.eyeLowerY".format(eyeCtrl),  "{0}.inputR".format(clamps[2]), f=True)
        mc.connectAttr("{0}.eyeLowerY".format(eyeCtrl),  "{0}.input1X".format(multiplyDivides[2]), f=True)
        mc.connectAttr("{0}.lwrlip_ty_radio".format(eyeCtrl), "{0}.input2X".format(multiplyDivides[2]), f=True)  #add
        
        md =  mc.createNode("multiplyDivide", n = "multiplyDv{0}eyelow{1}".format('_RX_', name))
        contion =  mc.createNode("condition", n = 'eyelow{0}RX_cond'.format(name))
        mc.connectAttr("{0}.outputR".format(clamps[2]),  "{0}.input1X".format(md), f=True)
        mc.connectAttr("{0}.lwrlip_tyDn_radio".format(eyeCtrl), "{0}.input2X".format(md), f=True)
        mc.connectAttr("{0}.outputX".format(md), "{0}.colorIfFalseR".format(contion), f=True)
        mc.connectAttr("{0}.outputX".format(multiplyDivides[2]), "{0}.colorIfTrueR".format(contion), f=True)
        mc.connectAttr("{0}.eyeLowerY".format(eyeCtrl), "{0}.firstTerm".format(contion), f=True)
        #mc.connectAttr("{0}.outColeR".format(contion), "{0}.firstTerm".format(contion), f=True)
        mc.setAttr("{0}.operation".format(contion), 5)
        
        mc.connectAttr("{0}.outColorR".format(contion), "{0}.input1D[1]".format(plusMinusAverages[3]), f=True)
        mc.connectAttr("{0}.outputR".format(clamps[1]), "{0}.input1D[0]".format(plusMinusAverages[3]), f=True)
        
        mc.connectAttr("{0}.output1D".format(plusMinusAverages[3]),"{0}.rx".format(lowJnt), f=True)
        
        # lowJnt ry
        mc.connectAttr("{0}.ry".format(eyeCtrl), "{0}.input1D[0]".format(plusMinusAverages[4]), f=True)
        mc.connectAttr("{0}.ry".format(eyeDrv), "{0}.input1D[1]".format(plusMinusAverages[4]), f=True)        
        mc.connectAttr("{0}.output1D".format(plusMinusAverages[4]), "{0}.input1X".format(multiplyDivides[3]), f=True)
        
        mc.connectAttr("{0}.lwrlip_ry_radio".format(eyeCtrl),  "{0}.input2X".format(multiplyDivides[3]), f=True)
        
        mc.connectAttr("{0}.outputX".format(multiplyDivides[3]), "{0}.ry".format(lowJnt), f=True)
        
        # lowJnt rz
        mc.connectAttr("{0}.eyeLowerX".format(eyeCtrl), "{0}.input1X".format(multiplyDivides[4]), f=True)
        mc.connectAttr("{0}.lwrlip_rz_radio".format(eyeCtrl), "{0}.input2X".format(multiplyDivides[4]), f=True)
        
        mc.connectAttr("{0}.outputX".format(multiplyDivides[4]), "{0}.rz".format(lowJnt), f=True)
        
        #speed

        mc.connectAttr("{0}.speed".format(eyeCtrl), "{0}.input2X".format(multiplyDivides[0]) , f =True)
        
        #setAttr
        #mc.setAttr("{0}.input2X".format(multiplyDivides[0]), 0.3)
        mc.setAttr("{0}.input2X".format(multiplyDivides[1]), 0.5)
        mc.setAttr("{0}.maxR".format(clamps[0]), 50)
        mc.setAttr("{0}.minR".format(clamps[2]), -0.250)
        mc.setAttr("{0}.maxR".format(clamps[2]), 0.700)
        
        
        
    #----------------------------------------------------------------------
    def connectUpperEye(self, eyeCtrl, eyeDrv, upperJnt, lowJnt, name):
        """"""
        plusMinusAverages =  []
        multiplyDivides =  []
        clamps =  []
        for x in  xrange(4):
            pma =  mc.createNode("plusMinusAverage", n="plusMinusA{0}eyeUpper{1}".format(x, name))
            mc.setAttr("{0}.operation".format(pma), 1)
            plusMinusAverages.append(pma)
        for x in  xrange(5):
            mult =  mc.createNode("multiplyDivide", n = "multiplyDv{0}eyeUpper{1}".format(x, name))
            mc.setAttr("{0}.operation".format(mult), 1)
            multiplyDivides.append(mult)
        for x in  xrange(2):
            clamp =  mc.createNode("clamp", n="clamp{0}eyeUpper{1}".format(x, name))
            clamps.append(clamp)
        # aimLock
        constr =  mc.listRelatives(eyeDrv, c=True,typ="constraint")[0]
        attr =  mc.aimConstraint(constr,q=1,wal=1)[0]
        mc.connectAttr("{0}.aimLock".format(eyeCtrl), "{0}.{1}".format(constr, attr) , f=True)
        
        # upperJnt rx
        mc.connectAttr("{0}.rx".format(lowJnt), "{0}.input1D[0]".format(plusMinusAverages[0]), f=True)
        mc.connectAttr("{0}.uprlip_up_limit".format(eyeCtrl), "{0}.input1D[1]".format(plusMinusAverages[0]), f=True)  #add
        
        mc.connectAttr("{0}.rx".format(eyeCtrl), "{0}.input1D[0]".format(plusMinusAverages[1]), f=True)
        mc.connectAttr("{0}.rx".format(eyeDrv), "{0}.input1D[1]".format(plusMinusAverages[1]), f=True)
        
        mc.connectAttr("{0}.output1D".format(plusMinusAverages[0]), "{0}.maxR".format(clamps[0]), f=True)
        mc.connectAttr("{0}.output1D".format(plusMinusAverages[1]), "{0}.inputR".format(clamps[0]), f=True)
        
        mc.connectAttr("{0}.uprlip_dn_limit".format(eyeCtrl), "{0}.minR".format(clamps[0]), f=True)
        mc.connectAttr("{0}.outputR".format(clamps[0]), "{0}.input1X".format(multiplyDivides[0]), f=True)
        
        
        mc.connectAttr("{0}.eyeUpperY".format(eyeCtrl), "{0}.inputR".format(clamps[1]), f=True)
        mc.connectAttr("{0}.outputR".format(clamps[1]), "{0}.input1X".format(multiplyDivides[1]), f=True)
        mc.connectAttr("{0}.uprlip_ty_radio".format(eyeCtrl), "{0}.input2X".format(multiplyDivides[1]), f=True)
        
        #mc.connectAttr("{0}.outputX".format(multiplyDivides[1]), "{0}.input1X".format(multiplyDivides[2]), f=True)
        
        multiplyD =  mc.createNode("multiplyDivide", n = "multiplyDv{0}eyeUpper{1}".format('_con_', name))
        multiplyD1 =  mc.createNode("multiplyDivide", n = "multiplyDv{0}eyeUpper{1}".format('_con_', name))
        mc.setAttr("{0}.input2X".format(multiplyD1), -1)
        condition =  mc.createNode("condition", n = "condition{0}eyeUpper{1}".format('_condition_', name))
        mc.setAttr("{0}.operation".format(condition), 5)
        
        mc.connectAttr("{0}.uprlip_tyUp_radio".format(eyeCtrl), "{0}.input2X".format(multiplyD), f=True)
        mc.connectAttr("{0}.outputR".format(clamps[1]), "{0}.input1X".format(multiplyD), f=True)
        mc.connectAttr("{0}.outputX".format(multiplyD), "{0}.input1X".format(multiplyD1), f=True)
        
        mc.connectAttr("{0}.eyeUpperY".format(eyeCtrl), "{0}.firstTerm".format(condition), f = True)
        mc.connectAttr("{0}.outputX".format(multiplyD1), "{0}.colorIfFalseR".format(condition), f=True)
        mc.connectAttr("{0}.outputX".format(multiplyDivides[1]), "{0}.colorIfTrueR".format(condition), f=True)
        mc.connectAttr("{0}.outColorR".format(condition), "{0}.input1X".format(multiplyDivides[2]), f=True)
        
        
        
        mc.connectAttr("{0}.outputX".format(multiplyDivides[2]), "{0}.input1D[1]".format(plusMinusAverages[2]), f=True)
        mc.connectAttr("{0}.outputX".format(multiplyDivides[0]), "{0}.input1D[0]".format(plusMinusAverages[2]), f=True)
        mc.connectAttr("{0}.output1D".format(plusMinusAverages[2]), "{0}.rx".format(upperJnt), f=True)
        
        # upperJnt ry
        mc.connectAttr("{0}.ry".format(eyeCtrl), "{0}.input1D[0]".format(plusMinusAverages[3]), f=True)
        mc.connectAttr("{0}.ry".format(eyeDrv), "{0}.input1D[1]".format(plusMinusAverages[3]), f=True)
        
        mc.connectAttr("{0}.output1D".format(plusMinusAverages[3]), "{0}.input1X".format(multiplyDivides[3]), f=True)
        mc.connectAttr("{0}.uprlip_ry_radio".format(eyeCtrl), "{0}.input2X".format(multiplyDivides[3]), f=True)
        
        mc.connectAttr("{0}.outputX".format(multiplyDivides[3]), "{0}.ry".format(upperJnt), f=True)
        
        # upperJnt rz
        mc.connectAttr("{0}.uprlip_rz_radio".format(eyeCtrl), "{0}.input2X".format(multiplyDivides[4]), f=True)
        mc.connectAttr("{0}.eyeUpperX".format(eyeCtrl), "{0}.input1X".format(multiplyDivides[4]), f=True)
        
        mc.connectAttr("{0}.outputX".format(multiplyDivides[4]), "{0}.rz".format(upperJnt), f=True)
        
        #setAttr
        mc.setAttr("{0}.minR".format(clamps[1]), -1)
        mc.setAttr("{0}.maxR".format(clamps[1]), 0.7)
        
        
        #speed
        plusA =  mc.createNode("plusMinusAverage", n = name + "_speed")
        mc.connectAttr("{0}.speed".format(eyeCtrl), "{0}.input1D[0]".format(plusA) , f = True)
        mc.setAttr("{0}.input1D[1]".format(plusA), 0.15)
        #mc.setAttr("{0}.input2X".format(multiplyDivides[0]), 0.8)
        mc.connectAttr("{0}.output1D".format(plusA), "{0}.input2X".format(multiplyDivides[0]) , f =True)
        
        
        

    #----------------------------------------------------------------------
    def mirr(self, mirror="L", *args):
        """"""
        if mirror == "L" or  mirror == "l":
            pos =  mc.xform(self.locatorList[0], q=True, ws=True, t=True)
            mc.xform(self.locatorList[1], ws=True, t=[pos[0]*-1, pos[1], pos[2]])
            
            ro = mc.xform(self.locatorList[0], q=True, ws=True, ro=True)
            mc.xform(self.locatorList[1], ws=True, ro=[ro[0], ro[1]*-1, ro[2]*-1])
            
            mc.setAttr(self.locatorList[1]+'.length', mc.getAttr(self.locatorList[0] + '.length'))
    
            x =  mc.xform('%s_aim' % self.locatorList[0], q=1, ws=1, t=1)
            print x
            mc.xform('%s_aim' % self.locatorList[1], ws=True, t=[x[0]*-1, x[1], x[2]])            
            #sys.stdout.write("Mirror L")
        if mirror == "R" or  mirror == "r":
            pos =  mc.xform(self.locatorList[1], q=True, ws=True, t=True)
            mc.xform(self.locatorList[0], ws=True, t=[-1*pos[0], pos[1], pos[2]])
            ro = mc.xform(self.locatorList[1], q=True, ws=True, ro=True)
            mc.xform(self.locatorList[0], ws=True, ro=[ro[0], ro[1]*-1, ro[2]*-1])
            mc.setAttr(self.locatorList[0]+'.length', mc.getAttr(self.locatorList[1] + '.length'))
    
            x =  mc.xform('%s_aim' % self.locatorList[1], q=1, ws=1, t=1)
            mc.xform('%s_aim' % self.locatorList[0], ws=True, t=[x[0]*-1, x[1], x[2]])
    
            #sys.stdout.write("Mirror R")

    #----------------------------------------------------------------------
    def all(self, *args):
        """"""
        mc.undoInfo(openChunk=True)
        for name in  self.locatorList:
            mc.delete(mc.listRelatives(name, c=True, type='constraint'))
            for x in ['x', 'y', 'z']:
                mc.setAttr('%s.r%s' % (name, x), k=True, ch=True, l=False)            
            ctrl , aimCtrl =  self.createCvCtrl(name.replace("Loc", "ctrl"))
            mc.setAttr(name+'.v', 0)
            #print name
            pos =  mc.xform(name, q=True, ws=True, t=True)
            rotate =  mc.xform(name, q=True, ws=True, ro=True)
            #
            drv =  mc.group(ctrl, n="{0}_drv".format(name.replace("Loc", "ctrl")))
            mc.xform(drv,os=1,piv= [0, 0, 0])
            zero =  mc.group(drv, n="{0}_zero".format(name.replace("Loc", "ctrl")))
            mc.xform(zero,os=1,piv= [0, 0, 0])
            
            mc.select(name.replace('Loc', 'Loc_aim'), r=True)
           # mc.select(ctrl, r=True)
            pupilla =  mc.joint(n=name.replace('Loc', 'pupilla'))
            mc.parent(pupilla,w=True)
            #mc.parent(pupilla, ctrl)
            mc.setAttr('%s.r' % pupilla, 0, 0, 0)
            mc.setAttr('%s.jo' % pupilla, 0, 0, 0)
            #mc.delete(mc.listRelatives(name.replace('Loc', 'Loc_aim'),p=True)[0])
            #mc.setAttr(pupilla + '.tz', 0.5)
          
            
            #aim
            aimzero =  mc.group(aimCtrl, n = "{0}_zero".format(name.replace("Loc", "aim")))
            mc.xform(aimzero,os=1,piv= [0, 0, 0])
            z =  mc.getAttr("{0}.boundingBoxMax".format(zero))[0][2]
            z1 =  mc.getAttr("{0}.boundingBoxMax".format(aimCtrl))[0][2]
            
            mc.xform(aimzero, ws=True, t=(pos[0], pos[1], z+z1))
            mc.parent(aimzero, zero)
            for x in  ['tx', 'ty', 'rx', 'ry', 'rz']:
                mc.setAttr(aimzero+"."+x, 0)
            mc.xform(zero, ws=True, t=pos)
            mc.xform(zero, ws=True, ro=rotate)            
            mc.parent(aimzero, w=True)
            
            
            #up aim
            aimUpLocator =  mc.spaceLocator(n="{0}_up_obj".format(name.replace("Loc", "aim")))[0]
            mc.move(pos[0], pos[1]+3, pos[2], aimUpLocator)
            #constraint
            
            mc.parentConstraint(aimCtrl, aimUpLocator, w=1, mo=True)
            #aimConstraint -offset 0 0 0 -weight 1 -aimVector 0 0 1 -upVector 0 1 0 -worldUpType "object" -worldUpObject locator1_aim_up_obj;

            mc.aimConstraint(aimCtrl, drv ,  aimVector = [0, 0, 1], upVector= [0, 1, 0], worldUpObject = aimUpLocator , mo=True, w=1, worldUpType = 'objectrotation')
            
            #eyeLip joint
            mc.select(cl=True)
            upperlip =  mc.joint(n="{0}_jnt".format(name.replace("Loc", "upperlip")), p=[0, 0, 0])
            upperlipGrp =  mc.group(upperlip, name = upperlip + "_zero")
            mc.xform(upperlipGrp,os=1,piv= [0, 0, 0])
            
            mc.xform(upperlipGrp, ws=True, t=pos)
            mc.xform(upperlipGrp, ws=True, ro=rotate)
            
            mc.select(cl=True)
            lowlip =  mc.joint(n="{0}_jnt".format(name.replace("Loc", "lowlip")), p=[0, 0, 0])
            lowlipGrp =  mc.group(lowlip, name = lowlip + "_zero")
            mc.xform(lowlipGrp,os=1,piv= [0, 0, 0])
            mc.xform(lowlipGrp, ws=True, t=pos)
            mc.xform(lowlipGrp, ws=True, ro=rotate)            
            
            #parent
            if mc.objExists(self.eyelipRigGrp):
                mc.parent(upperlipGrp, lowlipGrp, self.eyelipRigGrp)
            else:
                #mc.group(em=1, n=self.eyelipRigGrp)
                mc.group(upperlipGrp, lowlipGrp, n = self.eyelipRigGrp)
            
            if mc.objExists(self.aimUpObjGrp):
                mc.parent(aimUpLocator, self.aimUpObjGrp)
                for a in self.eyeLocatorAim:
                    p = mc.listRelatives(a, p = True)[0]
                    mc.parent(p, self.aimUpObjGrp)
            else:
                self.aimUpObjGrp =  mc.group(aimUpLocator, n=self.aimUpObjGrp)
            
            #parent loc
            mc.parent(name, ctrl)
            mc.parent(pupilla, ctrl)
            self.aimlist.append(aimzero)
            self.ctrlList.append(zero)
            
            
            self.addAttributes(ctrl)
            self.connectUpperEye(ctrl, drv, upperlip, lowlip, name)
            self.connectLowEye(ctrl, drv, upperlip, lowlip, name)
        
        self.eyeAim = mc.group(n = "eyeAim", em=True, w=True)
        mc.xform(self.eyeAim,os=1,piv= [0, 0, 0])
        self.eyeAim_zero =  mc.group(self.eyeAim , n = self.eyeAim_zero)
        mc.delete(mc.parentConstraint(self.aimlist, self.eyeAim_zero, mo=False, w=1))
        
        #
        self.eyeCtrlGrp =  mc.group(n=self.eyeCtrlGrp, em=True, w=True)
        self.eyeRigGrp =  mc.group(self.eyeCtrlGrp, n=self.eyeRigGrp)
        
        mc.delete(mc.parentConstraint(self.ctrlList, self.eyeRigGrp, mo=False, w=1))
        
        
        #
        mc.parent(self.aimlist,  self.eyeAim)
        mc.parent(self.eyeAim_zero, self.ctrlList,self.eyeCtrlGrp)
        mc.parent(self.eyelipRigGrp, self.aimUpObjGrp,self.eyeRigGrp)
        
        min = mc.getAttr("{0}.boundingBoxMin".format(self.eyeAim))[0]
        max = mc.getAttr("{0}.boundingBoxMax".format(self.eyeAim))[0]
        cv =  mc.curve(n="_cv", d = 1, p = [(min[0],min[1],0), (min[0],max[1],0), (max[0],max[1],0),(max[0],min[1],0),(min[0],min[1],0)], k = [0, 1, 2, 3, 4])        
        mc.parent(mc.listRelatives(cv, s=True, c=True)[0],self.eyeAim, s=True, r=True)
        mc.rename(mc.listRelatives(self.eyeAim, s=True, c=True)[0], self.eyeAim+"Shape")
        mc.delete(cv)
        for  x in  self.lockAttr:
            if x != 'v':
                mc.setAttr("{0}.{1}".format(self.aimUpObjGrp, x), lock=True, k=False)
            else:
                mc.setAttr("{0}.{1}".format(self.aimUpObjGrp, x), 0)
                mc.setAttr("{0}.{1}".format(self.aimUpObjGrp, x), lock=True, k=False)
        
        mc.undoInfo(closeChunk=True)
    #----------------------------------------------------------------------
    def reset(self, *args):
        """"""
        for x in self.locatorListRestParent:
            if x[1] != None :
                mc.parent(x[0], x[1])
            else:
                mc.parent(x[0], w=True)
        for a, l in zip(self.eyeLocatorAim, self.locatorListRestParent):
            mc.parent(mc.listRelatives(a, p = True)[0], w = True)
            mc.aimConstraint(a, l[0], offset = (0, 0, 0), aimVector = (0, 0, 1), worldUpType='vector', worldUpVector=(0, 1, 0), w=1)
            mc.setAttr(l[0] + '.v', 1)
        mc.delete(self.eyeRigGrp)
    #----------------------------------------------------------------------
    def setLoactor(self, locatorList):
        """"""
        self.locatorList =  locatorList
        self.locatorListRestParent = []
        for locator in  locatorList:
            parnet  =  mc.listRelatives(locator, p=True, f=True)
            self.locatorListRestParent.append((locator, parnet))
        
        return self.locatorList
        
########################################################################
class eyeRigUI(object):
    """"""
    __metaclass__=type 
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.uiName =  "eyeRigUi"
        self.eye = eyeRig()
        #super(eyeRig , self).__init__()
    #----------------------------------------------------------------------
    def createUi(self):
        """"""
        self.deleteUI()
        self.window = mc.window(self.uiName, w=200, h = 70, title = self.uiName+__version__, backgroundColor = (0.5, 1, 0.5))
        self.mainLayout = mc.columnLayout("mainLayout", adj = True)
        self.CreateButton = mc.button(l = "CreateLocator", c = partial(self.eye.createLocator))
        #self.RMirrButton = mc.button(l = "EyeMirr", c = partial(self.eye.mirr, "L"))
        self.RigEyeButton = mc.button(l = "EyeRigging", c = partial(self.eye.all))
        self.deleteButton = mc.button(l = "DeleteEyeRigging" , c = partial(self.eye.reset))
        self.createScriptJob()
        pass
    #----------------------------------------------------------------------
    def createScriptJob(self):
        """"""
        self.scriptJob = mc.scriptJob(p = self.window, e = ["DragRelease",  self.ScriptJobCommand])
    #----------------------------------------------------------------------
    def deleteUI(self):
        """"""
        if mc.window(self.uiName, ex=True):
            mc.deleteUI(self.uiName)
        if mc.windowPref(self.uiName, ex = True):
            mc.windowPref(self.uiName, r = True)
        pass
    #----------------------------------------------------------------------
    def show(self):
        """"""
        self.createUi()
        mc.showWindow(self.window)
    #----------------------------------------------------------------------
    def ScriptJobCommand(self, *args):
        """"""
        sel = mc.ls(sl = True)
        if sel :
            if "eye_L_Loc"in sel or 'eye_L_Loc_aim' in sel:
                self.eye.mirr("L")
                #sys.stdout.write("True")
            elif "eye_R_Loc" in sel or 'eye_R_Loc_aim' in sel:
                self.eye.mirr("R")
        else:
            pass
            #sys.stdout.write("False")
if __name__ == "__main__":
    win = eyeRigUI()
    win.show()
    
