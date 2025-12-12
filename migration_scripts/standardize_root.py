import os
import re
import json

# Configuration
PROJECT_ROOT = "d:/Proyectos/Web/agustinaalvarez.com - auto"
DRY_RUN = False  # Set to False to actually write files

# Target files list (from implementation plan)
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

# Replacement Logic
REPLACEMENTS = [
    # Título específico
    (r"en mi consultorio de Belgrano", "en mi consultorio en Buenos Aires (CABA)"),
    (r"en Belgrano", "en CABA (Ciudad de Buenos Aires)"),
    # General "Belgrano" in metadata/titles only?
    # Use careful regex to avoid breaking addresses in footer/contact unless intended.
    # The prompt says: "Siempre que aparezca Belgrano en título, H1, subtítulos, párrafos, metadescripción, etc."
    # We will be careful about not replacing the actual address "Belgrano" in the footer if it's the physical location.
    # But for "Root" version, we want "Buenos Aires / CABA" focus.
]

LANGUAGE_REDIRECT_SCRIPT = """<script>
(function () {
  try {
    var lang = (navigator.language || navigator.userLanguage || "").toLowerCase();
    if (!lang || lang.indexOf("en") !== 0) return;

    var path = window.location.pathname || "";
    if (path.indexOf("/en/") === 0) return;

    var parts = path.split("/");
    var last = parts.pop() || parts.pop(); // maneja posible trailing slash

    if (!last || last.indexOf(".html") === -1) return;

    window.location.href = "/en/" + last;
  } catch (e) {
    // Fallback silencioso: nunca romper la página por este script
  }
})();
</script>"""

