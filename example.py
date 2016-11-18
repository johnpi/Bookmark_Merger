#finds all my collected firefox bookmarks and merges them!
bookmark_dir='.'

import bookmark_pyparser as bpp

#finds a list (recursively) of all html (bookmark) files in the chosen directory
import os
htmlfiles=[]
for root,dirs,files in os.walk(bookmark_dir):
	print root
	htmlfiles_tmp=[os.path.join(root,fils) for fils in files if fils.split('.')[-1].lower()=='html']
	htmlfiles.extend(htmlfiles_tmp)

print
result={}
numhref=0
for bookmarkfile in htmlfiles:
        print '############################## parsing ', bookmarkfile
        parsedfile=bpp.bookmarkshtml.parseFile(file(bookmarkfile))
        numhref+=len(bpp.hyperlinks(parsedfile))
        print '############################## creating a bookmarkDict '
        bmDict=bpp.bookmarkDict(parsedfile)
        print '############################## merging latest file into result'
        result=bpp.merge_bookmarkDict(result,bmDict)
    

finalfile=file('merged bookmarks.html', 'w')
finalstr=bpp.serialize_bookmarkDict(result)
finalfile.write(finalstr)
finalfile.close()

print 'total nunber of hyperlinks found = ', numhref
print 'number of hyperlinks in final file=', len(bpp.hyperlinks_bookmarkDict(result))
print 'number of unique hyperlinks =', len(set(bpp.hyperlinks_bookmarkDict(result)))
print 'number of folders =', bpp.count_folders(result)