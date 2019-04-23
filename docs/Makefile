# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	#sphinx-apidoc -f --separate --module-first --ext-autodoc -o source/container ../container
	#sphinx-apidoc -f --separate --module-first --ext-autodoc -o source/scenarios ../scenarios
	#sphinx-apidoc -f --separate --module-first --ext-autodoc -o source/utils ../utils
	# Add -E option once all items are documented
	sphinx-apidoc -E -f -e -M -T --ext-autodoc -o source/api/ ../ ../docs/ ../controller/[!_]* ../setup.py
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)