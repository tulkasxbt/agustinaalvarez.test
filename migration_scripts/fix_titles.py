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

def clean_text(text, neighborhood):
    """
    Normalizes text to ensure format: "... en {Neighborhood} (CABA)"
    Removes recursive neighborhood mentions like "Belgrano (Belgrano (CABA))"
    """
    # 1. Remove all "(CABA)" temporarily to simplify
    text = text.replace("(CABA)", "")
    
    # 2. Collapse recursive patterns like "Belgrano (Belgrano)" -> "Belgrano"
    # We loop until no changes are made to handle N levels of nesting if any
    prev_text = ""
    while text != prev_text:
        prev_text = text
        # Remove parenthesized neighborhood: "Belgrano (Belgrano)"
        text = re.sub(f"{neighborhood}\s*\({neighborhood}\)", neighborhood, text, flags=re.IGNORECASE)
        # Remove repeated neighborhood: "Belgrano Belgrano"
        text = re.sub(f"{neighborhood}\s+{neighborhood}", neighborhood, text, flags=re.IGNORECASE)
        # Remove parentheses around the neighborhood if it stands alone or has issues: "(Belgrano)"
        text = re.sub(f"\({neighborhood}\)", neighborhood, text, flags=re.IGNORECASE)

    # 3. Ensure proper format
    # We want "{Neighborhood} (CABA)"
    # If the text ALREADY contains "{Neighborhood}", allow it, and append "(CABA)" if not present.
    # But wait, we might have multiple occurrences.
    # User said: "Si contiene múltiples repeticiones, colapsar a una sola mención."
    
    # Let's rebuild the specific string we want.
    # If we find the neighborhood, we ensure it's followed by (CABA).
    # But we don't want to replace "Tratamientos Faciales en Belgrano" with "Tratamientos Faciales en Belgrano (CABA) (CABA)".
    
    # Regex to find "{Neighborhood}" followed optionally by other stuff, and normalize it.
    # It's safer to just replace all occurrences of "{Neighborhood}" with a placeholder, then put it back once?
    # No, that might ruin sentences like "Visit Belgrano. Belgrano is nice."
    
    # Let's target the exact patterns the user mentioned: "{BARRIO} ({BARRIO})"
    # We already did that with the while loop above.
    
    # Now verify the (CABA) suffix.
    # We want "Belgrano (CABA)".
    # If we have "Belgrano", replace with "Belgrano (CABA)". 
    # BUT check if it's already "Belgrano (CABA)".
    
    if neighborhood not in text:
        # If neighborhood is missing, we might leave it or warn?
        # User implies we should have it. Assuming it's there or we should add it.
        # But this function is for cleaning existing titles.
        return text 

    # Clean up trailing spaces
    text = text.strip()
    
    # Simply replace the first occurrence of neighborhood with "##PLACEHOLDER##"
    # then remove all other occurrences? No, that's risky.
    
    # Let's try a regex for the specific "Title H1" style strings.
    # Usually: "Tratamiento X en Belgrano" or "Belgrano"
    
    # Replace "Belgrano" with "Belgrano (CABA)" IF not followed by (CABA)
    pattern = re.compile(f"{neighborhood}(?!\s*\(CABA\))", re.IGNORECASE)
    # This matches "Belgrano" not followed by "(CABA)".
    # Replace it with "Belgrano (CABA)"
    text = pattern.sub(f"{neighborhood} (CABA)", text)
    
    # Now we might have "Belgrano (CABA) (CABA)" if my previous logic was flawed, but the regex lookahead prevents that.
    # Wait, what if we have "Belgrano (Belgrano)"?
    # The while loop cleared that to "Belgrano".
    # Then the regex makes it "Belgrano (CABA)".
    
    # What if we have "Belgrano (CABA)" already?
    # The loop sees "Belgrano" ignoring (CABA) because we stripped (CABA) at step 1?
    # YES. Step 1 removed (CABA). So "Belgrano (CABA)" became "Belgrano ()".
    # That is bad. "()" should be cleaned.
    text = text.replace("()", "").strip() 
    
    # Let's refine Step 1:
    # Instead of strip (CABA), just fix the duplication first.
    
    return text

