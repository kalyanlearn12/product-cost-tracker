import re

def extract_myntra_price(soup):
    price_tag = soup.find('span', {'class': 'pdp-price'})
    if price_tag:
        try:
            return float(''.join(filter(str.isdigit, price_tag.text)))
        except Exception:
            return None
    meta_desc = soup.find('meta', {'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        match = re.search(r'Rs\.?\s*([\d,]+)', meta_desc['content'])
        if match:
            try:
                return float(match.group(1).replace(',', ''))
            except Exception:
                return None
    return None
