# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy core - see LICENSE for details
# module gnrbagxml : bag from/to xml methods
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import re, os
import datetime

from xml import sax
from xml.sax import saxutils

from gnr.core.gnrbag import Bag, BagNode, BagAsXml
from decimal import Decimal

from gnr.core import gnrstring
from gnr.core import gnrclasses
import time
REGEX_XML_ILLEGAL = re.compile(r'<|>|&')
ZERO_TIME=datetime.time(0,0)

def isValidValue(value):
    """A check method for the validity of a :class:`Bag <gnr.core.gnrbag.Bag>` value
    
    :param value: the value to be checked"""
    return value in (0,ZERO_TIME)
    
class _BagXmlException(Exception): pass

class BagFromXml(object):
    """The class that handles the conversion from the XML format to the
    :class:`Bag <gnr.core.gnrbag.Bag>` class"""
    def build(self, source, fromFile, catalog=None, bagcls=Bag, empty=None):
        """TODO
        
        :param source: TODO
        :param fromFile: TODO
        :param catalog: TODO
        :param bagcls: TODO
        :param empty: TODO"""
        if not bagcls: bagcls = Bag
        done = False
        testmode = False
        nerror = 0
        if isinstance(source, unicode):
            source = source.encode('utf8')
        while not done:
            try:
                result = self.do_build(source, fromFile, catalog=catalog, bagcls=bagcls, empty=empty, testmode=testmode)
                done = True
            except sax.SAXParseException:
                import sys

                l = sys.exc_info()
                if l[1].args[0] == 'not well-formed (invalid token)':
                    nerror = nerror + 1
                    linepos, colpos = (l[1]._locator.getLineNumber() - 1, l[1]._locator.getColumnNumber())
                    #print "xml error %i at line %i, col %i: trying to recover..." % (nerror, linepos, colpos)
                    if fromFile:
                        f = open(source, 'r')
                        source = f.read()
                        f.close()
                        fromFile = False
                    source = source.splitlines(True)
                    errline = source[linepos]
                    source[linepos] = errline[:colpos] + errline[colpos + 1:]
                    source = ''.join(source)
                    testmode = True
                else:
                    raise
                    #raise _BagXmlException(source, l[1].args[0])
        if testmode:
            result = self.do_build(source, fromFile, catalog=catalog, bagcls=bagcls, empty=empty)
        return result

    def do_build(self, source, fromFile, catalog=None, bagcls=Bag, empty=None, testmode=False):
        """TODO
        
        :param source: TODO
        :param fromFile: TODO
        :param catalog: TODO
        :param bagcls: TODO
        :param empty: TODO
        :param testmode: TODO"""
        if not testmode:
            bagImport = _SaxImporter()
        else:
            bagImport = sax.handler.ContentHandler()
        if not catalog:
            catalog = gnrclasses.GnrClassCatalog()
        bagImport.catalog = catalog
        bagImport.bagcls = bagcls
        bagImport.empty = empty
        bagImportError = _SaxImporterError()
        if fromFile:
            infile =  open(source)
            source = infile.read()
            infile.close()
                
        if isinstance(source, unicode):
            if source.startswith('<?xml'):
                source = source[source.index('?>'):]
            source = "<?xml version='1.0' encoding='UTF-8'?>%s" % source.encode('UTF-8')
        source = re.sub("&(?!([a-zA-Z][a-zA-Z0-9]*|#\d+);)", "&amp;", source)
        sax.parseString(source, bagImport)
        if not testmode:
            result = bagImport.bags[0][0]
            if bagImport.format == 'GenRoBag': result = result['GenRoBag']
            if result == None: result = []
            return result

class _SaxImporterError(sax.handler.ErrorHandler):
    def error(self, error):
        pass
        
    def fatalError(self, error):
        pass
        
    def warning(self, error):
        pass
        
