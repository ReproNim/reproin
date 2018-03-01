walkthrough-%.md: Makefile
	for f in source/images/walkthrough-$*/*.png; do \
	   bn=$$(basename $$f); \
	   echo "### $$bn\n\n![$$bn]($$f)\n"; \
	done >| $@

