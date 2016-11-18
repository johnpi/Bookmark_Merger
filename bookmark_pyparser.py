"""
 Copyright 2009 Robert Steed
 
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

#Parses firefox bookmark.html files
#takes care to minimise changes to the file.
import pyparsing as pp
import types

#Possible headers  - had 200 bookmark files covering 4(?) years of files
headers=[
"""<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>""",

"""<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
It will be read and overwritten.
Do Not Edit! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>""",

"""<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
It will be read and overwritten.
Do Not Edit! -->
<TITLE>Bookmarks</TITLE>""",

"""<!DOCTYPE NETSCAPE-Bookmark-file-1>
<html><head><!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! --><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><title>Bookmarks</title></head>
"""]
#headers = [ pp.And( pp.Literal(line.strip()) for line in head.splitlines()) for head in headers] # requires furthers changes to serialisation
headers2 = [pp.Combine( pp.And( pp.Literal(line.strip())+pp.ZeroOrMore(pp.White()) for line in head.splitlines()) ,adjacent=False) for head in headers]


#header1
startH1=pp.Literal("<H1")
endH1=pp.Literal("/H1>")
H1=pp.Combine(startH1 + pp.SkipTo(endH1) + endH1)

#bookmark tokens
startBM=pp.Literal("<DT><A HREF=") | pp.Literal("<DT><A FEEDURL=")
endBM=pp.Literal("</A>") + pp.Optional(pp.ZeroOrMore(pp.White())+pp.Literal("<DD>")+pp.SkipTo(pp.ZeroOrMore(pp.White())+"<")) #^ (pp.Literal("</A>")+pp.Literal("<DD>")+pp.SkipTo(pp.LineEnd()))
bookmarks= pp.Combine(startBM + '"' + pp.SkipTo('"').setResultsName("HyperLink",listAllMatches=True)+ '"'+ pp.SkipTo(endBM,include=True))

#separator 
separator=pp.Literal("<HR>")

#folder tokens
foldernamestart=pp.Literal("<DT><H3")
foldernameend=pp.Literal("</H3>") ^ (pp.Literal("</H3>")+pp.ZeroOrMore(pp.White())+pp.Literal("<DD>")+pp.SkipTo(pp.LineEnd()))
foldername=pp.Combine(foldernamestart+ pp.SkipTo(">")+">"+pp.SkipTo("</H3>").setResultsName("Folder")+foldernameend)

startlist=pp.Suppress("<DL><p>")
endlist=pp.Suppress("</DL><p>")

folderBM=pp.Forward()
foldercontents=folderBM|separator|bookmarks
folderstruct=pp.Group(foldername+startlist+pp.ZeroOrMore(foldercontents)+endlist)
folderBM<<folderstruct

#parser 
bookmarkshtml=pp.Or(headers2)+H1+pp.Optional(startlist)+pp.ZeroOrMore(foldercontents)+pp.Suppress("</DL>")+pp.Optional(pp.Suppress("<p>"))


#########HELPER FUNCTIONS

#wrap following in a class? wrap everything except parsing stuff into a class?



## all hyperlinks

def hyperlinks(parseresults):
    """returns all hyperlinks from parsed file"""
    try:
        itemlist= parseresults.HyperLink.asList()
    except:
        itemlist=[] # an empty folder
    for item in parseresults:
        if type(item)==types.StringType:
            pass
        elif 'Folder' in item.keys():
            #recursive
            foldercontents=hyperlinks(item)
            itemlist.extend(foldercontents)
    return itemlist

## clean_tree gives a set of nested lists/tuples giving hyperlinks and folders

def clean_tree(parseresults):
    """returns a set of nested lists/tuples from parsed file. Maintains the original folder structure but only containing foldernames and hyperlinks"""
    try:
        itemlist=parseresults.HyperLink.asList()
    except:
        itemlist=[] # an empty folder
    for item in parseresults:
        if type(item)==types.StringType:
            pass
        elif 'Folder' in item.keys():
            #recursive
            foldercontents=clean_tree(item)
            itemlist.append((item.Folder,foldercontents))
    return itemlist

#### Alternative Results Structure ######### a set of nested dictionaries using hyperlinks and folder names as keys and original text as values
# requires use of private attribute of ParseResults!

def bookmarkDict(parseresults):
    """returns a set of nested dictionaries from parsed file. Keys are hyperlinks, values are original strings. Original Folder headers strings are contained under key 'Folder'"""
    #print 'Creating a bookmarkDict'
    new={}
    try:
        for href,pos in parseresults._ParseResults__tokdict['HyperLink']:
            if new.has_key(href):
                new[href]=merge_entries(new[href],parseresults[pos])# if multiple href ? _merge_entries(,)
            else:
                new[href]=parseresults[pos]
    except:
        pass
    for item in parseresults:
        if type(item)==types.StringType:
            pass
        elif 'Folder' in item.keys():
            #print 'Creating a sub-bookmarkDict'
            foldercontents=bookmarkDict(item) #recursion
            foldercontents['Folder']=item[0] # original string for folder header
            if new.has_key(item['Folder']): # if there is more than one folder with the same name.
                print '|'*30+' merging 2 bookmarkDict folders named:',item.Folder
                new[item['Folder']]=merge_bookmarkDict(new[item['Folder']],foldercontents)
            else:
                new[item['Folder']]=foldercontents
    return new

## Creates cleaner parseresults
#removes ICON attribute, ADD_DATE, LAST_CHARSET ??

##removes personal_toolbar_folder tag - procedure.
def depersonalisefolders(parseresults):
    """removes personal_toolbar_folder tag. Acts on ParseResults instance in place (ie. a procedure)."""
    folders=top_folders_dict(parseresults)
    tag=pp.Literal('PERSONAL_TOOLBAR_FOLDER="true" ')
    parser=pp.Combine(pp.Optional(pp.SkipTo(tag)+tag.suppress())+pp.SkipTo(pp.stringEnd))
    for i in folders.values():
        i=i[0]
        parseresults[i][0]=parser.parseString(parseresults[i][0])[0]
    #return parseresults

## writes structure back to file

def _folder_serialize(parseresults,indent):
    tab='    '
    indstr=tab*indent #indentation
    sresult=indstr+parseresults[0]+'\n'
    sresult+=indstr+'<DL><p>'+'\n'
    for item in parseresults[1:]:
        if type(item)==types.StringType:
            sresult+=indstr+tab+item+'\n' #extra indentation
        elif 'Folder' in item.keys():
            sresult+=_folder_serialize(item,indent+1)
    sresult+=indstr+'</DL><p>'+'\n'
    return sresult

def serialize(parseresults):
    """Turns parsed bookmark file back into original string """
    result=''
    result+='\n'.join((parseresults[0],parseresults[1]))+'\n'
    result+='\n'
    result+='<DL><p>'+'\n'
    for item in parseresults[2:]:
        if type(item)==types.StringType:
            result+='    '+item+'\n' #indentation
        else:
            result+=_folder_serialize(item,indent=1)
    result+='</DL><p>'+'\n'
    return result

##writes bookmarkDict back to file

def _folder_serialize_bookmarkDict(bookdict,indent):
    tab='    '
    indstr=tab*indent #indentation
    sresult=indstr+bookdict['Folder']+'\n'
    sresult+=indstr+'<DL><p>'+'\n'
    for key in bookdict:
        if key!='Folder':
            item = bookdict[key]
            if type(item)==str:
                sresult+=indstr+tab+item+'\n' #extra indentation
            elif type(item)==dict:
                sresult+=_folder_serialize_bookmarkDict(item,indent+1)
    sresult+=indstr+'</DL><p>'+'\n'
    return sresult

def serialize_bookmarkDict(bookdict):
    """Turns parsed bookmark file back into original string """
    result=''
    result+=headers[0]+'\n' #headers[0] is that found in the most recent bookmark files
    result+="<H1>Bookmarks Menu</H1>"+'\n'
    result+='\n'
    result+='<DL><p>'+'\n'
    for item in bookdict.values():
        if type(item)==types.StringType:
            result+='    '+item+'\n' #indentation
        else:
            result+=_folder_serialize_bookmarkDict(item,indent=1)
    result+='</DL><p>'+'\n'
    return result


###############Combining two pyparsing.parseResults structures###################
    #strip
    #[0] -header
    #[1] -H1
    #folders of bookmarks , separators , bookmarks

##Looking for duplicate folders in bookmarks tree #


"""
def top_folders(parseresults):
    itemlist=[] # top folder?
    for item in parseresults:
        if type(item)==types.StringType:
            pass
        elif 'Folder' in item.keys():
            itemlist.append(item.Folder)
    return itemlist
