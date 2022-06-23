from django.db import models

from .tags import Tag

# Search criteria for the post search

class SearchCriteria:
    """Interface for creating search criteria"""

    def __init__(self) -> None:
        pass

    def search(self, s) -> models.QuerySet:
        return s

class SearchCriteriaTag(SearchCriteria):
    """Used to search for posts that contain a certain tag"""

    def __init__(self, tag: Tag) -> None:
        self.tag = tag

    def search(self, s) -> models.QuerySet:
        return s.filter(tags=self.tag)

class SearchCriteriaExcludeTag(SearchCriteria):
    """Used to exclude tags from a search"""

    def __init__(self, tag: Tag) -> None:
        self.tag = tag

    def search(self, s) -> models.QuerySet:
        return s.exclude(tags=self.tag)

class SearchCriteriaWildCardTags(SearchCriteria):
    """Used to search for posts that contain a certain tag"""

    def __init__(self, tags: [Tag]) -> None:
        self.tags = tags

    def search(self, s) -> models.QuerySet:
        # It must include at least one of the tags, without duplicates
        return s.filter(tags__in=self.tags).distinct('id')

class SearchCriteriaExcludeWildCardTags(SearchCriteria):
    """Used to exclude tags from a search"""

    def __init__(self, tags: [Tag]) -> None:
        self.tags = tags

    def search(self, s) -> models.QuerySet:
        return s.exclude(tags__in=self.tags).distinct('id')

class SearchCriteriaParameter(SearchCriteria):
    """Used to search for posts that have a certain parameter"""

    def __init__(self, parameter: str, value: str) -> None:
        self.parameter = parameter
        self.value = value

    def search(self, s) -> models.QuerySet:
        return s.filter(**{self.parameter: self.value})

class SearchCriteriaExcludeParameter(SearchCriteria):
    """Used to exclude posts that have a certain parameter"""

    def __init__(self, parameter: str, value: str) -> None:
        self.parameter = parameter
        self.value = value

    def search(self, s) -> models.QuerySet:
        return s.exclude(**{self.parameter: self.value})