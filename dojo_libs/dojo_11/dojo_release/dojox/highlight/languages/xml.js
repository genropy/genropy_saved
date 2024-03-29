/*
	Copyright (c) 2004-2008, The Dojo Foundation
	All Rights Reserved.

	Licensed under the Academic Free License version 2.1 or above OR the
	modified BSD license. For more information on Dojo licensing, see:

		http://dojotoolkit.org/book/dojo-book-0-9/introduction/licensing
*/


if(!dojo._hasResource["dojox.highlight.languages.xml"]){dojo._hasResource["dojox.highlight.languages.xml"]=true;dojo.provide("dojox.highlight.languages.xml");dojo.require("dojox.highlight._base");(function(){var _1={className:"comment",begin:"<!--",end:"-->"};var _2={className:"attribute",begin:" [a-zA-Z-]+=",end:"^",contains:["value"]};var _3={className:"value",begin:"\"",end:"\""};var dh=dojox.highlight,_5=dh.constants;dh.languages.xml={defaultMode:{contains:["pi","comment","cdata","tag"]},case_insensitive:true,modes:[{className:"pi",begin:"<\\?",end:"\\?>",relevance:10},_1,{className:"cdata",begin:"<\\!\\[CDATA\\[",end:"\\]\\]>"},{className:"tag",begin:"</?",end:">",contains:["title","tag_internal"],relevance:1.5},{className:"title",begin:"[A-Za-z:_][A-Za-z0-9\\._:-]+",end:"^",relevance:0},{className:"tag_internal",begin:"^",endsWithParent:true,contains:["attribute"],relevance:0,illegal:"[\\+\\.]"},_2,_3],XML_COMMENT:_1,XML_ATTR:_2,XML_VALUE:_3};})();}