def advanced_clean(text, neighborhood):
    # Strategy: 
    # 1. Simplify: Replace common messy patterns with just the Name.
    # Pattern: Name (Name ...) 
    cleaned = text
    
    # Regex for "Name (Name...)" nested or not
    # e.g. "Belgrano (Belgrano (CABA))" -> "Belgrano (CABA)"
    # User said: "format final permitido: ... en Belgrano (CABA)"
    
    # Let's try to just find the neighborhood mentions.
    # If found, check what's around it.
    
    # Case 1: "Belgrano (Belgrano)" -> "Belgrano"
    cleaned = re.sub(f"{neighborhood}\s*\({neighborhood}\s*(\(CABA\))?\)", f"{neighborhood}", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(f"{neighborhood}\s*\({neighborhood}\s*\)", f"{neighborhood}", cleaned, flags=re.IGNORECASE)
    
    # Case 2: "Belgrano (CABA)" -> keep or normalize.
    # If we have "Belgrano (CABA)", we want to ensure we don't duplicate.
    
    # Let's handle the specific user complaints first.
    # "Belgrano (Belgrano (CABA))"
    # "Palermo (Palermo)"
    
    # We can replace the whole messy block with "Belgrano (CABA)".
    # Messy block = Neighborhood followed by parens containing Neighborhood or CABA.
    
    pattern_messy = re.compile(fr"{neighborhood}\s*\((?:{neighborhood}|CABA|Buenos Aires|Capital Federal).*\)", re.IGNORECASE)
    # This is aggressive. Be careful.
    
    # Let's use the USER's specific normalizations:
    # {BARRIO} ({BARRIO}) -> {BARRIO} (CABA)
    # {BARRIO} ({BARRIO} (CABA)) -> {BARRIO} (CABA)
    
    regexs = [
        (fr"{neighborhood}\s*\({neighborhood}\s*\(CABA\)\)", f"{neighborhood} (CABA)"),
        (fr"{neighborhood}\s*\({neighborhood}\)", f"{neighborhood} (CABA)"),
        (fr"{neighborhood}\s*\(CABA\)", f"{neighborhood} (CABA)"), # Normalize spacing
        (fr"{neighborhood}\s*\({neighborhood}\s*\({neighborhood}\)\)", f"{neighborhood} (CABA)"),
    ]
    
    for pat, repl in regexs:
        cleaned = re.sub(pat, repl, cleaned, flags=re.IGNORECASE)
        
    # Final check: Ensure (CABA) is present if neighborhood is present?
    # Or just replace stand-alone "Belgrano" at the end of string?
    # Many titles end with " en Belgrano".
    
    # If it ends with " en Belgrano", make it " en Belgrano (CABA)".
    cleaned = re.sub(fr" en {neighborhood}$", f" en {neighborhood} (CABA)", cleaned, flags=re.IGNORECASE)
    
    # If it is JUST "Belgrano", make it "Belgrano (CABA)".
    if cleaned.strip().lower() == neighborhood.lower():
        cleaned = f"{neighborhood} (CABA)"
        
    # Check for double (CABA) (CABA)
    cleaned = cleaned.replace("(CABA) (CABA)", "(CABA)")
    
    return cleaned

def process_file(filepath, neighborhood):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    orig_content = content
    
    # Regex for Title
    def replace_title(match):
        return f"<title>{advanced_clean(match.group(1), neighborhood)}</title>"
    
    content = re.sub(r'<title>(.*?)</title>', replace_title, content, flags=re.DOTALL)
    
    # Regex for H1
    def replace_h1(match):
        return f"<h1>{advanced_clean(match.group(1), neighborhood)}</h1>"
    
    content = re.sub(r'<h1>(.*?)</h1>', replace_h1, content, flags=re.DOTALL)

    if content != orig_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    modified_count = 0
    for branch in BRANCHES:
        directory = os.path.join(BASE_DIR, branch)
        neighborhood = NEIGHBORHOOD_MAP[branch]
        print(f"Scanning {directory} for {neighborhood}...")
        
        files = glob.glob(os.path.join(directory, "*.html"))
        for filepath in files:
            if process_file(filepath, neighborhood):
                print(f"Fixed: {os.path.basename(filepath)}")
                modified_count += 1
                
    print(f"Total files modified: {modified_count}")

if __name__ == "__main__":
    main()
