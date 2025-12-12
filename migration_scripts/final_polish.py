import os
import re
import glob

BASE_DIR = r"d:\Proyectos\Web\agustinaalvarez.com - auto"
BRANCHES = ["belgrano", "palermo", "nunez"]
NEIGHBORHOOD_MAP = {
    "belgrano": "Belgrano",
    "palermo": "Palermo",
    "nunez": "Núñez"
}

def clean_duplication(text, neighborhood):
    # Aggressive cleanup of "Belgrano (Belgrano (CABA))" patterns
    # 1. Collapse matches
    # Regex for "Name (Name...)" nested or not
    
    # Remove all (CABA) first to normalize
    temp = text.replace("(CABA)", "").replace("((", "(").replace("))", ")")
    
    # Remove repeated neighborhood
    # "Belgrano (Belgrano)" -> "Belgrano"
    pattern_dup = re.compile(fr"{neighborhood}\s*\({neighborhood}\)", re.IGNORECASE)
    while pattern_dup.search(temp):
        temp = pattern_dup.sub(neighborhood, temp)
        
    # "Belgrano Belgrano" -> "Belgrano"
    pattern_adj = re.compile(fr"{neighborhood}\s+{neighborhood}", re.IGNORECASE)
    while pattern_adj.search(temp):
        temp = pattern_adj.sub(neighborhood, temp)
        
    # Cleanup empty parens
    temp = temp.replace("()", "").strip()
    
    # Now ensure (CABA) is present if neighborhood is present and it is a Title/H1 context.
    # But for meta description we might just want to clean duplication, not force (CABA) on every mention.
    # We will let the caller decide on forcing (CABA).
    return temp

def fix_file(filepath, neighborhood):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    orig_content = content
    
    # 1. Enforce (CABA) in Title and H1 if "en {Neighborhood}" is found
    # Regex: en {Neighborhood}(?!\s*\(CABA\))
    # match case insensitive? Neighborhood usually capitalized.
    
    pattern_en = re.compile(fr"en {neighborhood}(?!\s*\(CABA\))", re.IGNORECASE)
    replacement = f"en {neighborhood} (CABA)"
    
    # Title
    def repl_title(m):
        inner = m.group(1)
        # First clean duplications
        inner = clean_duplication(inner, neighborhood)
        # Then apply force (CABA)
        inner = pattern_en.sub(replacement, inner)
        return f"<title>{inner}</title>"
        
    content = re.sub(r'<title>(.*?)</title>', repl_title, content, flags=re.DOTALL)
    
    # H1
    def repl_h1(m):
        inner = m.group(1)
        inner = clean_duplication(inner, neighborhood)
        inner = pattern_en.sub(replacement, inner)
        return f"<h1>{inner}</h1>"
        
    content = re.sub(r'<h1>(.*?)</h1>', repl_h1, content, flags=re.DOTALL)
    
    # Meta Description - Clean duplication ONLY
    # content="... Belgrano (Belgrano (CABA)) ..."
    def repl_meta(m):
        # m.group(0) is the whole tag.
        # We want to replace content="..."
        # parsing html with regex is brittle but efficient for this specific mess.
        tag = m.group(0)
        # Extract content attr
        c_match = re.search(r'content="(.*?)"', tag)
        if c_match:
            old_c = c_match.group(1)
            new_c = clean_duplication(old_c, neighborhood)
            # Reconstruct
            return tag.replace(old_c, new_c)
        return tag

    content = re.sub(r'<meta name="description" content=".*?"', repl_meta, content)
    
    if content != orig_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    count = 0
    for branch in BRANCHES:
        directory = os.path.join(BASE_DIR, branch)
        neighborhood = NEIGHBORHOOD_MAP[branch]
        print(f"Polishing {branch} ({neighborhood})...")
        files = glob.glob(os.path.join(directory, "*.html"))
        for filepath in files:
            if fix_file(filepath, neighborhood):
                print(f"Polished: {os.path.basename(filepath)}")
                count += 1
    print(f"Total polished: {count}")

if __name__ == "__main__":
    main()
