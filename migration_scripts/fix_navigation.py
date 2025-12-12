import os
import re
import glob

BASE_DIR = r"d:\Proyectos\Web\agustinaalvarez.com - auto"
BRANCHES = ["belgrano", "palermo", "nunez"]

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    orig_content = content
    
    # 1. Tratamientos Faciales Hub
    # Goal: href="tratamientos.html"
    # Replace absolute or root-relative occurrences
    content = content.replace('href="https://agustinaalvarez.com/tratamientos.html"', 'href="tratamientos.html"')
    content = content.replace('href="/tratamientos.html"', 'href="tratamientos.html"')
    content = content.replace('href="../tratamientos.html"', 'href="tratamientos.html"')
    
    # 2. Tratamientos Corporales Hub
    # Goal: href="tratamientos_corporales.html"
    content = content.replace('href="https://agustinaalvarez.com/tratamientos_corporales.html"', 'href="tratamientos_corporales.html"')
    content = content.replace('href="/tratamientos_corporales.html"', 'href="tratamientos_corporales.html"')
    content = content.replace('href="../tratamientos_corporales.html"', 'href="tratamientos_corporales.html"')
    
    if content != orig_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    modified_count = 0
    for branch in BRANCHES:
        directory = os.path.join(BASE_DIR, branch)
        print(f"Scanning {directory}...")
        files = glob.glob(os.path.join(directory, "*.html"))
        for filepath in files:
            if fix_file(filepath):
                print(f"Fixed navigation in: {os.path.basename(filepath)}")
                modified_count += 1
                
    print(f"Total files adjusted for navigation: {modified_count}")

if __name__ == "__main__":
    main()
