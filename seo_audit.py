import os
import re
import json

def audit_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return None

    # Title
    title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else None
    
    # Meta Description
    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
    description = desc_match.group(1).strip() if desc_match else None
    
    # H1
    h1_matches = re.findall(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
    h1_count = len(h1_matches)
    h1_content = [clean_html(h) for h in h1_matches]
    
    # Canonical
    canonical_match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\'](.*?)["\']', content, re.IGNORECASE)
    canonical = canonical_match.group(1).strip() if canonical_match else None

    # OG Tags
    og_title = bool(re.search(r'property=["\']og:title["\']', content, re.IGNORECASE))
    og_desc = bool(re.search(r'property=["\']og:description["\']', content, re.IGNORECASE))
    
    # Images without Alt
    # Simple regex for <img> tags that don't have alt="..." inside
    # This is tricky with regex, simpler to find all imgs and check attributes
    imgs = re.findall(r'<img\s+([^>]*)>', content, re.IGNORECASE)
    missing_alt_count = 0
    for img_attrs in imgs:
        if 'alt=' not in img_attrs.lower():
            missing_alt_count += 1

    # Score Calculation (Simple heuristic)
    score = 100
    issues = []
    opportunities = []

    if not title:
        score -= 20
        issues.append("Missing Title")
    elif len(title) < 10:
        score -= 5
        issues.append("Title too short")
    elif len(title) > 70:
        score -= 5
        issues.append("Title too long")
        
    if not description:
        score -= 20
        issues.append("Missing Meta Description")
    elif len(description) < 50:
        score -= 5
        issues.append("Meta Description too short")
        
    if h1_count == 0:
        score -= 20
        issues.append("Missing H1")
    elif h1_count > 1:
        score -= 10
        issues.append(f"Multiple H1s ({h1_count})")
        
    if not canonical:
        score -= 10
        issues.append("Missing Canonical")
        
    if missing_alt_count > 0:
        score -= 5
        issues.append(f"{missing_alt_count} Images missing Alt text")

    if not og_title: 
        opportunities.append("Add Open Graph Title")
    if not og_desc:
        opportunities.append("Add Open Graph Description")
        
    return {
        "filename": os.path.basename(filepath),
        "path": filepath,
        "score": max(0, score),
        "title": title,
        "description": description,
        "h1_count": h1_count,
        "h1_content": h1_content,
        "canonical": canonical,
        "missing_alt": missing_alt_count,
        "issues": issues,
        "opportunities": opportunities
    }

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def main():
    root_dirs = ['.', 'afecciones']
    results = []
    
    for root_dir in root_dirs:
        if not os.path.exists(root_dir):
            continue
            
        for root, dirs, files in os.walk(root_dir):
            # Skip irrelevant info
            if 'phpmailer' in root or 'assets' in root or '.git' in root:
                continue
                
            for file in files:
                if file.endswith('.html'):
                    filepath = os.path.join(root, file)
                    res = audit_file(filepath)
                    if res:
                        results.append(res)
                        
                        
    with open('audit_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print("Audit complete. Results saved to audit_results.json")

if __name__ == "__main__":
    main()
