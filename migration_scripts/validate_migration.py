import os
import re

PROJECT_ROOT = "d:/Proyectos/Web/agustinaalvarez.com - auto"
LOCATIONS = ["belgrano", "palermo", "nunez"]
TARGET_FILES_SAMPLE = ["botox.html"] # We can check all, but let's iterate dirs

def check_file(filepath, location):
    issues = []
    
    if not os.path.exists(filepath):
        return ["File not found"]
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check Canonical
    # Expect: <link rel="canonical" href="https://agustinaalvarez.com/location/file.html">
    filename = os.path.basename(filepath)
    expected_canonical = f"https://agustinaalvarez.com/{location}/{filename}"
    if location == "root":
        expected_canonical = f"https://agustinaalvarez.com/{filename}"
        
    canonical_match = re.search(r'<link rel="canonical" href=["\'](.*?)["\']\s*/?>', content)
    if not canonical_match:
        # Try finding it with simple > just in case
        canonical_match = re.search(r'<link rel="canonical" href=["\'](.*?)["\']\s*>', content)
        
    if not canonical_match:
        issues.append("Missing Canonical")
    elif canonical_match.group(1) != expected_canonical:
        issues.append(f"Wrong Canonical: Found {canonical_match.group(1)}, Expected {expected_canonical}")
        
    # Check Hreflang
    hreflang = re.search(r'hreflang=', content)
    if location != "root":
        if hreflang:
            issues.append(f"Hreflang found in localized file")
    else:
        # Root must have hreflang
        if not hreflang:
            issues.append("Missing Hreflang in Root file")
            
    # Check Title
    # Should contain Location Name
    title_match = re.search(r'<title>(.*?)</title>', content)
    if title_match:
        title = title_match.group(1)
        if location != "root":
            # Belgrano, Palermo, Nuñez
            # Nuñez might be "Núñez"
            loc_name = location.capitalize()
            if location == "nunez": loc_name = "Núñez"
            if loc_name not in title:
                issues.append(f"Title missing location name '{loc_name}': {title}")
    
    # Check Assets path (simple check for "images/")
    # In subfolder, it should be "../images/"
    if location != "root":
        if 'src="images/' in content:
            issues.append("Found relative image path 'src=\"images/'. Should be '../images/'")
        if 'href="css/' in content:
            issues.append("Found relative css path 'href=\"css/'. Should be '../css/'")
            
    return issues

def main():
    report = []
    report.append("INFORME DE MIGRACIÓN MULTI-SUCURSAL")
    report.append("===================================")
    
    total_files = 0
    total_issues = 0
    
    # 1. Root Check
    report.append("\nRevison Root (CABA):")
    root_files = [f for f in os.listdir(PROJECT_ROOT) if f.endswith(".html") and "treatment" in f or "botox" in f or "sculptra" in f] # rough filter
    # Use the TARGET_FILES list if possible, but let's just dynamic scan
    # Let's use the explicit list from script 1 to be consistent?
    # Or just check critical files.
    
    treatments = ["botox.html", "sculptra.html", "rellenos.html", "depilacion.html"] # Sampling
    
    for t in treatments:
        path = os.path.join(PROJECT_ROOT, t)
        issues = check_file(path, "root")
        if issues:
            report.append(f"[FAIL] {t}: {', '.join(issues)}")
            total_issues += 1
        else:
            report.append(f"[OK] {t}")
            
    # 2. Location Check
    for loc in LOCATIONS:
        report.append(f"\nRevision {loc.upper()}:")
        loc_dir = os.path.join(PROJECT_ROOT, loc)
        if not os.path.exists(loc_dir):
            report.append(f"Directory {loc} missing!")
            continue
            
        files = os.listdir(loc_dir)
        count = 0
        for f in files:
            if not f.endswith(".html"): continue
            count += 1
            path = os.path.join(loc_dir, f)
            issues = check_file(path, loc)
            if issues:
                report.append(f"[FAIL] {f}: {', '.join(issues)}")
                total_issues += 1
            # else: report.append(f"[OK] {f}") # Verbose, maybe skip passing
            
        report.append(f"Processed {count} files in {loc}.")
        total_files += count
        
    report.append("\n===================================")
    report.append(f"Total Localized Files: {total_files}")
    report.append(f"Total Issues Found: {total_issues}")
    report.append("\nAcciones Automáticas Completadas:")
    report.append("- Estandarización de raíz a 'Buenos Aires / CABA'.")
    report.append("- Generación de carpetas /belgrano, /palermo, /nunez.")
    report.append("- Ajuste de rutas relativas (images, css, data).")
    report.append("- Actualización de SEO Metadata y Canonicals.")
    report.append("- Inyección de script de redirección de idioma.")
    
    with open(os.path.join(PROJECT_ROOT, "informe-multi-sucursal.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print("\n".join(report))

if __name__ == "__main__":
    main()
