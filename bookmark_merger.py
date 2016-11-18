#finds all my collected firefox bookmarks and merges them!
import bookmark_pyparser as bpp
import os
from optparse import OptionParser

usage="""usage: %prog [options] dir_path1 dir_path2

All html files in the given directories will be assumed to be firefox 
bookmark.html files.
If no directory is given then the current directory will be used"""

parser = OptionParser(usage=usage)
parser.add_option("-r","--recursive",
                  action="store_true",dest="recursive", default=False,
                  help="Recursively explore given directory for bookmark files")
parser.add_option("-o", "--outfile", dest="outfile",default="merged bookmarks.html",
                  help="write output to FILE [default: %default]", metavar="FILE")

(options, args) = parser.parse_args()

outfile=options.outfile
recursive=options.recursive
if args==[]:
    dir_path='.'
else:
    dir_path=args

#finds a list (recursively) of all html (bookmark) files in the chosen directory
htmlfiles=[]
for path in dir_path:
    if recursive==True:
        for root,dirs,files in os.walk(path):
            print root
            htmlfiles_tmp=[os.path.join(root,fils) for fils in files if fils.split('.')[-1].lower()=='html']
            htmlfiles.extend(htmlfiles_tmp)
    else:
        root=os.path.abspath(path)
        files=os.listdir(path)
        print root
        htmlfiles_tmp=[os.path.join(root,fils) for fils in files if fils.split('.')[-1].lower()=='html']
        htmlfiles.extend(htmlfiles_tmp)


print
result={}
numhref=0
for bookmarkfile in htmlfiles:
        print '##### parsing ', os.path.relpath(bookmarkfile,path)
        parsedfile=bpp.bookmarkshtml.parseFile(file(bookmarkfile))
        numhref+=len(bpp.hyperlinks(parsedfile))
        print '#### creating a bookmarkDict '
        bmDict=bpp.bookmarkDict(parsedfile)
        print '#### merging latest file into result'
        result=bpp.merge_bookmarkDict(result,bmDict)
    
finalfile=file(outfile, 'w')
finalstr=bpp.serialize_bookmarkDict(result)
finalfile.write(finalstr)
finalfile.close()

print 'total nunber of hyperlinks found = ', numhref
print 'number of hyperlinks in final file=', len(bpp.hyperlinks_bookmarkDict(result))
print 'number of unique hyperlinks =', len(set(bpp.hyperlinks_bookmarkDict(result)))
print 'number of folders =', bpp.count_folders(result)


