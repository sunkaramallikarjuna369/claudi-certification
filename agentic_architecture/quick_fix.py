# Quick fix for __main__ blocks in all Python files

import os
import re


def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'(if __name__ == "__main__":)\n(\s*import sys\n.*?\n)(\S)'

    def fix_match(m):
        if_block = m.group(1)
        indented_lines = m.group(2)
        next_line = m.group(3)

        lines = indented_lines.split('\n')
        fixed_lines = []
        for line in lines:
            if line.strip():
                if not line.startswith('    '):
                    fixed_lines.append('    ' + line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        return if_block + '\n' + '\n'.join(fixed_lines) + '\n'

    new_content = re.sub(pattern, fix_match, content, flags=re.DOTALL)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


# Apply to all Python files
for root, dirs, files in os.walk('agentic_architecture'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                if fix_file(filepath):
                    print(f'Fixed: {filepath}')
            except Exception as e:
                print(f'Error in {filepath}: {e}')

print('\nDone!')