"""
def duplicates(seq):
    uniques=set(seq)
    return [ x for x in seq if x not in uniques or uniques.remove(x)]
""""
def uniq(seq):
    seen = set(seq)
    return [ x for x in seq if x in seen and not seen.remove(x)]
"""

def top_folders_dict(parseresults):
    itemlist={} # top folder?
    for j,item in enumerate(parseresults):
        if type(item)==types.StringType:
            pass
        elif 'Folder' in item.keys():
            try:
                itemlist[item.Folder]+=[j]
            except:
                itemlist[item.Folder]=[j]
    return itemlist

def duplicates_dict(seq):
    return [ x for x in seq if len(seq[x])>1]
        
########################

    

##Looks for duplicate bookmarks? make it interactive and like duplicate bookmark add-on

def hyperlinks_bookmarkDict(bookdict):
    """returns all hyperlinks from bookmarkDict"""
    itemlist=[]
    for item in bookdict:
        if type(bookdict[item])==dict:
            #recursive
            foldercontents=hyperlinks_bookmarkDict(bookdict[item])
            itemlist.extend(foldercontents)
        elif item!='Folder' and type(bookdict[item])==str:
            itemlist.append(item)
        elif item!='Folder':
            print 'found an unknown item!: ', item
    return itemlist

## merges bookmarkDict
import copy

def merge_bookmarkDict(bookdict1,bookdict2):
    new=copy.deepcopy(bookdict1)
    if new==bookdict2: #optimisation
        return new
    else:
        for key,item in bookdict2.items():
            if key in new:
                if item == new[key]: #remove duplicates (optimisation)
                    print 
                    print '#'*10+' found duplicate of ',key
                    pass
                elif type(item)==str:
                    update=merge_entries(new[key],item) #strings must be different so need to be merged
                    new[key]=update
                elif type(item)==dict:
                    print '|'*30+' merging 2 bookmarkDicts folders named:', key
                    new[key]=merge_bookmarkDict(new[key],item)
                else:
                    print 'unexpected item:', item
            else:
                new[key]=item
    return new

def merge_entries(line1,line2):
    """merges two bookmark entries that should have the same content but different tags"""
    print 'merging 2 tokens strings'
    if line1==line2: #optimisation
        print 'Tokens are identical!'
        new=copy.copy(line1)
    else: #parse strings, take earlist ADD_DATE and latest LAST_VISIT \ LAST_MODIFIED, choose ID, CHARSET etc from most recent visit.
        #parser
        qt=pp.Suppress('"')
        feedurl='FEEDURL='+qt+pp.SkipTo('"')('feedurl')+qt
        href='HREF='+qt+pp.SkipTo('"')('href')+qt
        date=qt+pp.Word(pp.nums).setParseAction(lambda s,l,t: int(t[0]))+qt
        ad='ADD_DATE='+date('ad')
        lv='LAST_VISIT='+date('lv')
        lm='LAST_MODIFIED='+date('lm')
        ID='ID='+qt+pp.SkipTo(qt)('id')
        possible=feedurl|href|ad|lv|lm
        parser=pp.SkipTo(possible | "ID" | pp.StringEnd()).suppress()+pp.ZeroOrMore(possible)+pp.Optional(pp.SkipTo("ID")+ID)
        #parse
        l1=parser.parseString(line1)
        l2=parser.parseString(line2)
        #return l1,l2
        print '1) ', line1[:500]
        print '2) ', line2[:500]
        #Check for FEEDURL case
        if l1.feedurl!='':
            print "Dealing with a smart bookmark"
            print l1.feedurl
            l1.href=l2.href
        #check HREF
        if l1.href!=l2.href:
            print "Entries don't share location!"
            raise Exception
        #check ID
        if line1==line2.replace(l2.id,l1.id):
            print "strings only differ by ID"
        # ADD_DATE
        l1ad,l2ad=l1.ad,l2.ad
        # Recent change
        l1recent=l2recent=0
        for r in 'lv','lm':
            if r in l1: l1recent=l1recent*(l1recent>l1[r][0]) or l1[r][0]
            if r in l2: l2recent=l2recent*(l2recent>l2[r][0]) or l2[r][0]
        if l1recent>l2recent:
            print 'choosing (1)'
            new=copy.copy(line1)
            if l1ad=='' and l2ad=='':
                pass #no ADD_DATE so it doesn't matter
            elif l1ad=='' and l2ad!='': #add ADD_DATE
                print 'but using ADD_DATE from 2'
                extra='ADD_DATE="'+str(l2ad[0])+'" '
                if new[0:8]=='<DT><H3 ': new=new[0:8]+extra+new[8:] #bookmark foldername token
                else: #must be bookmark token
                    inpos=15+len(l1.href) #position to insert ADD_DATE
                    new=new[0:inpos]+extra+new[inpos:]
            elif l2ad!='' and l2ad[0]<l1ad[0]: #replace ADD_DATE
                print 'but replacing ADD_DATE with that from 2'
                new=new.replace(str(l1ad[0]),str(l2ad[0])) #ADD_DATE should be first item in string with this number!
        else:
            print 'choosing (2)'
            new=copy.copy(line2)
            if l2ad=='' and l1ad=='':
                pass #no ADD_DATE so it doesn't matter
            elif l2ad=='' and l1ad!='':
                print 'but using ADD_DATE from 1'
                extra='ADD_DATE="'+str(l1ad[0])+'" '
                if new[0:8]=='<DT><H3 ': new=new[0:8]+extra+new[8:] #bookmark foldername token
                else: #must be bookmark token
                    inpos=15+len(l2.href) #position to insert ADD_DATE
                    new=new[0:inpos]+extra+new[inpos:]
            elif l1ad!='' and l1ad[0]<l2ad[0]:
                print 'but replacing ADD_DATE with that from 1'
                new=new.replace(str(l2ad[0]),str(l1ad[0])) #ADD_DATE should be first item in string with this number!
        print 'NEW) ', new[:500]
    print ''
    return new
        
##########

def count_folders(bookmarkdict):
    """utility function to count the total number of folders in the collection"""
    count=0
    for entry in bookmarkdict.values():
        if type(entry)==types.DictType:
            count+=1
            count+=count_folders(entry) #recursion again.
    return count
        
    

############################################################################
if __name__=="__main__":
    ##test
    #Loads a bookmarks.html file. 
    #f=file("bookmarks 141208.html",'r')
    #f=file("workshop\\old1\\test\\bookmarks test.html","r")
    #f=file("bookmarks zi.html","r")
    #f=file("test.html")
    #bms=f.read()
    #f.close()
    #parsing 
    #tokens=bookmarkshtml.parseString(bms)

    #ct=clean_tree(tokens)
    #import pprint
    #pprint.pprint(ct)

    #alist=hyperlinks(tokens)

    #output=serialize(tokens)
    #outfile=open('bookmarks test parsed.html','w')
    #outfile.write(output)
    #outfile.close()

    #f2=file("workshop\\old1\\test\\bookmarks zi.html","r")
    #bms2=f2.read()
    #f2.close()
    #parsing 
    #tokens2=bookmarkshtml.parseString(bms2)


    pass
