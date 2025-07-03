"""
Pagination utility for handling API pagination responses.
"""

class Pagination:
    """
    A class that wraps pagination data from API responses
    to provide attribute access for templates.
    """
    
    def __init__(self, pagination_dict=None):
        """Initialize pagination from a dictionary"""
        if pagination_dict is None:
            pagination_dict = {}
            
        self.page = pagination_dict.get('page', 1)
        self.pages = pagination_dict.get('pages', 1)
        self.per_page = pagination_dict.get('per_page', 10)
        self.total = pagination_dict.get('total', 0)
        self.has_next = pagination_dict.get('has_next', False)
        self.has_prev = pagination_dict.get('has_prev', False)
    
    @classmethod
    def from_dict(cls, pagination_dict=None):
        """Create a Pagination object from a dictionary"""
        return cls(pagination_dict)
    
    @classmethod
    def create_empty(cls):
        """Create an empty pagination object"""
        return cls({
            'page': 1, 
            'pages': 1, 
            'total': 0, 
            'per_page': 10,
            'has_next': False,
            'has_prev': False
        })
