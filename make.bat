@ECHO OFF

if "%1" == "docs" (
	cd docs
	call make.bat html
	cd ..
)

if "%1" == "test" (
	cd docs
	call make.bat pickle
	cd ..
	python runtests.py
)

if "%1" == "test-all" (
	cd docs
	call make.bat pickle
	cd ..
	tox
)