from django.db import models


class UniversityManager(models.Manager):

    def with_related(self):
        return self.prefetch_related('courses')

    def by_score(self):
        return self.with_related().order_by('-score', 'name')

    def by_name(self):
        return self.with_related().order_by('name')

    def have_page(self):
        return self.filter(detail_page_enabled=True)
