"""
Product Extractor Module
Extracts product information from e-commerce websites
"""

from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass, field
import re
import json

from bs4 import BeautifulSoup

try:
    import extruct
    EXTRUCT_AVAILABLE = True
except ImportError:
    EXTRUCT_AVAILABLE = False

from utils.http_client import HTTPClient


@dataclass
class ProductData:
    """Represents extracted product data"""
    name: str
    url: str
    price: Optional[str] = None
    currency: Optional[str] = None
    availability: Optional[str] = None
    sku: Optional[str] = None
    brand: Optional[str] = None
    rating: Optional[float] = None
    review_count: int = 0
    description_length: int = 0
    image_url: Optional[str] = None
    image_alt_present: bool = False
    canonical: Optional[str] = None
    indexable: bool = True
    status_code: int = 200
    has_schema: bool = False
    
    # SEO issues
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'url': self.url,
            'price': self.price,
            'currency': self.currency,
            'availability': self.availability,
            'sku': self.sku,
            'brand': self.brand,
            'rating': self.rating,
            'review_count': self.review_count,
            'description_length': self.description_length,
            'image_url': self.image_url,
            'image_alt_present': self.image_alt_present,
            'canonical': self.canonical,
            'indexable': self.indexable,
            'status_code': self.status_code,
            'has_schema': self.has_schema,
            'issues': self.issues,
            'warnings': self.warnings
        }


@dataclass
class ProductExtractionResult:
    """Result of product extraction"""
    total_found: int = 0
    products: List[ProductData] = field(default_factory=list)
    with_schema: int = 0
    with_price: int = 0
    with_availability: int = 0
    with_rating: int = 0
    indexable_count: int = 0
    missing_image_alt: int = 0
    platform_detected: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_found': self.total_found,
            'products': [p.to_dict() for p in self.products],
            'with_schema': self.with_schema,
            'schema_coverage_percent': round(self.with_schema / self.total_found * 100, 1) if self.total_found > 0 else 0,
            'with_price': self.with_price,
            'price_coverage_percent': round(self.with_price / self.total_found * 100, 1) if self.total_found > 0 else 0,
            'with_availability': self.with_availability,
            'availability_coverage_percent': round(self.with_availability / self.total_found * 100, 1) if self.total_found > 0 else 0,
            'with_rating': self.with_rating,
            'indexable_count': self.indexable_count,
            'missing_image_alt': self.missing_image_alt,
            'platform_detected': self.platform_detected,
            'errors': self.errors
        }


