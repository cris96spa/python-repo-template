.PHONY: all tikz tikz-dark dark charts check-tools clean help

GENERATED_DIR := generated
TIKZ_SHARED := $(abspath tikz/_shared)
TIKZ_DENSITY ?= 800
PDFLATEX ?= pdflatex

help: # print all the available targets
	@echo "\nAvailable targets:\n"
	@grep -E '^[a-zA-Z_-]+:.*?# .*$$' $(MAKEFILE_LIST) | sed 's/:.*#/\t/' | column -t -s '	' ; echo

all: tikz charts # build every diagram

check-tools: # report which diagram tools are installed
	@for tool in $(PDFLATEX) magick pdf2svg; do \
		if command -v $$tool > /dev/null; then \
			echo "  found    $$tool"; \
		else \
			echo "  MISSING  $$tool"; \
		fi; \
	done
	@if uv run --extra diagrams python -c "import xy" > /dev/null 2>&1; then \
		echo "  found    xy"; \
	else \
		echo "  MISSING  xy (run: make -C .. install-diagrams)"; \
	fi

tikz: | $(GENERATED_DIR) # compile every tikz source to pdf, png and svg
	@mkdir -p $(GENERATED_DIR)/pdf $(GENERATED_DIR)/png $(GENERATED_DIR)/svg
	@failed=0; \
	for texfile in $$(find tikz -name '*_tikz.tex' | sort); do \
		dir=$$(dirname "$$texfile"); \
		base=$$(basename "$$texfile" .tex); \
		echo "Compiling $$base"; \
		( cd "$$dir" && TEXINPUTS=".:$(TIKZ_SHARED):" $(PDFLATEX) -interaction=nonstopmode "$$base.tex" > /dev/null 2>&1 ); \
		if [ -f "$$dir/$$base.pdf" ]; then \
			cp "$$dir/$$base.pdf" $(GENERATED_DIR)/pdf/$$base.pdf; \
			if command -v magick > /dev/null; then \
				magick -density $(TIKZ_DENSITY) "$$dir/$$base.pdf" -trim -quality 100 $(GENERATED_DIR)/png/$$base.png; \
			else \
				echo "  skipped png: magick not installed"; \
			fi; \
			if command -v pdf2svg > /dev/null; then \
				pdf2svg "$$dir/$$base.pdf" $(GENERATED_DIR)/svg/$$base.svg; \
			else \
				echo "  skipped svg: pdf2svg not installed"; \
			fi; \
		else \
			echo "  FAILED $$base"; \
			tail -n 20 "$$dir/$$base.log" 2>/dev/null; \
			failed=1; \
		fi; \
		rm -f "$$dir/$$base.aux" "$$dir/$$base.log" "$$dir/$$base.pdf"; \
	done; \
	exit $$failed

tikz-dark: | $(GENERATED_DIR) # compile every tikz source to a transparent dark png
	@mkdir -p $(GENERATED_DIR)/png
	@failed=0; \
	for texfile in $$(find tikz -name '*_tikz.tex' | sort); do \
		dir=$$(dirname "$$texfile"); \
		base=$$(basename "$$texfile" .tex); \
		echo "Compiling $$base (dark)"; \
		( cd "$$dir" && TEXINPUTS=".:$(TIKZ_SHARED):" $(PDFLATEX) -interaction=nonstopmode -jobname "$$base-dark" "\def\figdark{1}\input{$$base.tex}" > /dev/null 2>&1 ); \
		if [ -f "$$dir/$$base-dark.pdf" ]; then \
			if command -v magick > /dev/null; then \
				magick -density $(TIKZ_DENSITY) -background none "$$dir/$$base-dark.pdf" -trim -quality 100 $(GENERATED_DIR)/png/$$base-dark.png; \
			else \
				echo "  skipped png: magick not installed"; \
			fi; \
		else \
			echo "  FAILED $$base-dark"; \
			tail -n 20 "$$dir/$$base-dark.log" 2>/dev/null; \
			failed=1; \
		fi; \
		rm -f "$$dir/$$base-dark.aux" "$$dir/$$base-dark.log" "$$dir/$$base-dark.pdf"; \
	done; \
	exit $$failed

charts: | $(GENERATED_DIR) # render every chart script to png and svg
	@mkdir -p $(GENERATED_DIR)/png $(GENERATED_DIR)/svg
	@failed=0; \
	for script in $$(find charts -name '*.py' | sort); do \
		echo "Rendering $$script"; \
		for format in png svg; do \
			if ! uv run --extra diagrams python "$$script" --output-dir $(GENERATED_DIR)/$$format --format $$format; then \
				echo "  FAILED $$script ($$format)"; \
				failed=1; \
			fi; \
		done; \
	done; \
	exit $$failed

dark: tikz-dark # build every dark-mode variant

$(GENERATED_DIR):
	mkdir -p $(GENERATED_DIR)

clean: # remove generated output and latex build artifacts
	rm -rf $(GENERATED_DIR)
	find tikz \( -name '*.pdf' -o -name '*.aux' -o -name '*.log' \) -delete
