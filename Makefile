.PHONY: all help init init-git init-gh \
		refresh reinstate reincarnate \
		clean clean-pyc clean-build clean-docs clean-gen clean-bak \
		check check-sys check-types check-readme check-lint check-style reformat \
		test test-coverage test-all \
		docs docs-% docs-%-% \
		dist release unrelease publish unpublish \
		pub-docs pub-gh pub-pypi pub-brew \
		status corpus


.DEFAULT_GOAL := refresh

# Require pfig
PFIG := $(shell command -v pfig 2>/dev/null)
ifeq ($(PFIG),)
$(error ❌ pfig is required. Install via: pipx install pfig)
endif

# exported variables
export VERSION		:= $(shell pfig get -k project.version 2>/dev/null)
export PROJECT_NAME	:= $(shell pfig get -k project.name 2>/dev/null)

# git tag state
BRANCH				:= $(shell git rev-parse --abbrev-ref HEAD)
TAG					:= $(if $(filter main,$(BRANCH)),v$(VERSION),$(BRANCH)/v$(VERSION))

# Project metadata
DOCS_ROOT			:= $(or $(shell pfig get -k tool.pfig.docs-dir 2>/dev/null),docs)

DOCS_TOOLS			:= $(filter-out __%,$(notdir $(patsubst %/,%,$(wildcard docs/*/))))
ASSETS_DIR			:= $(PROJECT_NAME)/_assets
README_BUILD		:= $(DOCS_ROOT)/pfig/_build/readme/README.md
README_ROOT			:= README.md
BREWREPO			:= homebrew-$(PROJECT_NAME)

# Does this project need to be executed in-situ within target project?
NPKG_TYPE			:= $(or $(shell pfig get -k tool.npkg.type 2>/dev/null),external)
NPKG_ROLE			:= $(or $(shell pfig get -k tool.npkg.role 2>/dev/null),tool)

IS_IN_SITU			:= $(if $(filter in-situ,$(NPKG_TYPE)),1,0)
IS_EXTERNAL			:= $(if $(filter external,$(NPKG_TYPE)),1,0)
IS_TOOL				:= $(if $(filter tool,$(NPKG_ROLE)),1,0)
IS_PACKAGE			:= $(if $(filter package,$(NPKG_ROLE)),1,0)

INIT_STAMP			= .init_stamp

# ------------------------------------------------------------
# 🔒 Development safety checks
# ------------------------------------------------------------

# expected venv = current directory name
EXPECTED_VENV := $(notdir $(CURDIR))

define ensure-venv-active
	@if [ -z "$${VIRTUAL_ENV}" ]; then \
		echo "❌ ERROR: No virtualenv active."; \
		echo "   Expected: $(EXPECTED_VENV)"; \
		exit 1; \
	fi
endef

define ensure-correct-venv
	@if [ "$(EXPECTED_VENV)" != "$$(basename $$VIRTUAL_ENV)" ]; then \
		echo "❌ ERROR: Wrong virtualenv active: $$(basename $$VIRTUAL_ENV)"; \
		echo "   Expected: $(EXPECTED_VENV)"; \
		exit 1; \
	fi
endef

all: clean check refresh docs test

help:
	@echo "init - populate a virtual env project with required dependencies"
	@echo "init-git - create, initilize, and commit initial local git repo"
	@echo "init-gh - create github remote and push project to GitHub"
	@echo "refresh - refresh $(PROJECT_NAME) into active venv (editable)"
	@echo "reinstate - reinstantiate $(PROJECT_NAME) with latest dependencies."
	@echo "reincarnate - rebuild $(PROJECT_NAME) venv from scratch."
	@echo "clean - full clean of all artifacts and backup files"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-docs - remove doc build artifacts"
	@echo "clean-gen - remove other generated artifacts"
	@echo "clean-bak - remove backup files"
	@echo "check - execute all checks including lint and style compliance"
	@echo "check-sys - check all system dependencies"
	@echo "check-readme - check readme matches current usage"
	@echo "check-lint - check for lint using ruff"
	@echo "check-style - check style compliance with black"
	@echo "check-types - check types with mypy"
	@echo "reformat - reformat all python files to comply with black style"
	@echo "test - run tests quickly with the default Python"
	@echo "test-coverage - check code coverage"
	@echo "test-all - run tests on every Python version with nox"
	@echo "readme - generate README.md from usage information"
	@echo "docs - generate standard documentation (readme, manpages, ...)"
	@echo "docs-sync - publish pfig artifacts and then generate standard documentation (sphinx, ...)"
	@echo "docs-all - generate additional documentation (e.g. PDF, EPUB, ...)"
	@echo "docs-<tool>-all - generate standard documentation from tool (pfig, sphinx)"
	@echo "docs-<tool>-publish - publish documentation from tool build (README.md)"
	@echo "docs-<tool>-clean - remove documentation build artifacts"
	@echo "preflight - check everything is ready for release"
	@echo "dist - generate full distribution and stage package for release."
	@echo "release - tag, build, push, and perform local post-release install if applicable"
	@echo "unrelease - remove local release from current environment and local installation (pipx)"
	@echo "publish -  publish current release and documentation to GitHub for pip and brew install"
	@echo "pub-docs - publish documents on GitHub.io"
	@echo "pub-pfix - publish release to pfix static pip index"
	@echo "pub-gh - publish release on GitHub"
	@echo "pub-pypi - publish release on PyPi"
	@echo "pub-brew - publish release on GitHub as homebrew tap"
	@echo "unpublish -  remove named release from all published sites"

init: $(INIT_STAMP)
	@echo "✅ Project initialization complete."

$(INIT_STAMP):
	$(call ensure-venv-active)
	$(call ensure-correct-venv)

	@echo "🔧 Initializing development environment for $(PROJECT_NAME)…"

	@echo "📦 Installing base development tools…"
	pip install --upgrade pip wheel build twine

	@echo "📦 Installing project in editable mode (dev)…"
	@if pip install -e ".[dev]"; then \
		echo "✔ Editable install complete"; \
	else \
		echo "⚠️ Dev install incomplete (likely missing local deps such as pfig)"; \
	fi

	@echo "📚 Configuring MANPATH (if applicable)…"
	@if [ "$(IS_TOOL)" = "1" ] && [ "$(IS_EXTERNAL)" = "1" ] && [ -d docs/pfig/_build/manpage ]; then \
		HOOKDIR="$${VIRTUAL_ENV}/bin/postactivate.d"; \
		HOOK="$$HOOKDIR/$(PROJECT_NAME)-manpath.sh"; \
		MANDEV="$(CURDIR)/docs/pfig/_build/manpage"; \
		mkdir -p "$$HOOKDIR"; \
		echo "# $(PROJECT_NAME) dev manpages" > "$$HOOK"; \
		echo "DEV_MANPATH=\"$$MANDEV\"" >> "$$HOOK"; \
		echo "case \":\$$MANPATH:\" in" >> "$$HOOK"; \
		echo "  *:\$$DEV_MANPATH:*) ;;" >> "$$HOOK"; \
		echo "  *) export MANPATH=\"\$$DEV_MANPATH:\$$(manpath)\" ;; " >> "$$HOOK"; \
		echo "esac" >> "$$HOOK"; \
		echo "✔ MANPATH hook installed"; \
		echo ""; \
		echo "ℹ Reactivate the venv to apply:"; \
		echo "  deactivate && source $${VIRTUAL_ENV}/bin/activate"; \
	else \
		echo "ℹ️ Skipping MANPATH hook"; \
	fi

	@echo "🔍 Running initial lint (if applicable)…"
	@if [ "$(IS_TOOL)" = "1" ] && command -v pfig >/dev/null 2>&1; then \
		pfig lint || echo "⚠️ pfig lint reported issues"; \
	else \
		echo "ℹ️ Skipping system lint"; \
	fi

	@touch $(INIT_STAMP)

init-git:
	@if [ -d .git ]; then \
		echo "⚠️ Git repo already exists. Skipping init."; \
		exit 0; \
	fi
	@echo "🔧 Initializing local git repo…"
	@git init
	@git add .
	@git commit -m 'Initial commit'
	@echo "✅ Local git repo ready."

GH_VISIBILITY ?= private   # or override with: make init-gh GH_VISIBILITY=public

init-gh:
	@if ! command -v gh >/dev/null 2>&1; then \
		echo "❌ GitHub CLI (gh) not installed. Install with: brew install gh"; \
		exit 1; \
	fi
	@if [ ! -d .git ]; then \
		echo "❌ No local git repo. Run: make init-git"; \
		exit 1; \
	fi
	@echo "🐙 Preparing GitHub repository $(PROJECT_NAME)…"
	@if gh repo view $(PROJECT_NAME) >/dev/null 2>&1; then \
		echo "⚠️ GitHub repo already exists; skipping creation."; \
	else \
		echo "📦 Creating GitHub repo: $(PROJECT_NAME) ($(GH_VISIBILITY))"; \
		gh repo create $(PROJECT_NAME) --source=. --$(GH_VISIBILITY) --push; \
	fi
	@echo "🔼 Pushing local history to GitHub…"
	@git push -u origin main
	@echo "🌐 Ensuring gh-pages branch exists…"
	@if git ls-remote --exit-code --heads origin gh-pages >/dev/null 2>&1; then \
		echo "⚠️ gh-pages already exists; skipping creation."; \
	else \
		CUR_BRANCH=$$(git branch --show-current); \
		git checkout --orphan gh-pages >/dev/null 2>&1; \
		git rm -rf . >/dev/null 2>&1 || true; \
		printf "<!doctype html><meta charset=\"utf-8\"><title>$(PROJECT_NAME)</title><h1>$(PROJECT_NAME)</h1><p>GitHub Pages branch initialized.</p>\n" > index.html; \
		touch .nojekyll; \
		git add index.html .nojekyll; \
		git commit -m "Initialize gh-pages" >/dev/null; \
		git push -u origin gh-pages; \
		git checkout $$CUR_BRANCH >/dev/null 2>&1; \
	fi
	@echo "✅ GitHub project ready."
	@echo "ℹ️  To enable Pages, go to: Settings → Pages → set source to gh-pages branch."

# ------------------------------------------------------------
#  🟩 Rules for development workflow support
# ------------------------------------------------------------

# Default dev twitch:
# Reassert editable wiring only (cheap, non-destructive, no resolver churn)
refresh:
	$(call ensure-venv-active)
	$(call ensure-correct-venv)
	@echo "📦 Refreshing editable install of $(PROJECT_NAME)…"
	python -m pip install --editable .
	@echo "✅ $(PROJECT_NAME) refreshed (editable)."

# Reinstate declared intent:
# Ensure the active environment reflects pyproject.toml,
# upgrading eagerly *within declared constraints*.
#
# Notes:
#  - This may advance the environment ahead of pyproject.toml floors.
#  - No packages are removed; hitch-hiking cruft is left intact.
#  - Any resulting intent drift is surfaced by `pfig lint`
#    and resolved explicitly via `pfig restate`.
reinstate:
	$(call ensure-venv-active)
	$(call ensure-correct-venv)
	@echo "🔎 Validating declared intent…"
	@pfig lint || (echo "❌ Package dependency version problem; fix with 'pfig restate' or edit pyproject.toml" && exit 1)
	@echo "♻️  Reinstating environment to declared intent (eager)…"
	python -m pip install -U pip setuptools wheel
	python -m pip install --upgrade-strategy eager --editable .[dev]
	@echo "✅ Environment declared project dependencies now in effect."

# Reincarnate virtual environment:
# This destroys(!) the project virtual environment and recreates it (e.g. changing Python versions)
reincarnate:
	@echo "🔥 Reincarnating $(PROJECT_NAME)…"

	@if [ "$$(basename "$$VIRTUAL_ENV")" = "$(PROJECT_NAME)" ]; then \
		echo "❌ Refusing to reincarnate active environment '$(PROJECT_NAME)'."; \
		echo "👉 Run: deactivate"; \
		exit 1; \
	fi

	rmvirtualenv $(PROJECT_NAME) 2>/dev/null || true
	mkvirtualenv $(PROJECT_NAME)

	. $(WORKON_HOME)/$(PROJECT_NAME)/bin/activate && \
		pip install -U pip setuptools wheel && \
		pip install -e .[dev]

	@echo "✨ $(PROJECT_NAME) reborn."
	@echo "👉 Enter with: workon $(PROJECT_NAME)"

# ------------------------------------------------------------
#  🟩 Rules to tidy up the project
# ------------------------------------------------------------

clean: clean-pyc clean-build clean-docs clean-bak

clean-pyc:
	find . -name '__pycache__' -type d -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr $(ASSETS_DIR)
	rm -fr downloads/
	rm -fr *.egg-info
	rm -fr htmlcov/

clean-docs:
	@echo "🧹 Cleaning documentation tools..."
	@for tool in $(DOCS_TOOLS); do \
		if [ -f "docs/$$tool/Makefile" ]; then \
			echo "🧼 Cleaning $$tool..."; \
			$(MAKE) -C docs/$$tool --no-print-directory clean; \
		fi \
	done

clean-bak:
	find . -name '*.bak' -exec rm -f {} +

# ------------------------------------------------------------
#  🟩 Rules to check for lint, style, formatting
# ------------------------------------------------------------

check: check-sys check-readme check-lint check-style check-types check-version

check-sys:
	@if [ "$(IS_TOOL)" = "1" ]; then \
		echo "🔍 Running system/environment validation via pfig lint…" \
		pfig lint; \
	else \
		echo "ℹ️ Skipping system lint (package project)"; \
	fi

check-readme:
	@echo "🔍 Checking README.md is current…"
	@if [ ! -f "$(README_BUILD)" ]; then \
		echo "❌ Generated README missing: $(README_BUILD)"; \
		echo "   Run: make docs"; \
		exit 1; \
	fi
	@diff -u $(README_BUILD) $(README_ROOT) >/dev/null || \
		( echo "❌ README.md is out of date. Run: make docs-sync" && exit 1 )
	@echo "✅ README.md is up to date."

check-style:
	black --check --diff .

check-lint:
	ruff check --no-cache .

check-types:
	mypy $(PROJECT_NAME)

check-version:
	@echo "🔢 Checking version lineage…"; \
	branch=$$(git rev-parse --abbrev-ref HEAD); \
	version="$(VERSION)"; \
	\
	if [ "$$branch" = "main" ]; then \
		pattern="^v[0-9]"; \
	else \
		pattern="^$$branch/v[0-9]"; \
	fi; \
	\
	latest=$$(git tag -l | grep -E "$$pattern" | sed -E 's|.*/v||; s|^v||' | sort -V | tail -n1); \
	\
	if [ -n "$$latest" ]; then \
		printf "   latest: %s\n" "$$latest"; \
		printf "   current: %s\n" "$$version"; \
		\
		if [ "$$latest" = "$$version" ] || \
		   [ "$$(printf "%s\n%s\n" "$$latest" "$$version" | sort -V | head -n1)" = "$$version" ]; then \
			echo "❌ Version $$version is not a valid successor of $$latest"; \
			exit 1; \
		fi; \
	else \
		echo "   (no prior tags in this lineage)"; \
	fi

reformat:
	black .

# ------------------------------------------------------------
# 🧪 Rules to test package
# ------------------------------------------------------------

test:
	pytest -q

test-verbose:
	pytest -v

test-one:
	pytest -q $(TEST)

# ------------------------------------------------------------
#  🟩 Documentation rules
# ------------------------------------------------------------

docs:
	@echo "📚 Building documentation tools..."
	@for tool in $(DOCS_TOOLS); do \
		$(MAKE) docs-$$tool; \
	done

docs-sync:
	@echo "🔄 Syncing documentation tools..."
	@for tool in $(DOCS_TOOLS); do \
		$(MAKE) docs-$$tool-sync; \
	done

docs-%:
	@rest=$*; \
	tool=$${rest%%-*}; \
	backend=$${rest#*-}; \
	if [ "$$tool" = "$$backend" ]; then backend=""; fi; \
	if [ -z "$$backend" ]; then \
		if [ -f docs/$$tool/Makefile ]; then \
			echo "🔧 Building docs/$$tool"; \
			$(MAKE) -C docs/$$tool --no-print-directory; \
		else \
			echo "ℹ️ Skipping $$tool (no Makefile)"; \
		fi; \
	else \
		if [ -f docs/$$tool/Makefile ]; then \
			echo "🔧 Building docs/$$tool target $$backend"; \
			$(MAKE) -C docs/$$tool --no-print-directory $$backend; \
		else \
			echo "❌ Unknown docs tool: $$tool"; \
			exit 1; \
		fi; \
	fi

# MANPATH modification if venv hook not added by init (not run)
manpath:
	@echo "export MANPATH=\"$(CURDIR)/docs/pfig/_build/manpage:$$HOME/.local/share/man:$$(manpath)\""

# ------------------------------------------------------------
#  📦 Build Python distribution
# ------------------------------------------------------------

dist:
	@echo "📦 Building distribution artifacts…"

	[ -n "$(PROJECT_NAME)" ] && rm -rf "$(PROJECT_NAME)/_assets"
	rm -rf dist/

	@echo "📜 Writing asset manifest…"
	mkdir -p $(PROJECT_NAME)/_assets
	pfig get -m > $(PROJECT_NAME)/_assets/manifest.toml

	@echo "📦 Staging assets…"
	pfig get -l | while IFS=$$'\t' read -r src dst; do \
		dst="$(PROJECT_NAME)/$$dst"; \
		mkdir -p "$$(dirname "$$dst")"; \
		cp "$$src" "$$dst"; \
	done

	@echo "🐍 Building Python distribution…"
	@python -m build 2>&1 | \
	grep -v -e "^copying " \
		   -e "^adding " \
		   -e "^creating " \
		   -e "^writing "

	@echo "✅ dist ready."

# ------------------------------------------------------------
#  🚀 RELEASE / PUBLISH PIPELINE
# ------------------------------------------------------------

preflight: validate-npkg clean refresh docs docs-sync test check dist
	@echo "🔍 Preflight: validating release readiness…"
	@if [ "$(IS_TOOL)" = "1" ]; then \
		pfig lint release; \
	else \
		echo "ℹ️ Skipping release-mode system lint (package project)"; \
	fi
	@echo "✅ Takeoff clearance granted for $(PROJECT_NAME) $(VERSION)"

release-guard:
	$(call ensure-venv-active)
	$(call ensure-correct-venv)
	@{ \
		branch=$$(git rev-parse --abbrev-ref HEAD); \
		[ -n "$$branch" ] && [ "$$branch" != "HEAD" ] || { \
			echo "❌ Cannot release from detached HEAD"; exit 1; }; \
		[ -z "$$(git status --porcelain)" ] || { \
			echo "❌ Working tree is dirty. Commit or stash before tagging."; \
			exit 1; }; \
	}

validate-npkg:
	@if [ "$(IS_PACKAGE)" = "1" ] && [ "$(IS_EXTERNAL)" = "1" ]; then \
		echo "❌ Invalid config: package cannot be external"; \
		exit 1; \
	fi

status:
	@echo "BRANCH=$(BRANCH)"
	@echo "TAG=$(TAG)"
	@echo "NPKG_ROLE=$(NPKG_ROLE)"
	@echo "NPKG_TYPE=$(NPKG_TYPE)"
	@echo "IS_TOOL=$(IS_TOOL)"
	@echo "IS_PACKAGE=$(IS_PACKAGE)"
	@echo "IS_EXTERNAL=$(IS_EXTERNAL)"
	@echo "IS_IN_SITU=$(IS_IN_SITU)"

# ------------------------------------------------------------
#  🚀 Local release
# ------------------------------------------------------------

release: release-guard preflight
	@echo "🚀 Releasing $(PROJECT_NAME) $(VERSION)…"
	@echo "🌿 $(BRANCH) → 🏷️ $(TAG)"

	@# --------------------------------------------------------
	@# Ensure branch is not a namespace parent
	@# --------------------------------------------------------
	@if git for-each-ref --format='%(refname:short)' refs/heads | grep -q "^$(BRANCH)/"; then \
		echo "❌ Branch '$(BRANCH)' has children; cannot release from namespace"; \
		exit 1; \
	fi

	@# --------------------------------------------------------
	@# Ensure tag does NOT already exist
	@# --------------------------------------------------------
	@if git rev-parse "$(TAG)" >/dev/null 2>&1; then \
		echo "❌ Tag $(TAG) already exists"; \
		echo ""; \
		echo "💡 You probably want to bump the version:"; \
		echo "   pfig bump patch|minor|major"; \
		exit 1; \
	fi

	@# --------------------------------------------------------
	@# Push branch first (must succeed before tagging)
	@# --------------------------------------------------------
	@echo "📤 Pushing $(BRANCH)…"
	@git push origin "$(BRANCH)"

	@# --------------------------------------------------------
	@# Create and push tag
	@# --------------------------------------------------------
	@echo "🏷️ Creating $(TAG)…"
	@git tag -a "$(TAG)" -m "Release $(TAG)"

	@echo "📤 Pushing tag…"
	@git push origin "$(TAG)"

	@# --------------------------------------------------------
	@# Warn if GitHub Pages not configured (non-fatal)
	@# --------------------------------------------------------
	@gh api repos/{owner}/{repo}/pages >/dev/null 2>&1 || { \
		echo "⚠️  GitHub Pages not configured."; \
		echo "   Go to: Settings → Pages → set source to gh-pages branch."; \
	}

	@# --------------------------------------------------------
	@# Local install via pipx (external tools only)
	@# --------------------------------------------------------
	@if [ "$(IS_TOOL)" = "1" ] && [ "$(IS_EXTERNAL)" = "1" ]; then \
		WHEEL=$$(printf "%s\n" dist/*$(VERSION)*.whl 2>/dev/null | head -n 1); \
		if [ -z "$$WHEEL" ]; then \
			echo "❌ No wheel found in dist/"; \
			exit 1; \
		fi; \
		echo "📦 Installing via pipx…"; \
		pipx install --force "$$WHEEL" >/dev/null || { \
			echo "❌ pipx install failed"; exit 1; \
		}; \
	else \
		echo "ℹ️ Skipping pipx install"; \
	fi

	@echo "🎉 Local release complete for $(PROJECT_NAME) $(VERSION)"

# ------------------------------------------------------------
#  🌐 Publish docs to GitHub Pages (gh-pages branch)
# ------------------------------------------------------------

pub-docs:
	$(call ensure-venv-active)
	$(call ensure-correct-venv)
	@if [ "$(BRANCH)" != "main" ]; then \
		echo "❌ pub-docs only allowed from canonical branch (main)"; \
		exit 1; \
	fi
	@echo "🌐 Publishing documentation tools..."
	@for tool in $(DOCS_TOOLS); do \
		$(MAKE) docs-$$tool-publish; \
	done

# ------------------------------------------------------------
#  Publish to private package index (pfix)
# ------------------------------------------------------------

pub-pfix: release
	@echo "📦 Publishing to private index (pfix)…"
	@if command -v pfix >/dev/null 2>&1; then \
		pfix publish .; \
	else \
		echo "❌ pfix not available"; \
		exit 1; \
	fi

# ------------------------------------------------------------
#  🐍 Publish to PyPI
# ------------------------------------------------------------

pub-pypi: release
	@echo "🚀 Uploading $(PROJECT_NAME) $(VERSION) to PyPI…"
	twine upload dist/*
	@echo "📦 Uploaded to PyPI."

# ------------------------------------------------------------
#  🍺 Publish/update Homebrew tap (stub)
# ------------------------------------------------------------

pub-brew: release
	@echo "🍺 Updating Homebrew tap for $(PROJECT_NAME)…"
	@echo "TODO: Implement formula generation + commit/push to $(BREWREPO)"
	@echo "✔️ Brew publishing stub"

# ------------------------------------------------------------
#  🌍 Aggregate publish (outside this machine)
# ------------------------------------------------------------

publish: pub-pfix pub-pypi pub-brew
	@echo "🌍 Publish complete for $(PROJECT_NAME) $(VERSION)"

# ------------------------------------------------------------
#  Generate complete pdf of source code for physical backup
# ------------------------------------------------------------

CORPUS_PS := corpus.ps
CORPUS_PS2 := corpus2.ps
CORPUS_PDF := corpus.pdf

SOURCES := pyproject.toml Makefile $(shell find $(or $(PROJECT_NAME),.) -name "*.py" | sort)

corpus.pdf:
	enscript -2GrT4fCourier6 -C --file-align=1 --toc \
	-o $(CORPUS_PS) $(SOURCES)
	@pages=$$(grep -c '^%%Page:' $(CORPUS_PS)); \
	psselect $$pages,1-$$((pages-1)) $(CORPUS_PS) $(CORPUS_PS2)
	ps2pdf $(CORPUS_PS2) $(CORPUS_PDF)

corpus: corpus.pdf