class _SaxImporter(sax.handler.ContentHandler):
    def startDocument(self):
        self.bags = [[Bag(), None]]
        self.valueList = []
        self.format = ''
        self.currType = None
        self.currArray = None

    def getValue(self):
        if self.valueList:
            if self.valueList[0] == '\n': self.valueList[:] = self.valueList[1:]
            if self.valueList:
                if(self.valueList[-1] == '\n'): self.valueList.pop()
        return saxutils.unescape(''.join(self.valueList))

    def startElement(self, tagLabel, attributes):
        attributes = dict([(str(k), self.catalog.fromTypedText(saxutils.unescape(v))) for k, v in attributes.items()])
        if  len(self.bags) == 1:
            if tagLabel.lower() == 'genrobag': self.format = 'GenRoBag'
            else: self.format = 'xml'
            self.bags.append((self.bagcls(), attributes))
        else:
            if(self.format == 'GenRoBag'):
                self.currType = None
                if '_T' in attributes:
                    self.currType = attributes.pop('_T')
                elif 'T' in attributes:
                    self.currType = attributes.pop('T')
                if not self.currArray:
                    newitem = self.bagcls()
                    if self.currType:
                        if self.currType.startswith("A"):
                            self.currArray = tagLabel
                            newitem = []
                    self.bags.append((newitem, attributes))
            else:
                if ''.join(self.valueList).strip() != '':
                    value = self.getValue()
                    if value:
                        self.bags[-1][0].nodes.append(BagNode(self.bags[-1][0], '_', value))
                self.bags.append((self.bagcls(), attributes))
        self.valueList = []

    def characters(self, s):
        if s == '\n': self.valueList.append(s)
        #s=s.strip()
        if not self.valueList or self.valueList[-1] == '\n':
            s = s.lstrip()
        s = s.rstrip('\n')
        if s != '': self.valueList.append(s)

    def endElement(self, tagLabel):
        value = self.getValue()
        self.valueList = []
        dest = self.bags[-1][0]
        if (self.format == 'GenRoBag'):
            if value:
                if self.currType and self.currType != 'T':
                    try:
                        value = self.catalog.fromText(value, self.currType)
                    except:
                        import sys
                        #print sys.exc_info()[1]
                        #print value
                        value = None
        if self.currArray: #handles an array
            if self.currArray != tagLabel: # array's content
                if value == '':
                    if self.currType and self.currType != 'T':
                        value = self.catalog.fromText('', self.currType)
                dest.append(value)
            else: #array enclosure
                self.currArray = None
                curr, attributes = self.bags.pop()
                self.setIntoParentBag(tagLabel, curr, attributes)
        else:
            curr, attributes = self.bags.pop()
         
            if value or isValidValue(value):
                if curr:
                    curr.nodes.append(BagNode(curr, '_', value))
                else:
                    curr = value
            if not curr and not isValidValue(curr):
                if self.empty:
                    curr = self.empty()
                else:
                    curr = self.catalog.fromText('', self.currType)
            self.setIntoParentBag(tagLabel, curr, attributes)

    def setIntoParentBag(self, tagLabel, curr, attributes):
        dest = self.bags[-1][0]
        if '_tag'  in attributes: tagLabel = attributes.pop('_tag')
        if attributes:
            dest.nodes.append(BagNode(dest, tagLabel, curr, attributes, _removeNullAttributes=False))
        else:
            dest.nodes.append(BagNode(dest, tagLabel, curr))
            
