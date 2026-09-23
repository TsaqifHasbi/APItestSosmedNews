import sys

file_path = 'c:\\Users\\Asus\\OneDrive\\Documents\\Project_Streamlit\\cobaAPI\\dashboard\\poc\\app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_else = False

for i, line in enumerate(lines):
    if line.startswith("    else:"):
        new_lines.append(line)
        in_else = True
        continue
        
    if in_else:
        if line.strip() == "":
            new_lines.append(line)
        elif line.startswith("    ") and not line.startswith("        ") and i > 525:
            # We need to indent exactly 4 more spaces to everything that was at 1 level of indent
            # But wait, it's safer to just indent EVERYTHING after "else:" that has at least 4 spaces, by adding 4 more spaces.
            # However, the scope of the `else` should be until the end of the `with tab9:` block!
            # The `with tab9:` block ends at the end of the file or when another top-level `with` happens.
            # Actually, `app.py` ends at line 741. Is everything until EOF inside `with tab9:`? Let's assume yes because it's the last tab.
            if len(line) - len(line.lstrip()) >= 4:
                new_lines.append("    " + line)
            else:
                new_lines.append(line)
                in_else = False # exited the with tab9 block
        else:
            if len(line) - len(line.lstrip()) >= 4:
                new_lines.append("    " + line)
            else:
                new_lines.append(line)
    else:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Indentation fixed.")
