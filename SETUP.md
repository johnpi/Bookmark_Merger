#Setup

##Setup in a virtual environment


###Installing Miniconda

If you haven't done already install a virtual environment, as an example we will use miniconda.
Install miniconda:

wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh

bash Miniconda2-latest-Linux-x86_64.sh


###Set up Bookmark Merger

conda create -n Bookmark_Merger python=2.7

source activate Bookmark_Merger

conda install pyparsing

conda install git

conda clean -t

git clone https://github.com/johnpi/Bookmark_Merger.git

cd Bookmark_Merger/


Now Bookmark Merger is ready. An example of how to use it is this

python bookmark_merger.py ~/Documents/Bookmarks/ -o ~/Documents/Bookmarks/result.html

This will read all .html files in ~/Documents/Bookmarks/ and after merging their contents will store the result in ~/Documents/Bookmarks/result.html
