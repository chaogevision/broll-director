#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
TARGET_DIR="$CODEX_HOME_DIR/skills/personal-talking-head-visual-director"

mkdir -p "$(dirname "$TARGET_DIR")"
if [ -e "$TARGET_DIR" ]; then
  BACKUP="$TARGET_DIR.backup.$(date +%Y%m%d-%H%M%S)"
  mv "$TARGET_DIR" "$BACKUP"
  echo "Existing skill moved to: $BACKUP"
fi
cp -R "$SOURCE_DIR" "$TARGET_DIR"
echo "Installed to: $TARGET_DIR"
echo "Restart Codex before using the skill."
