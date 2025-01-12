REM make both html & singlepage and publish to surge
sphinx-build -M clean . _build
sphinx-build -M html . _build
sphinx-build -M singlehtml . _build
copy _build\singlehtml\index.html _build\html\single.html
surge _build\html sayc-joel.surge.sh
