# docs/pfig/Makefile

PROJECT_ROOT        := $(abspath ../..)
DOCS_ROOT           := $(CURDIR)
BUILD_ROOT          := $(DOCS_ROOT)/_build
DIST_ROOT           := $(PROJECT_ROOT)/pfig_dist
SENTINEL            := pfig :: documentation rendered from source.

.PHONY: all readme sphinx sync publish publish-readme clean dist


# ------------------------------------------------------------
# Default build
# ------------------------------------------------------------

all: readme


# ------------------------------------------------------------
# Documentation backends (compile only)
# ------------------------------------------------------------

readme:
	@echo "📘 Building README documentation..."
	@cd $(PROJECT_ROOT) && \
		pfig docs --force readme

sphinx:
	@echo "📘 Building Sphinx documentation (pfig projection)..."
	@cd $(PROJECT_ROOT) && \
		pfig docs --force sphinx


# ------------------------------------------------------------
# Sync repository artifacts (in-repo only)
# ------------------------------------------------------------

sync:
	@echo "📝 Publishing README.md to project root..."

	@if [ ! -f "$(BUILD_ROOT)/readme/README.md" ]; then \
		echo "❌ Missing compiled README"; exit 1; \
	fi

	@# ---- Guard overwrite
	@if [ -f "$(PROJECT_ROOT)/README.md" ]; then \
		if ! grep -q "$(SENTINEL)" "$(PROJECT_ROOT)/README.md"; then \
			echo "❌ Refusing to overwrite handwritten README.md"; \
			echo "   This file was not rendered by pfig."; \
			echo "   Remove it manually or use FORCE_README=1."; \
			exit 1; \
		fi \
	fi

	@cp -f $(BUILD_ROOT)/readme/README.md $(PROJECT_ROOT)/README.md
	@echo "✔ README.md updated."
	@echo "ℹ️  Repo in sync for pfig docs."

# ------------------------------------------------------------
# Publish (external promotion)
# ------------------------------------------------------------

publish:
	@echo "ℹ️  No external publish step for pfig docs."


# ------------------------------------------------------------
# Clean build artifacts
# ------------------------------------------------------------

clean:
	@echo "🧹 Cleaning pfig documentation build artifacts..."
	rm -rf $(BUILD_ROOT)

