from django.conf.urls import url

from . import views

urlpatterns = [

    ###
    ### admin sign off app endpoints
    ###
    url(r'^projectsList', views.get_projects_list, name='get projects list'),
    url(r'^searchProject', views.search_for_project, name='search for project'),
    url(r'^viewProject/(?P<projectNo>.*)', views.view_project, name='view project'),
    url(r'^saveAdminChangesToProject', views.save_admin_changes_to_project_data, name='view project'),




    ###
    ### nutshell app endpoints
    ###

    url(r'^projects/(?P<projectNo>.*)', views.get_count_point_data, name='clone'),
    url(r'^networkInfo/(?P<projectNo>.*)', views.get_network_info, name='clone'),
    url(r'^surveyMethodology/(?P<projectNo>.*)', views.get_survey_methodology, name='clone'),
    url(r'^usefulInfo/(?P<projectNo>.*)', views.get_useful_info, name='clone'),
    url(r'^saveProject', views.save_count_point_info, name='save'),
    url(r'^saveData', views.save_project_data, name='save'),
    url(r'^uploadProjectData', views.save_project_data, name='save'),
    url(r'^saveNetworkInfo', views.load_schedule_from_excel, name='save')

]