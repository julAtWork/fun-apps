# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from fun.tests.utils import skipUnlessLms
from universities.factories import UniversityFactory


@skipUnlessLms
class CourseListTest(ModuleStoreTestCase):
    def setUp(self):
        super(CourseListTest, self).setUp()
        self.url = reverse('fun-courses-index')
        UniversityFactory(name=u"University1", code='univ1')
        UniversityFactory(name=u"University2", code='univ2')
        CourseFactory(org='univ1', number='001', display_name=u"Course1", ispublic=True)
        CourseFactory(org='univ2', number='002', display_name=u"Course2", ispublic=True)

    def test_list(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Course1')
        self.assertContains(response, 'Course2')

    def test_filtered_list(self):
        response = self.client.get(self.url, {'university': 'univ1'})
        self.assertContains(response, 'Course1')
        self.assertNotContains(response, 'Course2')

    def test_form_error(self):
        response = self.client.get(self.url, {'university': 'nope'})
        self.assertEqual(302, response.status_code)
