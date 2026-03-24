chdir c:\dev\python\MemoryServes\docs
sphinx-build -W -b html source build\html
sphinx-build -W -b htmlhelp source build\htmlhelp
set htmlhelp=c:\dev\python\MemoryServes\docs\build\htmlhelp\MemoryServesManual.hhp
"c:\program files (x86)\HTML Help Workshop\hhc" %htmlhelp%
chdir c:\dev\python\MemoryServes

set basedir=c:\dev\python\MemoryServes

echo Creating directories...
mkdir %basedir%\media\manual\
mkdir %basedir%\media\manual\_images\
mkdir %basedir%\media\manual\_sources\
mkdir %basedir%\media\manual\_static\
echo Copying files...
copy %basedir%\docs\build\html\*.html               %basedir%\media\manual\
copy %basedir%\docs\build\html\_images\*.png        %basedir%\media\manual\_images\
copy %basedir%\docs\build\html\_sources\*.txt       %basedir%\media\manual\_sources\
copy %basedir%\docs\build\html\_static\*            %basedir%\media\manual\_static\