class ProductExtractor:
    """
    Extracts product information from e-commerce websites
    
    Extraction priority:
    1. JSON-LD type: Product
    2. Category pages product cards + pagination
    3. Platform hints (Woo/Shopify) ONLY if detectable without login
    """
    
    # E-commerce platform indicators
    PLATFORM_INDICATORS = {
        'woocommerce': [
            '/wp-content/plugins/woocommerce/',
            'woocommerce',
            'wc-',
            'add-to-cart',
        ],
        'shopify': [
            'cdn.shopify.com',
            'shopify',
            '/collections/',
            'product-form',
        ],
        'magento': [
            '/static/frontend/',
            'Magento',
            'mage/',
            'catalog-product',
        ],
        'prestashop': [
            'prestashop',
            '/modules/',
            'id_product',
        ],
        'opencart': [
            'opencart',
            'route=product',
        ]
    }
    
    def __init__(self):
        """Initialize product extractor"""
        self.http_client = HTTPClient(timeout=15)
        
        if not EXTRUCT_AVAILABLE:
            print("  [!] extruct not installed - JSON-LD extraction will be limited")
    
    def extract_from_urls(self, urls: List[str], max_products: int = 50) -> ProductExtractionResult:
        """
        Extract products from a list of URLs
        
        Args:
            urls: List of URLs to extract from
            max_products: Maximum products to extract
            
        Returns:
            ProductExtractionResult
        """
        result = ProductExtractionResult()
        platform_detected = None
        
        print(f"  [+] Extracting products from {len(urls)} URLs...")
        
        for url in urls[:max_products]:
            try:
                product = self.extract_single(url)
                if product:
                    result.products.append(product)
                    
                    if product.has_schema:
                        result.with_schema += 1
                    if product.price:
                        result.with_price += 1
                    if product.availability:
                        result.with_availability += 1
                    if product.rating:
                        result.with_rating += 1
                    if product.indexable:
                        result.indexable_count += 1
                    if not product.image_alt_present and product.image_url:
                        result.missing_image_alt += 1
                    
                    # Detect platform from first product
                    if not platform_detected and product.has_schema:
                        platform_detected = self._detect_platform_from_url(url)
                        
            except Exception as e:
                result.errors.append(f"{url}: {str(e)}")
        
        result.total_found = len(result.products)
        result.platform_detected = platform_detected
        
        print(f"  [+] Extracted {result.total_found} products")
        
        return result
    
    def extract_single(self, url: str) -> Optional[ProductData]:
        """
        Extract product data from a single URL
        
        Args:
            url: Product URL
            
        Returns:
            ProductData or None
        """
        try:
            response = self.http_client.get(url)
            
            if not response:
                return None
            
            product = ProductData(
                name='',
                url=url,
                status_code=response.status_code
            )
            
            if response.status_code != 200:
                product.indexable = False
                product.issues.append(f"Non-200 status code: {response.status_code}")
                return product
            
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try JSON-LD extraction first
            schema_data = self._extract_from_jsonld(html_content, soup)
            if schema_data:
                product.has_schema = True
                product.name = schema_data.get('name', '')
                product.price = schema_data.get('price')
                product.currency = schema_data.get('currency')
                product.availability = schema_data.get('availability')
                product.sku = schema_data.get('sku')
                product.brand = schema_data.get('brand')
                product.rating = schema_data.get('rating')
                product.review_count = schema_data.get('review_count', 0)
                product.image_url = schema_data.get('image')
                product.description_length = schema_data.get('description_length', 0)
            
            # Extract from HTML (fills in gaps)
            self._extract_from_html(soup, product, url)
            
            # Check indexability
            self._check_indexability(soup, product)
            
            # Generate issues and warnings
            self._generate_issues(product)
            
            return product
            
        except Exception as e:
            return None
    
    def _extract_from_jsonld(self, html_content: str, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract product data from JSON-LD"""
        
        if EXTRUCT_AVAILABLE:
            return self._extract_with_extruct(html_content)
        else:
            return self._extract_jsonld_manually(soup)
    
    def _extract_with_extruct(self, html_content: str) -> Optional[Dict[str, Any]]:
        """Extract using extruct library"""
        try:
            data = extruct.extract(html_content, syntaxes=['json-ld'])
            
            for item in data.get('json-ld', []):
                item_type = item.get('@type', '')
                
                if isinstance(item_type, list):
                    item_type = item_type[0] if item_type else ''
                
                if item_type == 'Product':
                    return self._parse_product_schema(item)
            
            return None
            
        except Exception as e:
            return None
    
    def _extract_jsonld_manually(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract JSON-LD manually without extruct"""
        try:
            for script in soup.find_all('script', type='application/ld+json'):
                content = script.string
                if not content:
                    continue
                
                try:
                    data = json.loads(content)
                    
                    # Handle @graph structure
                    if isinstance(data, dict) and '@graph' in data:
                        items = data['@graph']
                    elif isinstance(data, list):
                        items = data
                    else:
                        items = [data]
                    
                    for item in items:
                        if not isinstance(item, dict):
                            continue
                        
                        item_type = item.get('@type', '')
                        if isinstance(item_type, list):
                            item_type = item_type[0] if item_type else ''
                        
                        if item_type == 'Product':
                            return self._parse_product_schema(item)
                
                except json.JSONDecodeError:
                    continue
            
            return None
            
        except Exception as e:
            return None
    
    def _parse_product_schema(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Product schema item"""
        result = {
            'name': item.get('name', ''),
        }
        
        # Price from offers
        offers = item.get('offers')
        if offers:
            if isinstance(offers, list):
                offers = offers[0]
            if isinstance(offers, dict):
                result['price'] = offers.get('price')
                result['currency'] = offers.get('priceCurrency')
                
                availability = offers.get('availability', '')
                if availability:
                    # Normalize availability
                    if 'InStock' in str(availability):
                        result['availability'] = 'InStock'
                    elif 'OutOfStock' in str(availability):
                        result['availability'] = 'OutOfStock'
                    elif 'PreOrder' in str(availability):
                        result['availability'] = 'PreOrder'
                    else:
                        result['availability'] = availability
        
        # SKU
        result['sku'] = item.get('sku') or item.get('productID')
        
        # Brand
        brand = item.get('brand')
        if brand:
            if isinstance(brand, dict):
                result['brand'] = brand.get('name', '')
            else:
                result['brand'] = str(brand)
        
        # Rating
        aggregate_rating = item.get('aggregateRating')
        if aggregate_rating:
            if isinstance(aggregate_rating, dict):
                try:
                    result['rating'] = float(aggregate_rating.get('ratingValue', 0))
                    result['review_count'] = int(aggregate_rating.get('reviewCount', 0))
                except (ValueError, TypeError):
                    pass
        
        # Image
        image = item.get('image')
        if image:
            if isinstance(image, list):
                image = image[0]
            if isinstance(image, dict):
                result['image'] = image.get('url', '')
            else:
                result['image'] = str(image)
        
        # Description
        description = item.get('description', '')
        if description:
            result['description_length'] = len(description)
        
        return result
    
    def _extract_from_html(self, soup: BeautifulSoup, product: ProductData, base_url: str):
        """Extract product data from HTML"""
        
        # Name from H1 if not set
        if not product.name:
            h1 = soup.find('h1')
            if h1:
                product.name = h1.get_text().strip()
        
        # Canonical
        canonical = soup.find('link', rel='canonical')
        if canonical:
            product.canonical = canonical.get('href', '')
        
        # Check main product image for alt text
        if product.image_url:
            # Try to find the image and check alt
            img = soup.find('img', src=re.compile(re.escape(product.image_url.split('/')[-1]) if '/' in product.image_url else product.image_url))
            if img and img.get('alt'):
                product.image_alt_present = True
        
        # If no image found from schema, try common patterns
        if not product.image_url:
            # Look for product images
            product_img = soup.find('img', class_=re.compile(r'product|main|primary|featured', re.I))
            if product_img:
                product.image_url = product_img.get('src', '')
                if product_img.get('alt'):
                    product.image_alt_present = True
        
        # Try to get price from HTML if not from schema
        if not product.price:
            price_patterns = [
                ('span', {'class': re.compile(r'price|amount|cost', re.I)}),
                ('div', {'class': re.compile(r'price|amount|cost', re.I)}),
                ('p', {'class': re.compile(r'price|amount|cost', re.I)}),
            ]
            
            for tag, attrs in price_patterns:
                element = soup.find(tag, attrs)
                if element:
                    price_text = element.get_text().strip()
                    # Extract price value
                    price_match = re.search(r'[\d,.]+', price_text)
                    if price_match:
                        product.price = price_match.group()
                        break
    
    def _check_indexability(self, soup: BeautifulSoup, product: ProductData):
        """Check if page is indexable"""
        
        # Check meta robots
        meta_robots = soup.find('meta', attrs={'name': 'robots'})
        if meta_robots:
            content = meta_robots.get('content', '').lower()
            if 'noindex' in content:
                product.indexable = False
                product.issues.append("Page has noindex directive")
    
    def _generate_issues(self, product: ProductData):
        """Generate SEO issues and warnings"""
        
        # Name issues
        if not product.name:
            product.issues.append("Missing product name")
        elif len(product.name) < 10:
            product.warnings.append("Product name too short")
        
        # Price issues
        if not product.price:
            product.issues.append("Missing price")
        
        # Availability issues
        if not product.availability:
            product.issues.append("Missing availability")
        
        # Schema issues
        if not product.has_schema:
            product.issues.append("No Product schema markup")
        
        # Image issues
        if not product.image_url:
            product.warnings.append("No product image found")
        elif not product.image_alt_present:
            product.warnings.append("Product image missing alt text")
        
        # Description issues
        if product.description_length == 0:
            product.warnings.append("No product description in schema")
        elif product.description_length < 50:
            product.warnings.append("Product description too short")
    
    def _detect_platform_from_url(self, url: str) -> Optional[str]:
        """Detect e-commerce platform from URL patterns"""
        url_lower = url.lower()
        
        for platform, indicators in self.PLATFORM_INDICATORS.items():
            for indicator in indicators:
                if indicator.lower() in url_lower:
                    return platform
        
        return None
    
    def detect_platform(self, html_content: str, url: str) -> Optional[str]:
        """
        Detect e-commerce platform from HTML content
        
        Args:
            html_content: HTML content
            url: URL
            
        Returns:
            Platform name or None
        """
        content_lower = html_content.lower()
        url_lower = url.lower()
        
        for platform, indicators in self.PLATFORM_INDICATORS.items():
            for indicator in indicators:
                if indicator.lower() in content_lower or indicator.lower() in url_lower:
                    return platform
        
        return None
    
    def extract_from_category_page(self, url: str, max_products: int = 20) -> List[str]:
        """
        Extract product URLs from a category/listing page
        
        Args:
            url: Category page URL
            max_products: Maximum product URLs to extract
            
        Returns:
            List of product URLs
        """
        product_urls = []
        
        try:
            response = self.http_client.get(url)
            if not response or response.status_code != 200:
                return product_urls
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Common product link patterns
            product_patterns = [
                ('a', {'href': re.compile(r'/product/', re.I)}),
                ('a', {'href': re.compile(r'/products/', re.I)}),
                ('a', {'href': re.compile(r'/p/', re.I)}),
                ('a', {'class': re.compile(r'product|item', re.I)}),
                ('a', {'data-product-id': True}),
            ]
            
            for tag, attrs in product_patterns:
                links = soup.find_all(tag, attrs)
                for link in links:
                    href = link.get('href', '')
                    if href:
                        full_url = urljoin(url, href)
                        if full_url not in product_urls:
                            product_urls.append(full_url)
                        
                        if len(product_urls) >= max_products:
                            break
                
                if len(product_urls) >= max_products:
                    break
        
        except Exception as e:
            pass
        
        return product_urls
