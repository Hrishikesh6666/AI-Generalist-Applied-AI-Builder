import fitz
import io

def extract_from_pdf(pdf_file, label="Document"):
    if hasattr(pdf_file, 'read'):
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    else:
        doc = fitz.open(pdf_file)
    
    full_text = f"=== {label} ===\n"
    images = []
    seen_sizes = set() 

    for page_num, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            full_text += f"\n[Page {page_num+1}]\n{text}\n"
        
        for img in page.get_images(full=True):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]
            size = len(img_bytes)
            
            # ── Key fix: only keep real photos, skip icons/logos ──
            # Real inspection photos are typically > 50KB
            # Skip if we've already seen an image of exactly this size
            if size < 50000:
                continue
            if size in seen_sizes:
                continue
            seen_sizes.add(size)

            images.append({
                "page": page_num + 1,
                "data": img_bytes,
                "ext": base_image["ext"],
                "source": label,
                "size_kb": size // 1024
            })

    doc.close()
    return full_text, images


def get_key_sections(full_text, max_chars=6000):
    """
    For thermal docs: preserve ALL text since temperature readings
    are spread throughout and must not be cut.
    For inspection docs: focus on observation sections.
    """
    # If it's a thermal doc, return full text up to limit
    if "hotspot" in full_text.lower() or "coldspot" in full_text.lower() or "emissivity" in full_text.lower():
        return full_text[:max_chars]
    
    # For inspection docs, filter to relevant sections
    priority_keywords = [
        "summary", "observation", "leakage", "dampness",
        "negative side", "positive side", "impacted area",
        "recommended", "action", "treatment", "crack",
        "seepage", "bathroom", "terrace", "external wall",
        "balcony", "bedroom", "hall", "kitchen", "parking"
    ]
    
    lines = full_text.split('\n')
    relevant_lines = []
    char_count = 0
    
    for line in lines:
        line_lower = line.lower()
        is_relevant = any(kw in line_lower for kw in priority_keywords)
        
        if is_relevant or line.startswith('[Page') or line.startswith('==='):
            relevant_lines.append(line)
            char_count += len(line)
            if char_count > max_chars:
                break
    
    return '\n'.join(relevant_lines)