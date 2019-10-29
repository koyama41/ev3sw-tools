#! /usr/bin/python3

import xml.etree.ElementTree as ET
import sys
import re
import argparse

global args

def updateDict(dictname, dict, key, value, printWarning=False):
    if key == None:
        if printWarning:
            print("Warning: " + dictname + ": key is None, value is " + str(value))
    elif key in dict:
        if printWarning:
            print("Warning: " + dictname + ": " + key + " is already in dict: " + value + " is ignored")
    else:
        dict[key] = value

def gettag(node):
    tag = node.tag
    return re.sub('\{[^}]*\} *', '', tag) 

def getId(node, parenttag=""):
    tag = gettag(node)
    if '.' in tag and (tag.split('.'))[0] == parenttag:
        for child in node:
            return getId(child)
    if "Id" in node.attrib:
        return node.attrib["Id"]
    return None

def getSequenceIn(node, parenttag=""):
    tag = gettag(node)
    if '.' in tag and (tag.split('.'))[0] == parenttag:
        for child in node:
            return getSequenceIn(child)
    for child in node:
        if gettag(child) == "Terminal" and child.attrib["Direction"] == "Input" and "Wire" in child.attrib:
            return child.attrib["Wire"]
    return None

def getSequenceOut(node, parenttag=""):
    tag = gettag(node)
    if '.' in tag and (tag.split('.'))[0] == parenttag:
        for child in node:
            return getSequenceOut(child)
    for child in node:
        if gettag(child) == "Terminal" and child.attrib["Direction"] == "Output" and "Wire" in child.attrib:
            return child.attrib["Wire"]
    return None

def printxml(indent, node):
    print(indent + gettag(node), node.attrib)
    for child in node:
        printxml(indent + "  ", child)

#def printnode(indent, node):
#    if "Id" in node.attrib:
#        del node.attrib["Id"]
#    if "Bounds" in node.attrib:
#        del node.attrib["Bounds"]
#    print(indent + gettag(node), node.attrib)
#    for child in node:
#        if gettag(child) == "Terminal" and (child.attrib["Id"] == "SequenceIn" or child.attrib["Id"] == "SequenceOut"):
#            continue
#        if gettag(child) == "ConfigurableMethodTerminal":
#            for grandchild in child:
#                print(indent + "  " + gettag(grandchild), grandchild.attrib)
#            continue
#        printxml(indent + "  ", child)
                    
#def printSequence(indent, node):
#    while True:
#        printnode(indent, node)
#        wire = getSequenceOut(node)
#        if wire != None and wire in seqInWire2id:
#            nodeid = seqInWire2id[wire]
#            if nodeid in id2node:
#                node = id2node[nodeid]
#                continue
#            else:
#                pass
#                #print("#DEBUG else2#: nodeid=" + nodeid)
#        else:
#            pass
#            #print("#DEBUG else1#: wire=" + str(wire))
#        break

def processConfigurableMethodTerminal(node, indent=""):
    i = None
    d = None
    t = None
    w = None
    for child in node:
        if gettag(child) == "Terminal":
            i = child.attrib["Id"]
            d = child.attrib["Direction"]
            t = child.attrib["DataType"]
            if "Wire" in child.attrib:
                w = child.attrib["Wire"]

    if i == "InterruptsToListenFor_16B03592_CD76_4D58_8DC3_E3C3091E327A" and d == "Input" and t == "Int32":
        pass
    else:
        if w == None:
            if "ConfiguredValue" in node.attrib:
                print(indent + i + "." + d + " :: " + t + " = " + node.attrib["ConfiguredValue"])
            else:
                print(indent + i + "." + d + " :: " + t + " = None")
        else:
            if "ConfiguredValue" in node.attrib:
                print(indent + i + "." + d + " :: " + t + " = Wire(" + w + "," + node.attrib["ConfiguredValue"] + ")")
            else:
                print(indent + i + "." + d + " :: " + t + " = Wire(" + w + ")")

