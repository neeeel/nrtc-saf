from django.conf.urls import url

from . import views

urlpatterns = [

    ###
    ### admin sign off app endpoints
    ###
    url(r'^projectMap', views.view_all_projects, name='get projects list'),
    url(r'^getProjectMap', views.get_project_map, name='get projects list'),
    url(r'^downloadPdf', views.download_pdf, name='get projects list'),
    url(r'^sign', views.sign_survey, name='get projects list'),
    url(r'^finish', views.finish_survey, name='get projects list'),
    url(r'^supervisor', views.get_projects_list, name='get projects list'),
    url(r'^getNetworkInfo', views.get_networkInfo, name='get projects list'),
    url(r'^getItemsOfInterest', views.get_items_of_interest, name='get projects list'),
    url(r'^saveItemsOfInterest', views.save_items_of_interest, name='get projects list'),
    url(r'^searchProject', views.search_for_project, name='search for project'),
    url(r'^searchRoadworks', views.search_for_roadworks, name='search for project'),
    url(r'^getColumnValues', views.get_column_values, name='search for project'),
    url(r'^filter', views.update_projects_list, name='search for project'),
    url(r'^viewProject/(?P<projectNo>.*)', views.view_project, name='view project'),





    ###
    ### nutshell app endpoints
    ###
    url(r'^saf', views.saf, name='convert'),
    url(r'^logon', views.index, name='convert'),
    url(r'^choices', views.view_choices, name='convert'),
    url(r'^homeSafe', views.home_safe, name='convert'),
    url(r'^markAsHomeSafe', views.mark_home_safe, name='convert'),
    url(r'^map', views.get_map, name='convert'),
    url(r'^projects/(?P<projectNo>.*)', views.get_count_point_data, name='clone'),
    url(r'^surveyMethodology/(?P<projectNo>.*)', views.get_survey_methodology, name='clone'),
    url(r'^usefulInfo/(?P<projectNo>.*)', views.get_useful_info, name='clone'),
    url(r'^saveNetworkInfo', views.save_network_info, name='save'),
    url(r'^saveData', views.save_project_data, name='save'),
    url(r'^uploadProjectData', views.save_project_data, name='save'),
    url(r'^updateScheduleFromClientFile', views.update_schedule_from_client_file, name='save')

]