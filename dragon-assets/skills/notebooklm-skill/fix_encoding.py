#!/usr/bin/env python3
"""Quick fix for emoji encoding issues in notebooklm-skill scripts"""
import os
import re

emoji_replacements = {
    '✅': '[OK]',
    '❌': '[X]',
    '⚠️': '[!]',
    '⏳': '...',
    '⏱️': '[Time]',
    'ℹ️': '[Info]',
    '📚': '[Library]',
    '🔍': '[Search]',
    '📝': '[Note]',
    '🗑️': '[Delete]',
    '📊': '[Stats]',
    '🌐': '[Web]',
    '🚀': '[Rocket]',
    '💡': '[Idea]',
    '📦': '[Package]',
    '🔧': '[Tool]',
    '📁': '[Folder]',
    '🎯': '[Target]',
    '✨': '[Star]',
    '💬': '[Chat]',
    '📢': '[Announce]',
    '🔐': '[Lock]',
    '🔴': '[Red]',
    '🔄': '[Refresh]',
    '🔑': '[Key]',
    '⭐': '[Star]',
    '💾': '[Save]',
}

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    for emoji, replacement in emoji_replacements.items():
        content = content.replace(emoji, replacement)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {filepath}")
        return True
    return False

scripts_dir = r"C:\Users\li\.claude\skills\notebooklm-skill\scripts"
fixed_count = 0

for filename in os.listdir(scripts_dir):
    if filename.endswith('.py'):
        filepath = os.path.join(scripts_dir, filename)
        if fix_file(filepath):
            fixed_count += 1

print(f"\nTotal files fixed: {fixed_count}")