def processConfigurableMethodTerminalNoIndent(comma, node):
    i = None
    d = None
    t = None
    w = None
    for child in node:
        if gettag(child) == "Terminal":
            i = child.attrib["Id"]
            d = child.attrib["Direction"]
            t = child.attrib["DataType"]
            if "Wire" in child.attrib:
                w = child.attrib["Wire"]

    if i == "InterruptsToListenFor_16B03592_CD76_4D58_8DC3_E3C3091E327A" and d == "Input" and t == "Int32":
        return False
    print(comma, end="")

    if d == "Output":
        print("out=", end="")
    if i == "Degrees":
        print("deg=", end="")
    if i == "Brake\\ At\\ End":
        print("brake=", end="")
    if w == None:
        if "ConfiguredValue" in node.attrib:
            print(node.attrib["ConfiguredValue"], end="")
        else:
            print("None", end="")
    else:
        if "ConfiguredValue" in node.attrib:
            print("Wire(" + w + "," + node.attrib["ConfiguredValue"] + ")", end="")
        else:
            print("Wire(" + w + ")", end="")
    return True

def processMethodCall(node, indent="", name="Call"):
    if args.verbose:
        print(indent + name + "(" + node.attrib["Target"] + ")")
        for child in node:
            if gettag(child) == "ConfigurableMethodTerminal":
                processConfigurableMethodTerminal(child, indent + "  ")
            elif gettag(child) == "Terminal":
                pass
            else:
                processNode(child, indent + "  ##")
    else:
        target = name + "_" + node.attrib["Target"]
        print(indent + re.sub('\\\..*$', '', target) + "(", end="")
        comma = ""
        for child in node:
            if gettag(child) == "ConfigurableMethodTerminal":
                if processConfigurableMethodTerminalNoIndent(comma, child):
                    comma = ", "
        print(")")
        for child in node:
            if     (gettag(child) != "ConfigurableMethodTerminal"
                    and gettag(child) != "Terminal"):
                processNode(child, indent + "  ##")

def processConfigurableWaitFor(node, indent=""):
    processMethodCall(node, indent, "WaitFor")

def processConfigurableMethodCall(node, indent=""):
    processMethodCall(node, indent, "MethodCall")

def processPairedConfigurableMethodCall(node, indent=""):
    processMethodCall(node, indent, "PairedMethodCall")
    return node.attrib["PairedStructure"]

def processStartBlock(node, indent=""):
    if args.verbose:
        print(indent + "StartBlock")

def processCompoundStmt(node, indent="", startBlock=None):
    if len(node) == 1:
        for child in node:
            processNode(child, indent)
        return

    id2node = {}
    seqInWire2id = {}
    id2seqOutWire = {}
    tag = gettag(node)
    alreadyprinted = {}
    debuglist = []
    for child in node:
        nodeid = getId(child, tag)
        seqin = getSequenceIn(child, tag)
        seqout = getSequenceOut(child, tag)
        debuglist += (nodeid, seqin, seqout)

        updateDict("id2node", id2node, nodeid, child, True)
        updateDict("seqInWire2id", seqInWire2id, seqin, nodeid)
        updateDict("id2seqOutWire", id2seqOutWire, nodeid, seqout)
        if gettag(child) == "StartBlock":
            startBlock = child

#    print(indent + "##DEBUG:", debuglist)

    for child in node:
        childtag = gettag(child)
        if childtag == "ConfigurableWhileLoop.ConfigurableLoopTunnel":
            alreadyprinted[getId(child)] = True
            print(indent + "LoopTunnel("  + child.attrib["AutoIndex"] + ", " + child.attrib["Id"] + ", " + child.attrib["Terminals"] + ")")
        elif childtag == "ConfigurableMegaAccessor" and child.attrib["AccessorType"] == "Input":
            alreadyprinted[getId(child)] = True
            processMethodCall(child, indent, "MegaAccessor")

    if startBlock != None:
        walknode = startBlock
        while True:
            alreadyprinted[getId(walknode)] = True
            pairednodeid = processNode(walknode, indent)
            wire = getSequenceOut(walknode, tag)
            if pairednodeid != None:
                alreadyprinted[pairednodeid] = True
                pairednode = id2node[pairednodeid]
                processNode(pairednode, indent)
                wire = getSequenceOut(pairednode, tag)
            if wire != None and wire in seqInWire2id:
                nodeid = seqInWire2id[wire]
                if nodeid in id2node:
                    walknode = id2node[nodeid]
                    continue
                else:
                    pass
                #print("#DEBUG else2#: nodeid=" + nodeid)
            else:
                pass
            #print("#DEBUG else1#: wire=" + str(wire))
            break

    captionAlreadyPrinted = False
    for child in node:
        if getId(child) in alreadyprinted:
            pass
        else:
            if gettag(child) != "Wire" and gettag(child) != "Terminal":
                if captionAlreadyPrinted:
                    pass
                else:
                    print("")
                    print(indent + "###NOT CONNECTED###")
                    captionAlreadyPrinted = True
                printxml(indent + "##", child)
    if captionAlreadyPrinted:
        print("")

