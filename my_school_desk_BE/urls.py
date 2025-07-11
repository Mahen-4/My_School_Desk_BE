"""
URL configuration for my_school_desk_BE project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core_admin.views import admin_action_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('creation-admin-action/', admin_action_view, name='msd-admin-action'),
    path('test-admin-action/', admin_action_view),
    path('auth/', include(("custom_auth.urls", "custom_auth"), "custom_auth")),
    path('',include(("school.urls", "school"), "school")),
    path('',include(("works.urls", "works"), "works")),
    path('',include(("grades.urls", "grades"), "grades")),
    path('',include(("quiz.urls", "quiz"), "quiz")),
    
    
]
