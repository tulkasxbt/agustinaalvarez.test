import os
import re
import json
import shutil
import random

# Configuration
PROJECT_ROOT = "d:/Proyectos/Web/agustinaalvarez.com - auto"
DRY_RUN = False
LOCATIONS = {
    "belgrano": {
        "name": "Belgrano",
        "full_name": "Belgrano (CABA)",
        "address": "Federico Lacroze 2306, Belgrano, CABA",
        "keywords_extra": "Belgrano, Belgrano CABA, Belgrano Buenos Aires",
        "intro_variations": [
            "En mi consultorio de Belgrano (CABA), ofrezco este tratamiento personalizado.",
            "Si estás en Belgrano y buscás resultados naturales, este tratamiento es ideal.",
            "Acercate a nuestro centro en Belgrano para una evaluación médica completa."
        ]
    },
    "palermo": {
        "name": "Palermo",
        "full_name": "Palermo (CABA)",
        "address": "Palermo, CABA", # Generic if no specific address given
        "keywords_extra": "Palermo, Palermo CABA, Palermo Buenos Aires",
        "intro_variations": [
            "Atendemos pacientes de Palermo buscando la mejor calidad médica.",
            "Si vivís o trabajás en Palermo, nuestro consultorio es tu mejor opción.",
            "Elegido por pacientes de Palermo por su seguridad y resultados naturales."
        ]
    },
    "nunez": {
        "name": "Núñez",
        "full_name": "Núñez (CABA)",
        "address": "Núñez, CABA",
        "keywords_extra": "Núñez, Núñez CABA, Núñez Buenos Aires",
        "intro_variations": [
            "Para pacientes de Núñez que valoran la estética médica responsable.",
            "Muy cerca de Núñez, brindamos tratamientos de última generación.",
            "Tu opción de confianza en la zona de Núñez para tratamientos faciales."
        ]
    }
}

TARGET_FILES = [
    "alquimia.html", "botox.html", "celulitis_corporal.html", "depilacion.html",
    "enzimas_pbserum.html", "erbium.html", "flacidez_corporal.html", "labios.html",
    "laser_qswitch.html", "longlasting.html", "luz_pulsada.html", "mesoterapia.html",
    "mesoterapia_filorga.html", "modelado_corporal.html", "pbserum_corporal.html",
    "peeling.html", "plasma.html", "profhilo.html", "radiesse.html", 
    "radiesse_corporal.html", "radiofrecuencia.html", "rellenos.html", 
    "sculptra.html", "sculptra_corporal.html", "skinbooster.html", 
    "tratamiento_capilar.html", "tratamientos_corporales.html"
]

