#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SITE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$SITE_ROOT/_site"
LOCAL_BASE_URL="${SITE_BASE_URL:-http://localhost:4000}"

if [[ "$BUILD_DIR" != "$SITE_ROOT/_site" ]]; then
    echo "Refusing to clean unexpected build directory: $BUILD_DIR" >&2
    exit 1
fi

# Build from checked-in files, matching what exists in a clean GitHub Actions
# checkout. This deliberately avoids publishing unrelated untracked files that
# happen to live beside the site locally.
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

while IFS= read -r -d '' relative_path; do
    case "$relative_path" in
        .github/* | blog/* | deploy/* | _site/*)
            continue
            ;;
    esac

    source_path="$SITE_ROOT/$relative_path"
    [[ -f "$source_path" ]] || continue

    destination_path="$BUILD_DIR/$relative_path"
    mkdir -p "$(dirname "$destination_path")"
    cp "$source_path" "$destination_path"
done < <(git -C "$SITE_ROOT" ls-files -z)

# Root HTML pages and project media are public source paths. Overlay them from
# the working tree so newly created pages/assets appear in local previews before
# they are staged, without copying unrelated local documents into _site.
for html_source in "$SITE_ROOT"/*.html; do
    [[ -f "$html_source" ]] || continue
    cp "$html_source" "$BUILD_DIR/"
done

if [[ -d "$SITE_ROOT/project-assets" ]]; then
    cp -R "$SITE_ROOT/project-assets" "$BUILD_DIR/"
fi

# The blog is a separate Hugo site published beneath /blog/. Override its
# production base URL so styles, navigation, and post links remain local.
hugo \
    --source "$SITE_ROOT/blog" \
    --destination "$BUILD_DIR/blog" \
    --baseURL "${LOCAL_BASE_URL%/}/blog/"
touch "$BUILD_DIR/.nojekyll"

echo "Built full site at $BUILD_DIR"
