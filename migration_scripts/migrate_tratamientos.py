import os
import re

SOURCE_FILE = r"d:\Proyectos\Web\agustinaalvarez.com - auto\tratamientos.html"
BASE_DIR = r"d:\Proyectos\Web\agustinaalvarez.com - auto"

BRANCHES = {
    "belgrano": {"name": "Belgrano", "h1": "Tratamientos en Belgrano (CABA)", "title": "Tratamientos Faciales en Belgrano (CABA) | Agustina Alvarez"},
    "palermo": {"name": "Palermo", "h1": "Tratamientos en Palermo (CABA)", "title": "Tratamientos Faciales en Palermo (CABA) | Agustina Alvarez"},
    "nunez": {"name": "Núñez", "h1": "Tratamientos en Núñez (CABA)", "title": "Tratamientos Faciales en Núñez (CABA) | Agustina Alvarez"}
}

def migrate():
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Generic Path Fixes
    # CSS/JS/Assets/Images
    content = content.replace('href="assets/', 'href="../assets/')
    content = content.replace('href="css/', 'href="../css/')
    content = content.replace('src="images/', 'src="../images/')
    content = content.replace('href="/images/', 'href="../images/') # Favicon
    content = content.replace("url('images/", "url('../images/") # Inline styles

    # JSON Data
    content = content.replace("fetch('/data/", "fetch('../data/")
    content = content.replace("fetch('./data/", "fetch('../data/") # just in case

    # Global Links (Nav)
    content = content.replace('href="https://agustinaalvarez.com/"', 'href="../index.html"')
    content = content.replace('href="https://agustinaalvarez.com"', 'href="../index.html"') # Catch w/o slash
    content = content.replace('href="afecciones.html"', 'href="../afecciones.html"')
    content = content.replace('href="faqs.html"', 'href="../faqs.html"')
    content = content.replace('href="contacto.html"', 'href="../contacto.html"')
    # Blog - leave absolute if it was absolute, but code has 'https://agustinaalvarez.com/blog/' -> keep it.

    # 2. Branch Specifics
    for branch_slug, branch_data in BRANCHES.items():
        print(f"Processing {branch_slug}...")
        branch_content = content
        
        # Remove Hreflangs
        branch_content = re.sub(r'<link rel="alternate" hreflang=".*?" href=".*?" />\s*', '', branch_content)
        
        # Update Canonical
        branch_content = re.sub(
            r'<link rel="canonical" href=".*?" />',
            f'<link rel="canonical" href="https://agustinaalvarez.com/{branch_slug}/tratamientos.html" />',
            branch_content
        )

        # Update Title
        # Regex to capture the title tag content
        branch_content = re.sub(
            r'<title>.*?</title>',
            f'<title>{branch_data["title"]}</title>',
            branch_content
        )

        # Update H1
        # It usually is <h1>Tratamientos en Belgrano</h1>
        # We replace the inner text.
        branch_content = re.sub(
            r'<h1>.*?</h1>',
            f'<h1>{branch_data["h1"]}</h1>',
            branch_content
        )

        # Content Text Replacement (Naive approach for now, "Belgrano" -> "Neighborhood")
        # BUT we must be careful not to break "Tratamientos Faciales en Belgrano" if it was already replaced by title regex.
        # Actually, the user wants us to fix the root content later. 
        # For the branch files, we need to replace "Belgrano" with the new neighborhood in the descriptions if present.
        # The source file ALREADY HAS "Belgrano" in text.
        
        # Let's replace "Belgrano" with branch name in the body text ONLY IF it's not Belgrano branch (or even if it is, to standardize).
        # We need to be careful with URLs.
        # We already adjusted paths. All internal links to treatments (botox.html) are local.
        
        if branch_slug != "belgrano":
            # Replace "Belgrano" in text
            branch_content = branch_content.replace("Belgrano", branch_data["name"])

        # Special check for "Capital Federal, Buenos Aires" in footer -> maybe change? User didn't specify footer change but "Raíz: Buenos Aires / CABA".
        # Leave footer for now.

        # FIX 4.1: Check links to hubs
        # "tratamientos.html" is already correct (same dir)
        # "tratamientos_corporales.html" is already correct (same dir)
        # Ensure they don't have ../ unless intended. In original they effectively link to current dir.
        # Original: href="tratamientos.html" -> In branch/tratamientos.html, this links to branch/tratamientos.html. CORRECT.
        
        # Write file
        target_path = os.path.join(BASE_DIR, branch_slug, "tratamientos.html")
        with open(target_path, 'w', encoding='utf-8') as f_out:
            f_out.write(branch_content)
            
        print(f"Written: {target_path}")

if __name__ == "__main__":
    migrate()