def localize_content(content, filename, loc_key, loc_data):
    # 1. Path Adjustments (Going one level deep)
    # data/ -> ../data/
    # images/ -> ../images/
    # css/ -> ../css/
    # js/ -> ../js/
    # assets/ -> ../assets/
    # fonts/ -> ../fonts/
    # favicon -> ../images/favicon
    
    # Generic relative path fix for standard folders
    for folder in ["data", "images", "imagenes", "css", "js", "assets", "fonts", "phpmailer"]:
        # Match src="folder/..." or href="folder/..." or url('folder/...') or "folder/file.json"
        
        # Regex explanation:
        # (?<=["'\(]) checks for quote or paren before (lookbehind)
        # folder + / matches the folder start
        # strict replacing might be safer:
        # We want to replace "folder/" with "../folder/" ONLY if it's not already absolute or relative.
        # But commonly in this project they are "images/logo.png".
        
        # Simple replace strategy can work if we are careful not to double headers.
        # content = content.replace(f'"{folder}/', f'"../{folder}/')
        # content = content.replace(f"'{folder}/", f"'../{folder}/")
        
        # Using regex to capture boundary
        def replace_path(match):
            return f"{match.group(1)}../{folder}/"
            
        content = re.sub(f'([\"\']){folder}/', replace_path, content)
        content = re.sub(f'(\(){folder}/', replace_path, content) # url(images/...)

    # Fix specific links to global pages (index.html, contacto.html, etc.)
    # Links to other treatments stay relative (e.g. href="botox.html") because we are copying them all.
    # Links to "tratamientos.html", "afecciones.html", "faqs.html", "contacto.html", "index.html", "blog/" need ../
    GLOBAL_PAGES = ["index.html", "contacto.html", "faqs.html", "afecciones.html", "tratamientos.html", "tratamientos_corporales.html", "depilacion.html"]
    # Wait, "tratamientos.html" etc. are in the list? No, "tratamientos.html" is a summary page.
    # If "tratamientos.html" is NOT in TARGET_FILES (it is not in the list I have), then we should link to "../tratamientos.html".
    # However, "tratamientos_corporales.html" IS in TARGET_FILES. So links to it should stay relative "tratamientos_corporales.html".
    # Let's verify which are targets.
    
    TARGET_SET = set(TARGET_FILES)
    
    def update_links(match):
        quote = match.group(1)
        link = match.group(2)
        if link.startswith("http") or link.startswith("#") or link.startswith("mailto:") or link.startswith("tel:") or link.startswith("javascript:"):
            return match.group(0)
        
        if link in TARGET_SET:
            return match.group(0) # Keep relative link to other localized page
        
        # Else it's a global page or unknown
        return f'href={quote}../{link}{quote}'

    # Only target hrefs
    content = re.sub(r'href=([\"\'])(.*?)([\"\'])', update_links, content)
    
    # 2. Variable Replacement (Buenos Aires -> Location)
    # Strategy: Replace "Buenos Aires (CABA)" or "Buenos Aires" with "Neighborhood (CABA)" matchingly.
    # We must be careful not to break the address in footer if we want to keep it "Federico Lacroze..." 
    # But usually we want to emphasize the location.
    
    name = loc_data["name"] # Belgrano
    full_name = loc_data["full_name"] # Belgrano (CABA)
    
    # Replace general "Buenos Aires (CABA)" -> "Location (CABA)"
    content = content.replace("Buenos Aires (CABA)", full_name)
    content = content.replace("Buenos Aires", name) # Simple fallback
    content = content.replace("CABA", full_name) # Ensure CABA mentions get the neighborhood context? debatable.
    # actually "CABA" -> "Núñez (CABA)" might be repetitve "Núñez (Núñez (CABA))" if CABA was part of full name.
    # Let's rely on specific replacements first.
    
    # Replace Titles
    # <title>... Buenos Aires ...</title> -> <title>... Belgrano ...</title>
    
    # Update H1
    content = re.sub(r"<h1>(.*?)</h1>", lambda m: f"<h1>{m.group(1).replace('Buenos Aires', name).replace('CABA', name)}</h1>", content)
    
    # 3. Content Variation (Intro insertion)
    # Find the first paragraph after H1 or first <p> in main container.
    # We'll just prepend a paragraph to the first text section.
    intro = random.choice(loc_data["intro_variations"])
    intro_html = f'<p style="font-size: 16px; line-height: 1.6; font-weight: bold; color: #555;">📍 {intro}</p>'
    
    # Insert after first H2 match or similar?
    # Or replace the first <p after H1.
    def inject_intro(match):
        return f"{match.group(0)}\n    {intro_html}"
    
    content = re.sub(r'</h1>', inject_intro, content, count=1)

    # 4. SEO Metadata
    def update_meta_desc(match):
        return match.group(0).replace("Buenos Aires", name).replace("CABA", full_name)
    content = re.sub(r'<meta name="description".*?>', update_meta_desc, content)
    
    # 5. Canonical
    # <link rel="canonical" href="https://agustinaalvarez.com/botox.html">
    # -> https://agustinaalvarez.com/belgrano/botox.html
    new_canonical = f"https://agustinaalvarez.com/{loc_key}/{filename}"
    
    # Robust Replace
    if 'rel="canonical"' in content:
        content = re.sub(r'<link rel="canonical" href=".*?"\s*/?>', f'<link rel="canonical" href="{new_canonical}">', content)
        # Also catch non-closed version just in case
        content = re.sub(r'<link rel="canonical" href=".*?">', f'<link rel="canonical" href="{new_canonical}">', content)
    else:
        # Fallback: Insert in head
        content = content.replace("</head>", f'<link rel="canonical" href="{new_canonical}">\n</head>')
    
    # 6. Hreflang Removal
    # Remove single lines with hreflang
    content = re.sub(r'<link rel="alternate" hreflang="es" href=".*?"\s*/?>\s*', '', content)
    content = re.sub(r'<link rel="alternate" hreflang="en" href=".*?"\s*/?>\s*', '', content)
    
    # Fallback for standard syntax without slash
    content = re.sub(r'<link rel="alternate" hreflang="es" href=".*?">\s*', '', content)
    content = re.sub(r'<link rel="alternate" hreflang="en" href=".*?">\s*', '', content)
    
    # 7. JSON-LD Update
    # areaServed -> Neighborhood
    # "addressLocality": "Buenos Aires" -> "Buenos Aires" (Keep city)
    # But maybe add "addressLocality": "Belgrano, Buenos Aires"?
    # Prompt says: "areaServed -> mencionar 'Belgrano (CABA)'"
    
    # We will use regex substitution on "metrics" we know.
    # "areaServed": { "@type": "Place", "name": "Ciudad de Buenos Aires" }
    # -> "name": "Belgrano (CABA)"
    
    content = content.replace('"name": "Ciudad de Buenos Aires"', f'"name": "{full_name}"')
    content = content.replace('"areaServed": "Ciudad de Buenos Aires"', f'"areaServed": "{full_name}"')
    
    # 8. Logo Link Fix
    # Fix logo link to point to root index
    # <a href="https://agustinaalvarez.com"> or <a href="../index.html">
    # If it is absolute https://agustinaalvarez.com, we can leave it or make it absolute /belgrano/?
    # Prompt says: "Si un enlace apunta a la home principal... podés mantenerlo apuntando a la raíz"
    # But for user experience in silo, usually logo goes to silo home? 
    # But we don't have a specific silo home (e.g. index.html inside belgrano).
    # So logo should go to global home.
    # My link updater handles relative links. Absolute links are ignored.
    # If the logo href is absolute, it stays absolute (Global Home).

    return content

def main():
    print(f"Starting Localization... Dry Run: {DRY_RUN}")
    
    for loc_key, loc_data in LOCATIONS.items():
        # Create dir if not exists (already done by earlier step but good to be safe)
        loc_dir = os.path.join(PROJECT_ROOT, loc_key)
        if not os.path.exists(loc_dir):
            os.makedirs(loc_dir)
            
        for filename in TARGET_FILES:
            src_path = os.path.join(PROJECT_ROOT, filename)
            dst_path = os.path.join(loc_dir, filename)
            
            if not os.path.exists(src_path):
                print(f"Warning: Source {filename} not found.")
                continue
                
            with open(src_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            new_content = localize_content(content, filename, loc_key, loc_data)
            
            if DRY_RUN:
                # print(f"Would write {dst_path}")
                pass
            else:
                with open(dst_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Created {dst_path}")

if __name__ == "__main__":
    main()