def processConfigurableWhileLoop(node, indent=""):
    print(indent + "WhileLoop(" + node.attrib["DiagramId"] + ", " + node.attrib["InterruptName"] + ")")
    startNode = None
    for child in node:
        if gettag(child) == "ConfigurableWhileLoop.BuiltInMethod":
            if child.attrib["CallType"] == "LoopIndex":
                startNode = child
    processCompoundStmt(node, indent + "  ", startNode)

def processConfigurableWhileLoop_BuiltInMethod(node, indent=""):
    print(indent + "WhileLoop.BuiltInMethod(" + node.attrib["CallType"] + ")")
    for child in node:
        processNode(child, indent + "  ")

def processConfigurableFlatCaseStructure(node, indent=""):
    print(indent + "FlatCaseStructure(" + node.attrib["DataType"] + ", " + node.attrib["Default"] + ")")
    for child in node:
        if gettag(child) != "Terminal":
            processNode(child, indent + "  ")

def processConfigurableFlatCaseStructure_Case(node, indent=""):
    print(indent + "Case(" + node.attrib["Id"] + ", " + node.attrib["Pattern"] + ")")
    startNode = None
    for child in node:
        #printxml(indent + "  ", child)
        if gettag(child) == "SequenceNode" and getSequenceOut(child) != None:
            startNode = child
    processCompoundStmt(node, indent + "  ", startNode)

def processConfigurableCaseStructure(node, indent=""):
    print(indent + "CaseStructure(" + node.attrib["DataType"] + ", " + node.attrib["Default"] + ")")
    for child in node:
        if gettag(child) != "Terminal":
            processNode(child, indent + "  ")

def processConfigurableCaseStructure_Case(node, indent=""):
    print(indent + "Case(" + node.attrib["Id"] + ", " + node.attrib["Pattern"] + ")")
    startNode = None
    for child in node:
        #printxml(indent + "  ", child)
        if gettag(child) == "SequenceNode" and getSequenceOut(child) != None:
            startNode = child
    processCompoundStmt(node, indent + "  ", startNode)

def processSequenceNode(node, indent=""):
    #print(indent + "SequenceNode(" + node.attrib["Id"] + ")")
    pass

def processBlockDiagram(node, indent=""):
    processCompoundStmt(node, indent)

def processVirtualInstrument(node, indent=""):
    for child in node:
        if gettag(child) == "BlockDiagram":
            processBlockDiagram(child, indent)
        else:
            pass

def processNamespace(node, indent=""):
    for child in node:
        processNode(child, indent)

def processSourceFile(node, indent=""):
    for child in node:
        processNode(child, indent)

def processUnknownNode(node, indent=""):
    print(indent + "##processUnknownNode##")
    printxml(indent + "##", node)

def processNode(node, indent=""):
    funcname = "process" + re.sub('\.', '_', gettag(node))
    gf = globals()
    if funcname in gf:
        func = gf[funcname]
        return func(node, indent)
    else:
        return processUnknownNode(node, indent)


parser = argparse.ArgumentParser(description="analyze .ev3p file(s)")
parser.add_argument('inputfile', type=argparse.FileType("r"),
                    help='input file name')
parser.add_argument('-v', '--verbose',
                    action='store_true',
                    help='show verbose messages')
args = parser.parse_args()

if args.inputfile:
    processNode(ET.fromstring(args.inputfile.read()))
else:
    processNode(ET.fromstring(sys.stdin.read()))
