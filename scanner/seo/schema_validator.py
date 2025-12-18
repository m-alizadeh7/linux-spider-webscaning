"""
Schema Validator Module
Validates JSON-LD structured data for SEO best practices
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import re

from bs4 import BeautifulSoup

try:
    import extruct
    EXTRUCT_AVAILABLE = True
except ImportError:
    EXTRUCT_AVAILABLE = False


class IssueSeverity(Enum):
    """Severity levels for schema issues"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class SchemaIssue:
    """Represents a schema validation issue"""
    severity: IssueSeverity
    schema_type: str
    field: str
    message: str
    suggestion: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'severity': self.severity.value,
            'schema_type': self.schema_type,
            'field': self.field,
            'message': self.message,
            'suggestion': self.suggestion
        }


@dataclass
class SchemaValidationResult:
    """Result of schema validation"""
    schemas_found: List[str] = field(default_factory=list)
    total_schemas: int = 0
    errors: List[SchemaIssue] = field(default_factory=list)
    warnings: List[SchemaIssue] = field(default_factory=list)
    info: List[SchemaIssue] = field(default_factory=list)
    coverage_score: float = 0.0
    article_schema_valid: bool = False
    product_schema_valid: bool = False
    breadcrumb_present: bool = False
    organization_present: bool = False
    website_present: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'schemas_found': self.schemas_found,
            'total_schemas': self.total_schemas,
            'errors': [e.to_dict() for e in self.errors],
            'warnings': [w.to_dict() for w in self.warnings],
            'info': [i.to_dict() for i in self.info],
            'coverage_score': self.coverage_score,
            'article_schema_valid': self.article_schema_valid,
            'product_schema_valid': self.product_schema_valid,
            'breadcrumb_present': self.breadcrumb_present,
            'organization_present': self.organization_present,
            'website_present': self.website_present,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings)
        }