class BagToXml(object):
    """The class that handles the conversion from the :class:`Bag <gnr.core.gnrbag.Bag>`
    class to the XML format"""
    def nodeToXmlBlock(self, node):
        """Handle all the different node types, call the method build tag. Return
        the XML tag that represent the BagNode
        
        :param node: the :meth:`BagNode <gnr.core.gnrbag.BagNode>`"""
        nodeattr = dict(node.attr)
        if '__forbidden__' in nodeattr:
            return ''
        if self.unresolved and node.resolver is not None and not getattr(node.resolver,'_xmlEager',None):
            if not nodeattr.get('_resolver_name'):
                nodeattr['_resolver'] = gnrstring.toJson(node.resolver.resolverSerialize())
            value = ''
            if isinstance(node._value, Bag):
                value = self.bagToXmlBlock(node._value)
            return self.buildTag(node.label, value, nodeattr, '', xmlMode=True)

        nodeValue = node.getValue()
        if isinstance(nodeValue, Bag) and nodeValue: #<---Add the second condition in order to type the empty bag.
            result = self.buildTag(node.label,
                                   self.bagToXmlBlock(nodeValue), nodeattr, '', xmlMode=True)

        elif isinstance(nodeValue, BagAsXml):
            result = self.buildTag(node.label, nodeValue, nodeattr, '', xmlMode=True)

        #elif ((isinstance(nodeValue, list) or isinstance(nodeValue, dict))):
        #    nodeValue = gnrstring.toJson(nodeValue)
        #    result = self.buildTag(node.label, nodeValue, node.attr)
        #elif nodeValue and (isinstance(nodeValue, list) or isinstance(nodeValue, tuple)):
        #    result = self.buildTag(node.label,
        #                           '\n'.join([self.buildTag('C', c) for c in nodeValue]),
        #                           node.attr, cls='A%s' % self.catalog.getClassKey(nodeValue[0]),
        #                           xmlMode=True)
        
        elif self.mode4d and (nodeValue and (isinstance(nodeValue, list) or isinstance(nodeValue, tuple))):
            if node.label[:3] in ('AR_','AL_','AT_','AD_','AH_','AB_'):
                cls4d = node.label[:2] # if variable name specify array type, use it
            else:
                cls4d = 'A%s' % self.catalog.getClassKey(nodeValue[0])
            result = self.buildTag(node.label,
                       '\n'.join([self.buildTag('C', c) for c in nodeValue]),
                       node.attr, cls=cls4d,
                       xmlMode=True)

        else:
            result = self.buildTag(node.label, nodeValue, node.attr)
        return result

    #-------------------- toXmlBlock --------------------------------
    def bagToXmlBlock(self, bag):
        """Return an XML block version of the Bag.
        
        The XML block version of the Bag uses XML attributes for an efficient representation of types:
        If the element-leaf is a simple string, there are no type attributes in the corresponding XML nodes 
        otherwise a 'T' attribute is set to the node and the value of 'T' changes in function of the type 
        (value of 'T' is 'B' for boolean, 'L' for integer, 'R' for float, 'D' for date, 'H' for time).
        
        >>> mybag=Bag()
        >>> mybag['aa.bb']=4567
        >>> mybag['aa.cc']='test'
        >>> mybag.toXmlBlock()
        ['<aa>', u'<cc>test</cc>', u'<bb T="L">4567</bb>', '</aa>']"""
        return '\n'.join([self.nodeToXmlBlock(node) for node in bag.nodes])
        
    #-------------------- toXml --------------------------------
    def build(self, bag, filename=None, encoding='UTF-8', catalog=None, typeattrs=True, typevalue=True,
              addBagTypeAttr=True,onBuildTag=None,
              unresolved=False, autocreate=False, docHeader=None, self_closed_tags=None,
              translate_cb=None, omitUnknownTypes=False, omitRoot=False, forcedTagAttr=None,mode4d=False,pretty=None):
        """Return a complete standard XML version of the Bag, including the encoding tag 
        ``<?xml version=\'1.0\' encoding=\'UTF-8\'?>``; the Bag's content is hierarchically represented 
        as an XML block sub-element of the ``<GenRoBag>`` node.
        
        Is also possible to write the result on a file, passing the path of the file as the ``filename`` parameter.
        
        :param bag: the Bag to transform in a XML block version
        :param filename: the path of the output file
        :param encoding: allow to set the XML encoding
        :param catalog: TODO
        :param typeattrs: TODO
        :param typevalue: TODO
        :param addBagTypeAttr: TODO
        :param onBuildTag: TODO
        :param unresolved: TODO
        :param autocreate: TODO
        :param docHeader: TODO
        :param self_closed_tags: TODO
        :param translate_cb: TODO
        :param omitUnknownTypes: TODO
        :param omitRoot: TODO
        :param forceTagAttr: TODO
        
        >>> mybag = Bag()
        >>> mybag['aa.bb'] = 4567
        >>> mybag.toXml()
        '<?xml version=\'1.0\' encoding=\'iso-8859-15\'?><GenRoBag><aa><bb T="L">4567</bb></aa></GenRoBag>'"""
        result = docHeader or "<?xml version='1.0' encoding='" + encoding + "'?>\n"
        if not catalog:
            catalog = gnrclasses.GnrClassCatalog()
        self.translate_cb = translate_cb
        self.omitUnknownTypes = omitUnknownTypes
        self.catalog = catalog
        self.typeattrs = typeattrs
        self.typevalue = typevalue
        self.self_closed_tags = self_closed_tags or []
        self.forcedTagAttr = forcedTagAttr
        self.addBagTypeAttr = addBagTypeAttr
        self.onBuildTag = onBuildTag
        self.mode4d = mode4d
        if not typeattrs:
            self.catalog.addSerializer("asText", bool, lambda b: 'y' * int(b))
            
        self.unresolved = unresolved
        if omitRoot:
            result = result + self.bagToXmlBlock(bag)
        else:
            result = result + self.buildTag('GenRoBag', self.bagToXmlBlock(bag), xmlMode=True)
        result = unicode(result).encode(encoding, 'replace')
        if pretty:
            from xml.dom.minidom import parseString
            result = parseString(result)
            result = result.toprettyxml()
            result = result.replace('\t\n','').replace('\t\n','')
        if filename:
            if autocreate:
                dirname = os.path.dirname(filename)
                if dirname and not os.path.exists(dirname):
                    os.makedirs(dirname)
            output = open(filename, 'w')
            output.write(result)
            output.close()
        return result
        
    def buildTag(self, tagName, value, attributes=None, cls='', xmlMode=False):
        """TODO Return the XML tag that represent self BagNode
        
        :param tagName: TODO
        :param value: TODO
        :param attributes: TODO
        :param cls: TODO
        :param xmlMode: TODO"""
        #if value == None:
        #    value = ''
        if self.onBuildTag:
            self.onBuildTag(label=tagName,value=value,attributes=attributes)
        t = cls
        if not t:
            if value != '':
                #if not isinstance(value, basestring):
                if isinstance(value, Bag):
                    if self.addBagTypeAttr:
                        value, t = '', 'BAG'
                    else:
                        value = ''
                elif isinstance(value, BagAsXml):
                    value = value.value
                else:
                    if self.mode4d and isinstance(value, Decimal):
                        value = float(value)
                    value, t = self.catalog.asTextAndType(value, translate_cb=self.translate_cb)
                if isinstance(value, BagAsXml):
                    print x
                try:
                    value = unicode(value)
                except Exception, e:
                    raise e
                    #raise '%s: %s' % (str(tagName), value)
        if attributes:
            attributes = dict(attributes)
            if self.forcedTagAttr and self.forcedTagAttr in attributes:
                tagName = attributes.pop(self.forcedTagAttr)
            if tagName == '__flatten__':
                return value
            if self.omitUnknownTypes:
                attributes = dict([(k, v) for k, v in attributes.items()
                                   if type(v) in (basestring, str, unicode, int, float, long,
                                                  datetime.date, datetime.time, datetime.datetime,
                                                  bool, type(None), list, tuple, dict, Decimal) or 
                                     (callable(v) and 
                                            (hasattr(v,'is_rpc') or 
                                            (hasattr(v,'__name__') and v.__name__.startswith('rpc_'))))
                                   ])
            else:
                attributes = dict([(k, v) for k, v in attributes.items()])
            if self.typeattrs:
                attributes = ' '.join(['%s=%s' % (
                lbl, saxutils.quoteattr(self.catalog.asTypedText(val, translate_cb=self.translate_cb,jsmode=True))) for lbl, val in
                                       attributes.items()])
            else:
                attributes = ' '.join(
                        ['%s=%s' % (lbl, saxutils.quoteattr(self.catalog.asText(val, translate_cb=self.translate_cb)))
                         for lbl, val in attributes.items() if val is not False])
        originalTag = tagName
        tagName = re.sub(r'[^\w:]', '_', originalTag).replace('__', '_')
        if tagName[0].isdigit(): tagName = '_' + tagName
        
        if tagName != originalTag:
            result = '<%s _tag=%s' % (tagName, saxutils.quoteattr(saxutils.escape(originalTag)))
        else:
            result = '<%s' % tagName;
            
        if self.typevalue and t != '' and t != 'T':
            result = '%s _T="%s"' % (result, t)
        if attributes: result = "%s %s" % (result, attributes)
        if isinstance(value, BagAsXml):
            print x
        if not xmlMode:
            if not isinstance(value, unicode): value = unicode(value, 'UTF-8')
            #if REGEX_XML_ILLEGAL.search(value): value='<![CDATA[%s]]>' % value
            #else: value = saxutils.escape((value))
            
            if value.endswith('::HTML'):
                value = value[:-6]
            elif REGEX_XML_ILLEGAL.search(value):
                value = saxutils.escape(value)
                
                #if REGEX_XML_ILLEGAL.search(value):
                #    if value.endswith('::HTML'):
                #        value = value[:-6]
                #    else:
                #        value = saxutils.escape(value)
                #elif value.endswith('::HTML'):
                #    value = value[:-6]
                #
            #if value.find('\n')!=-1: value= '\n%s\n' % value
        if not value and tagName in self.self_closed_tags:
            result = '%s/>' % result
        else:
            result = '%s>%s</%s>' % (result, value, tagName)

        return result