#!/usr/bin/env python3
"""
Convert multi-line jsonify() responses to single-line format.
"""
import re
import sys
from pathlib import Path

def convert_jsonify_to_single_line(content):
    """Convert multi-line jsonify() calls to single line."""
    
    # Pattern to match return jsonify({ ... })
    pattern = r'return jsonify\(\{([^}]+(?:\{[^}]*\}[^}]*)*)\}\)'
    
    def compress_dict(match):
        dict_content = match.group(1)
        # Remove newlines and extra spaces
        compressed = re.sub(r'\s+', ' ', dict_content.strip())
        return f'return jsonify({{{compressed}}})'
    
    # More robust approach: find all return jsonify patterns
    lines = content.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line starts a multi-line jsonify
        if 'return jsonify({' in line and not line.strip().endswith('})'):
            # Collect all lines until we find the closing })
            jsonify_lines = [line]
            i += 1
            brace_count = line.count('{') - line.count('}')
            
            while i < len(lines) and brace_count > 0:
                jsonify_lines.append(lines[i])
                brace_count += lines[i].count('{') - lines[i].count('}')
                i += 1
            
            # Combine into single line
            full_text = ' '.join(jsonify_lines)
            # Clean up whitespace
            full_text = re.sub(r'\s+', ' ', full_text)
            full_text = full_text.replace('{ ', '{').replace(' }', '}').replace(' ,', ',')
            
            # Get the indentation from the first line
            indent = len(jsonify_lines[0]) - len(jsonify_lines[0].lstrip())
            result.append(' ' * indent + full_text.strip())
        else:
            result.append(line)
            i += 1
    
    return '\n'.join(result)

def main():
    route_files = [
        'backend/routes/auth.py',
        'backend/routes/admin.py',
        'backend/routes/doctor.py',
        'backend/routes/patient.py',
    ]
    
    for file_path in route_files:
        path = Path(file_path)
        if not path.exists():
            print(f"Skipping {file_path} - not found")
            continue
        
        print(f"Processing {file_path}...")
        content = path.read_text()
        converted = convert_jsonify_to_single_line(content)
        
        # Backup original
        backup_path = path.with_suffix('.py.bak')
        path.rename(backup_path)
        
        # Write converted
        path.write_text(converted)
        print(f"  ✓ Converted and saved (backup: {backup_path})")

if __name__ == '__main__':
    main()
