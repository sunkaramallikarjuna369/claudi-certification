# Fix UTF-8 encoding for all Python files in agentic_architecture
# Run this to fix emoji encoding issues on Windows

import os


def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add UTF-8 fix at the beginning of __main__ blocks
    fix = '''import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

'''

    if 'if __name__ == "__main__":' in content and 'sys.stdout = io.TextIOWrapper' not in content:
        idx = content.find('if __name__ == "__main__":')
        newline_idx = content.find('\n', idx)
        content = content[:newline_idx+1] + fix + content[newline_idx+1:]

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {filepath}")


# Find all Python files
for root, dirs, files in os.walk('agentic_architecture'):
    for file in files:
        if file.endswith('.py'):
            fix_file(os.path.join(root, file))

print("\nDone fixing UTF-8 encoding!")