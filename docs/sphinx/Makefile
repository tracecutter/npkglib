# ---------------------------------------------------------------------------
# docs/sphinx/Makefile — Sphinx documentation builder
#
# Responsibilities:
#   - Build Sphinx outputs from sources in docs/sphinx/
#   - Emit outputs under docs/sphinx/_build/
#
# Non-responsibilities:
#   - Generating documentation sources (handled externally, e.g. psym)
#   - Publishing or installation
# ---------------------------------------------------------------------------

.PHONY: all html singlehtml latex latexpdf epub sync publish clean help

# ------------------------------------------------------------
# Layout
# ------------------------------------------------------------

PROJECT_ROOT := $(abspath ../..)
SPHINX_ROOT  := .

# Tool-neutral source directory
SOURCEDIR    := src
BUILDDIR     := _build

# Auto-detect upstream (e.g. docs/psym/_build/sphinx)
# If not present, operate in standalone mode
SPHINX_UPSTREAM ?=
ifneq ("$(wildcard $(PROJECT_ROOT)/docs/psym/_build/sphinx)","")
SPHINX_UPSTREAM := $(PROJECT_ROOT)/docs/psym/_build/sphinx
endif

# ------------------------------------------------------------
# Sphinx
# ------------------------------------------------------------

SPHINXBUILD ?= sphinx-build

SPHINXOPTS  ?=
SPHINXOPTS  += -d $(BUILDDIR)/doctrees
SPHINXOPTS  += -c $(SPHINX_ROOT)

# Consume exported vars (from parent Makefile)
ifneq ($(strip $(VERSION)),)
SPHINXOPTS += -D release=$(VERSION)
endif

ifneq ($(strip $(PROJECT_NAME)),)
SPHINXOPTS += -D project=$(PROJECT_NAME)
endif


# ------------------------------------------------------------
# Default target
# ------------------------------------------------------------

all: html

# ------------------------------------------------------------
# Sync using psym (if present) to build sphinx projection
# ------------------------------------------------------------

sync:
	@echo "ℹ️  Repo in sync for sphinx docs."

pull-upstream:
	@if [ -d "$(PROJECT_ROOT)/docs/psym" ] && [ -f "$(PROJECT_ROOT)/docs/psym/Makefile" ]; then \
		echo "🔄 Sync (sphinx): building projection via docs/psym…"; \
		$(MAKE) -C $(PROJECT_ROOT)/docs/psym --no-print-directory sphinx; \
	fi; \
	\
	if [ -d "$(PROJECT_ROOT)/docs/psym/_build/sphinx" ]; then \
		echo "📥 Sync (sphinx): preparing to copy projection into $(SOURCEDIR)…"; \
		if [ -z "$$(ls -A $(PROJECT_ROOT)/docs/psym/_build/sphinx 2>/dev/null)" ]; then \
			echo "❌ Upstream source exists but is empty — refusing to sync"; \
			exit 1; \
		fi; \
		echo "📥 Sync (sphinx): copying projection into $(SOURCEDIR)…"; \
		rsync -av --delete \
			$(PROJECT_ROOT)/docs/psym/_build/sphinx/ \
			$(SOURCEDIR)/; \
	else \
		echo "ℹ️  No upstream source projection (using local sources in $(SOURCEDIR)/)"; \
	fi

# ------------------------------------------------------------
# Build targets
# ------------------------------------------------------------

html: pull-upstream
	@echo "📘 Building Sphinx HTML..."
	@echo "   project=$(PROJECT_NAME) version=$(VERSION)"
	@$(SPHINXBUILD) -b html $(SPHINXOPTS) $(SOURCEDIR) $(BUILDDIR)/html

singlehtml: sync
	@echo "📘 Building Sphinx single-page HTML..."
	@$(SPHINXBUILD) -b singlehtml $(SPHINXOPTS) $(SOURCEDIR) $(BUILDDIR)/singlehtml

latex: sync
	@echo "📘 Building Sphinx LaTeX..."
	@$(SPHINXBUILD) -b latex $(SPHINXOPTS) $(SOURCEDIR) $(BUILDDIR)/latex

latexpdf: latex
	@echo "📘 Building PDF from LaTeX..."
	@$(MAKE) -C $(BUILDDIR)/latex --no-print-directory all-pdf

epub: sync
	@echo "📘 Building EPUB..."
	@$(SPHINXBUILD) -b epub $(SPHINXOPTS) $(SOURCEDIR) $(BUILDDIR)/epub

# ------------------------------------------------------------
# Publish (GitHub Pages)
# ------------------------------------------------------------

publish: html
	@echo "🌐 Publishing documentation to GitHub Pages…"

	@if [ ! -d "$(BUILDDIR)/html" ]; then \
		echo "❌ Missing Sphinx HTML build"; exit 1; \
	fi

	@REMOTE_URL=$$(git config --get remote.origin.url); \
	if [ -z "$$REMOTE_URL" ]; then \
		echo "❌ Could not determine git remote"; exit 1; \
	fi; \
	TMP_DIR=$$(mktemp -d); \
	cp -r $(BUILDDIR)/html/* $$TMP_DIR; \
	touch $$TMP_DIR/.nojekyll; \
	cd $$TMP_DIR && \
		git init -q && \
		git checkout -b gh-pages && \
		git add -A && \
		git commit -m "docs: publish $(VERSION)" >/dev/null && \
		git remote add origin $$REMOTE_URL && \
		echo "🚀 Pushing to gh-pages…" && \
		git push -f origin gh-pages:gh-pages >/dev/null && \
	cd - >/dev/null && \
	rm -rf $$TMP_DIR

	@echo "✔️ Documentation published."

# ------------------------------------------------------------
# Clean
# ------------------------------------------------------------

clean:
	@echo "🧹 Cleaning Sphinx build artifacts..."
	@rm -rf $(BUILDDIR)

# ------------------------------------------------------------
# Help
# ------------------------------------------------------------

help:
	@echo "Sphinx sources are located under src/."
	@echo "They may be generated externally (e.g. by psym) or edited directly."
	@echo ""
	@echo "Sphinx build targets:"
	@echo "  html         Build HTML documentation (default)"
	@echo "  singlehtml   Build single-page HTML"
	@echo "  latexpdf     Build PDF via LaTeX"
	@echo "  epub         Build EPUB"
	@echo "  clean        Remove build artifacts"
	@echo ""
	@echo "Publish html to GitHub pages:"
	@echo "  publish      Build and publish _build/html to gh-pages."

