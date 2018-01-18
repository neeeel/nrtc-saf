from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^projects/(?P<projectNo>.*)', views.get_count_point_data, name='clone'),
    url(r'^networkInfo/(?P<projectNo>.*)', views.get_network_info, name='clone'),
    url(r'^surveyMethodology/(?P<projectNo>.*)', views.get_survey_methodology, name='clone'),
    url(r'^usefulInfo/(?P<projectNo>.*)', views.get_useful_info, name='clone'),
    url(r'^saveProject', views.save_count_point_info, name='save'),
    url(r'^saveData', views.save_project_data, name='save'),
    url(r'^saveNetworkInfo', views.save_network_info, name='save')
]