class SchemaValidator:
    """
    Validates JSON-LD structured data blocks
    
    Validates presence of critical fields for:
    - Article: headline/datePublished/author/mainEntityOfPage
    - Product: name/offers.price/offers.availability
    - BreadcrumbList
    - Organization
    - WebSite
    """
    
    # Required fields for each schema type
    ARTICLE_REQUIRED = ['headline', 'datePublished', 'author']
    ARTICLE_RECOMMENDED = ['mainEntityOfPage', 'dateModified', 'image', 'publisher']
    
    PRODUCT_REQUIRED = ['name']
    PRODUCT_OFFER_REQUIRED = ['price', 'priceCurrency', 'availability']
    PRODUCT_RECOMMENDED = ['description', 'image', 'sku', 'brand']
    
    BREADCRUMB_REQUIRED = ['itemListElement']
    
    ORGANIZATION_REQUIRED = ['name']
    ORGANIZATION_RECOMMENDED = ['url', 'logo', 'contactPoint', 'sameAs']
    
    WEBSITE_REQUIRED = ['name', 'url']
    WEBSITE_RECOMMENDED = ['potentialAction']
    
    # Article types to validate
    ARTICLE_TYPES = ['Article', 'NewsArticle', 'BlogPosting', 'TechArticle', 'ScholarlyArticle']
    
    def __init__(self):
        """Initialize schema validator"""
        if not EXTRUCT_AVAILABLE:
            print("  [!] extruct not installed - schema validation will be limited")
    
    def validate(self, html_content: str) -> SchemaValidationResult:
        """
        Validate structured data in HTML
        
        Args:
            html_content: HTML content to validate
            
        Returns:
            SchemaValidationResult
        """
        result = SchemaValidationResult()
        
        # Extract JSON-LD blocks
        schemas = self._extract_schemas(html_content)
        
        if not schemas:
            result.warnings.append(SchemaIssue(
                severity=IssueSeverity.WARNING,
                schema_type='General',
                field='JSON-LD',
                message='No JSON-LD structured data found',
                suggestion='Add JSON-LD schema markup for better search visibility'
            ))
            return result
        
        result.total_schemas = len(schemas)
        
        for schema in schemas:
            schema_type = self._get_schema_type(schema)
            result.schemas_found.append(schema_type)
            
            # Validate based on type
            if schema_type in self.ARTICLE_TYPES:
                self._validate_article(schema, result)
            elif schema_type == 'Product':
                self._validate_product(schema, result)
            elif schema_type == 'BreadcrumbList':
                self._validate_breadcrumb(schema, result)
            elif schema_type == 'Organization':
                self._validate_organization(schema, result)
            elif schema_type == 'WebSite':
                self._validate_website(schema, result)
        
        # Calculate coverage score
        result.coverage_score = self._calculate_coverage_score(result)
        
        return result
    
    def _extract_schemas(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract JSON-LD schemas from HTML"""
        schemas = []
        
        if EXTRUCT_AVAILABLE:
            try:
                data = extruct.extract(html_content, syntaxes=['json-ld'])
                schemas = data.get('json-ld', [])
                
                # Flatten @graph structures
                flattened = []
                for schema in schemas:
                    if isinstance(schema, dict) and '@graph' in schema:
                        flattened.extend(schema['@graph'])
                    else:
                        flattened.append(schema)
                schemas = flattened
                
            except Exception as e:
                pass
        else:
            # Manual extraction
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                for script in soup.find_all('script', type='application/ld+json'):
                    content = script.string
                    if content:
                        try:
                            data = json.loads(content)
                            if isinstance(data, dict) and '@graph' in data:
                                schemas.extend(data['@graph'])
                            elif isinstance(data, list):
                                schemas.extend(data)
                            else:
                                schemas.append(data)
                        except json.JSONDecodeError:
                            pass
            except Exception as e:
                pass
        
        return schemas
    
    def _get_schema_type(self, schema: Dict[str, Any]) -> str:
        """Get schema type from schema object"""
        schema_type = schema.get('@type', 'Unknown')
        if isinstance(schema_type, list):
            schema_type = schema_type[0] if schema_type else 'Unknown'
        return schema_type
    
    def _validate_article(self, schema: Dict[str, Any], result: SchemaValidationResult):
        """Validate Article schema"""
        schema_type = self._get_schema_type(schema)
        valid = True
        
        # Check required fields
        for field in self.ARTICLE_REQUIRED:
            if field not in schema or not schema[field]:
                valid = False
                result.errors.append(SchemaIssue(
                    severity=IssueSeverity.ERROR,
                    schema_type=schema_type,
                    field=field,
                    message=f'Missing required field: {field}',
                    suggestion=f'Add {field} to your {schema_type} schema'
                ))
        
        # Check recommended fields
        for field in self.ARTICLE_RECOMMENDED:
            if field not in schema or not schema[field]:
                result.warnings.append(SchemaIssue(
                    severity=IssueSeverity.WARNING,
                    schema_type=schema_type,
                    field=field,
                    message=f'Missing recommended field: {field}',
                    suggestion=f'Consider adding {field} for better search visibility'
                ))
        
        # Validate author structure
        author = schema.get('author')
        if author:
            if isinstance(author, str):
                result.warnings.append(SchemaIssue(
                    severity=IssueSeverity.WARNING,
                    schema_type=schema_type,
                    field='author',
                    message='Author should be an object with @type and name',
                    suggestion='Use {"@type": "Person", "name": "Author Name"}'
                ))
            elif isinstance(author, dict) and not author.get('name'):
                result.errors.append(SchemaIssue(
                    severity=IssueSeverity.ERROR,
                    schema_type=schema_type,
                    field='author.name',
                    message='Author object missing name',
                    suggestion='Add name property to author object'
                ))
        
        # Validate publisher
        publisher = schema.get('publisher')
        if publisher:
            if isinstance(publisher, dict):
                if not publisher.get('name'):
                    result.errors.append(SchemaIssue(
                        severity=IssueSeverity.ERROR,
                        schema_type=schema_type,
                        field='publisher.name',
                        message='Publisher missing name',
                        suggestion='Add name to publisher object'
                    ))
                if not publisher.get('logo'):
                    result.warnings.append(SchemaIssue(
                        severity=IssueSeverity.WARNING,
                        schema_type=schema_type,
                        field='publisher.logo',
                        message='Publisher missing logo',
                        suggestion='Add logo ImageObject to publisher'
                    ))
        
        # Validate dates
        date_published = schema.get('datePublished')
        if date_published:
            if not self._is_valid_date_format(date_published):
                result.warnings.append(SchemaIssue(
                    severity=IssueSeverity.WARNING,
                    schema_type=schema_type,
                    field='datePublished',
                    message='Date format may not be optimal',
                    suggestion='Use ISO 8601 format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS+TZ'
                ))
        
        result.article_schema_valid = valid
    
    def _validate_product(self, schema: Dict[str, Any], result: SchemaValidationResult):
        """Validate Product schema"""
        valid = True
        
        # Check required fields
        for field in self.PRODUCT_REQUIRED:
            if field not in schema or not schema[field]:
                valid = False
                result.errors.append(SchemaIssue(
                    severity=IssueSeverity.ERROR,
                    schema_type='Product',
                    field=field,
                    message=f'Missing required field: {field}',
                    suggestion=f'Add {field} to your Product schema'
                ))
        
        # Check offers
        offers = schema.get('offers')
        if not offers:
            valid = False
            result.errors.append(SchemaIssue(
                severity=IssueSeverity.ERROR,
                schema_type='Product',
                field='offers',
                message='Missing offers object',
                suggestion='Add offers with price, currency, and availability'
            ))
        else:
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            
            for field in self.PRODUCT_OFFER_REQUIRED:
                if field not in offers or not offers[field]:
                    valid = False
                    result.errors.append(SchemaIssue(
                        severity=IssueSeverity.ERROR,
                        schema_type='Product',
                        field=f'offers.{field}',
                        message=f'Missing required field in offers: {field}',
                        suggestion=f'Add {field} to offers object'
                    ))
            
            # Check availability format
            availability = offers.get('availability', '')
            if availability and 'schema.org' not in str(availability):
                result.warnings.append(SchemaIssue(
                    severity=IssueSeverity.WARNING,
                    schema_type='Product',
                    field='offers.availability',
                    message='Availability should use schema.org URL format',
                    suggestion='Use https://schema.org/InStock or https://schema.org/OutOfStock'
                ))
        
        # Check recommended fields
        for field in self.PRODUCT_RECOMMENDED:
            if field not in schema or not schema[field]:
                result.warnings.append(SchemaIssue(
                    severity=IssueSeverity.WARNING,
                    schema_type='Product',
                    field=field,
                    message=f'Missing recommended field: {field}',
                    suggestion=f'Consider adding {field} for better product visibility'
                ))
        
        # Check for aggregateRating
        if 'aggregateRating' in schema:
            rating = schema['aggregateRating']
            if isinstance(rating, dict):
                if not rating.get('ratingValue'):
                    result.warnings.append(SchemaIssue(
                        severity=IssueSeverity.WARNING,
                        schema_type='Product',
                        field='aggregateRating.ratingValue',
                        message='Missing ratingValue in aggregateRating',
                        suggestion='Add ratingValue to show star ratings in search results'
                    ))
        
        result.product_schema_valid = valid
    
    def _validate_breadcrumb(self, schema: Dict[str, Any], result: SchemaValidationResult):
        """Validate BreadcrumbList schema"""
        result.breadcrumb_present = True
        
        items = schema.get('itemListElement', [])
        if not items:
            result.errors.append(SchemaIssue(
                severity=IssueSeverity.ERROR,
                schema_type='BreadcrumbList',
                field='itemListElement',
                message='BreadcrumbList has no items',
                suggestion='Add ListItem elements with position, name, and item'
            ))
            return
        
        # Validate each item
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            
            if not item.get('position'):
                result.errors.append(SchemaIssue(
                    severity=IssueSeverity.ERROR,
                    schema_type='BreadcrumbList',
                    field=f'itemListElement[{i}].position',
                    message=f'Breadcrumb item {i} missing position',
                    suggestion='Add position number to each ListItem'
                ))
            
            if not item.get('name') and not item.get('item', {}).get('name'):
                result.warnings.append(SchemaIssue(
                    severity=IssueSeverity.WARNING,
                    schema_type='BreadcrumbList',
                    field=f'itemListElement[{i}].name',
                    message=f'Breadcrumb item {i} missing name',
                    suggestion='Add name to each ListItem'
                ))
    
    def _validate_organization(self, schema: Dict[str, Any], result: SchemaValidationResult):
        """Validate Organization schema"""
        result.organization_present = True
        
        for field in self.ORGANIZATION_REQUIRED:
            if field not in schema or not schema[field]:
                result.errors.append(SchemaIssue(
                    severity=IssueSeverity.ERROR,
                    schema_type='Organization',
                    field=field,
                    message=f'Missing required field: {field}',
                    suggestion=f'Add {field} to your Organization schema'
                ))
        
        for field in self.ORGANIZATION_RECOMMENDED:
            if field not in schema or not schema[field]:
                result.warnings.append(SchemaIssue(
                    severity=IssueSeverity.WARNING,
                    schema_type='Organization',
                    field=field,
                    message=f'Missing recommended field: {field}',
                    suggestion=f'Consider adding {field} for richer organization display'
                ))
    
    def _validate_website(self, schema: Dict[str, Any], result: SchemaValidationResult):
        """Validate WebSite schema"""
        result.website_present = True
        
        for field in self.WEBSITE_REQUIRED:
            if field not in schema or not schema[field]:
                result.errors.append(SchemaIssue(
                    severity=IssueSeverity.ERROR,
                    schema_type='WebSite',
                    field=field,
                    message=f'Missing required field: {field}',
                    suggestion=f'Add {field} to your WebSite schema'
                ))
        
        # Check for SearchAction
        potential_action = schema.get('potentialAction')
        if not potential_action:
            result.info.append(SchemaIssue(
                severity=IssueSeverity.INFO,
                schema_type='WebSite',
                field='potentialAction',
                message='No SearchAction defined',
                suggestion='Add SearchAction to enable sitelinks search box in Google'
            ))
        else:
            if isinstance(potential_action, list):
                potential_action = potential_action[0]
            if isinstance(potential_action, dict):
                if potential_action.get('@type') == 'SearchAction':
                    if not potential_action.get('query-input'):
                        result.warnings.append(SchemaIssue(
                            severity=IssueSeverity.WARNING,
                            schema_type='WebSite',
                            field='potentialAction.query-input',
                            message='SearchAction missing query-input',
                            suggestion='Add query-input to define search parameter'
                        ))
    
    def _is_valid_date_format(self, date_str: str) -> bool:
        """Check if date string is in valid ISO 8601 format"""
        iso_pattern = r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?(([+-]\d{2}:\d{2})|Z)?)?$'
        return bool(re.match(iso_pattern, str(date_str)))
    
    def _calculate_coverage_score(self, result: SchemaValidationResult) -> float:
        """Calculate overall schema coverage score (0-100)"""
        score = 0.0
        max_score = 100.0
        
        # Base score for having any schema
        if result.total_schemas > 0:
            score += 20
        
        # Score for important schema types
        if result.breadcrumb_present:
            score += 15
        if result.organization_present:
            score += 15
        if result.website_present:
            score += 10
        if result.article_schema_valid:
            score += 20
        if result.product_schema_valid:
            score += 20
        
        # Deductions for errors
        error_deduction = len(result.errors) * 5
        warning_deduction = len(result.warnings) * 2
        
        score = max(0, score - error_deduction - warning_deduction)
        
        return min(score, max_score)