def update_content(content, filename):
    original_content = content
    
    # 1. Text Replacements
    # Strategy: Replace "Belgrano" with "Buenos Aires" in specific contexts like titles, headings, descriptions.
    # Avoid replacing "Federico Lacroze 2306, Belgrano" in the footer address if we want to keep the physical address accurate.
    # However, prompt says: "No cambies el NAP real... salvo que haya direcciones explícitas de barrio: convertí a una versión general “CABA” si aplica."
    # So "Federico Lacroze 2306, Belgrano" might become "Federico Lacroze 2306, CABA".
    
    # Specific substitutions
    content = re.sub(r"Botox en Belgrano", "Botox en Buenos Aires (CABA)", content, flags=re.IGNORECASE)
    content = re.sub(r"centro de [eE]st[ée]tica en Belgrano", "centro de estética en Buenos Aires", content, flags=re.IGNORECASE)
    
    # General substitutions based on prompt examples
    content = content.replace("en mi consultorio de Belgrano", "en mi consultorio en Buenos Aires (CABA)")
    # "en Belgrano" -> "en CABA" (careful with this one)
    # We'll stick to specific known patterns first.
    
    # Metadata updates
    # <title>... Belgrano ...</title>
    def update_title(match):
        text = match.group(1)
        if "Belgrano" in text:
            text = text.replace("Belgrano", "Buenos Aires (CABA)")
        if "Buenos Aires" not in text and "CABA" not in text:
            text += " - Buenos Aires (CABA)"
        return f"<title>{text}</title>"
    
    content = re.sub(r"<title>(.*?)</title>", update_title, content, flags=re.DOTALL)

    # <meta name="description" ...>
    def update_meta_desc(match):
        attrs = match.group(1)
        if 'name="description"' in attrs:
            content_match = re.search(r'content=["\'](.*?)["\']', attrs)
            if content_match:
                desc = content_match.group(1)
                new_desc = desc.replace("Belgrano", "Buenos Aires (CABA)")
                if "Buenos Aires" not in new_desc and "CABA" not in new_desc:
                    new_desc += " en Buenos Aires (CABA)."
                return f'<meta {attrs.replace(desc, new_desc)}>'
        return match.group(0)

    content = re.sub(r'<meta (.*?)>', update_meta_desc, content)

    # <meta name="keywords" ...>
    def update_keywords(match):
        attrs = match.group(1)
        if 'name="keywords"' in attrs:
            content_match = re.search(r'content=["\'](.*?)["\']', attrs)
            if content_match:
                kws = content_match.group(1)
                # Replace global "Belgrano" in keywords
                new_kws = kws.replace("Belgrano", "Buenos Aires (CABA)")
                
                if "Buenos Aires" not in new_kws:
                    new_kws += ", Buenos Aires"
                if "CABA" not in new_kws:
                    new_kws += ", CABA"
                    
                return f'<meta {attrs.replace(kws, new_kws)}>'
        return match.group(0)
    
    content = re.sub(r'<meta (.*?)>', update_keywords, content)


    # H1 / H2 Replacements
    def update_headings(match):
        tag = match.group(1)
        text = match.group(2)
        if "Belgrano" in text:
            new_text = text.replace("Belgrano", "Buenos Aires (CABA)")
            return f"<{tag}>{new_text}</{tag}>"
        return match.group(0)

    content = re.sub(r"<(h[1-2])>(.*?)</\1>", update_headings, content, flags=re.IGNORECASE | re.DOTALL)

    # JSON-LD Updates
    # We need to find the <script type="application/ld+json"> block and edit it.
    
    def update_json_ld(match):
        json_str = match.group(1)
        try:
            data = json.loads(json_str)
            
            # Helper to update a node
            def update_node(node):
                # Update Address
                if "address" in node and isinstance(node["address"], dict):
                    node["address"]["addressLocality"] = "Buenos Aires"
                    node["address"]["addressRegion"] = "CABA"
                
                # Update AreaServed
                if "areaServed" in node:
                    if isinstance(node["areaServed"], dict):
                         node["areaServed"]["name"] = "Ciudad de Buenos Aires"
                    elif isinstance(node["areaServed"], str):
                        node["areaServed"] = "Ciudad de Buenos Aires"
                
                # Check for other Belgrano mentions in description/name
                if "description" in node and "Belgrano" in node["description"]:
                    node["description"] = node["description"].replace("Belgrano", "Buenos Aires")

                # If it's a list (graph), recurse
                if "@graph" in node:
                    for item in node["@graph"]:
                        update_node(item)
                
                # If provider is nested
                if "provider" in node and isinstance(node["provider"], dict):
                    update_node(node["provider"])

            if isinstance(data, list):
                for item in data:
                    update_node(item)
            else:
                update_node(data)

            return f'<script type="application/ld+json">\n{json.dumps(data, indent=2, ensure_ascii=False)}\n</script>'
        except json.JSONDecodeError:
            print(f"Warning: Could not parse JSON-LD in {filename}")
            return match.group(0)

    content = re.sub(r'<script type="application/ld+json">\s*({.*?})\s*</script>', update_json_ld, content, flags=re.DOTALL)


    # Canonical Update
    # <link rel="canonical" href="...">
    target_canonical = f"https://agustinaalvarez.com/{filename}"
    if 'rel="canonical"' in content:
        # Match anything inside href, allow optional slash at end
        content = re.sub(r'<link rel="canonical" href=".*?">', f'<link rel="canonical" href="{target_canonical}">', content)
        content = re.sub(r'<link rel="canonical" href=".*?"\s*/>', f'<link rel="canonical" href="{target_canonical}">', content)
    else:
        # Insert after meta charset or in head
        content = content.replace("</head>", f'<link rel="canonical" href="{target_canonical}">\n</head>')

    # Hreflang Check
    # Ensure es and en exist and point correctly.
    
    es_href = f"https://agustinaalvarez.com/{filename}"
    en_href = f"https://agustinaalvarez.com/en/{filename}"
    
    hreflang_es = f'<link rel="alternate" hreflang="es" href="{es_href}">'
    hreflang_en = f'<link rel="alternate" hreflang="en" href="{en_href}">'

    # Remove existing hreflangs to avoid dupes/mess
    # Handle both > and /> and multi-line attributes strictly or loosely
    content = re.sub(r'<link rel="alternate" hreflang="es" href=".*?"\s*/?>', '', content)
    content = re.sub(r'<link rel="alternate" hreflang="en" href=".*?"\s*/?>', '', content)
    
    # Add fresh ones (clean up empty lines later if needed)
    # Insert before </head>
    marker = "</head>"
    replacement = f"{hreflang_es}\n{hreflang_en}\n{marker}"
    content = content.replace(marker, replacement)


    # Language Redirect Script
    # Check if already exists
    if "navigator.language" not in content and "/en/" in content: 
         # Simple check might fail if other scripts use navigator.language.
         # The snippet provided is specific.
         pass
    
    if LANGUAGE_REDIRECT_SCRIPT.strip() not in content:
        # Insert before </body>
        content = content.replace("</body>", f"{LANGUAGE_REDIRECT_SCRIPT}\n</body>")

    return content

def main():
    print(f"Starting Root Standardization... Dry Run: {DRY_RUN}")
    
    for filename in TARGET_FILES:
        filepath = os.path.join(PROJECT_ROOT, filename)
        if not os.path.exists(filepath):
            print(f"Skipping {filename}: Not found.")
            continue
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        new_content = update_content(content, filename)
        
        if content != new_content:
            print(f"Changes detected for {filename}")
            if DRY_RUN:
                # Show a snippet of changes?
                # For now just confirming it worked.
                pass
            else:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated {filename}")
        else:
            print(f"No changes for {filename}")

if __name__ == "__main__":
    main()
