import math

class Paginator:
    def __init__(self, page, total_count, per_page=10, width=4, page_url=''):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count
        self.page_url = page_url

        self.width = width

    @property
    def total_pages(self):
        return math.ceil(self.total_count / float(self.per_page))

    @property
    def has_prev(self):
        return self.page > 1
    
    @property
    def display_arrows_left(self):
        return self.page > self.width + 1
    
    @property
    def display_arrows_right(self):
        return self.page < self.total_count - self.width
    
    @property
    def numbers(self):
        actual = []
        for num in range(self.page - self.width, self.page + self.width + 1):
            if num < 1:
                continue
            
            if num > self.total_pages:
                continue

            actual.append(num)
        
        return actual