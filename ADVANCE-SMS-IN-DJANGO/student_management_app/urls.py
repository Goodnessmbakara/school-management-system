
from django.urls import include, path

from . import HodViews, StaffViews, StudentViews, WebsiteViews, views

urlpatterns = [
    path('', WebsiteViews.home, name="home"),
    path('login/', views.loginPage, name="login"),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('doLogin/', views.doLogin, name="doLogin"),
    path('get_user_details/', views.get_user_details, name="get_user_details"),
    path('logout_user/', views.logout_user, name="logout_user"),
    path('admin_home/', HodViews.admin_home, name="admin_home"),
    path('add_staff/', HodViews.add_staff, name="add_staff"),
    path('manage_staff/', HodViews.manage_staff, name="manage_staff"),
    path('edit_staff/<staff_id>/', HodViews.edit_staff, name="edit_staff"),
    path('edit_staff_save/', HodViews.edit_staff_save, name="edit_staff_save"),
    path('delete_staff/<staff_id>/', HodViews.delete_staff, name="delete_staff"),
    path('sessions/search/', HodViews.search_sessions, name='search_sessions'),
    path('manage_session/', HodViews.manage_session, name="manage_session"),
    path('add_session/', HodViews.add_session, name="add_session"),
    path('add_session_save/', HodViews.add_session_save, name="add_session_save"),
    path('edit_session/<session_id>', HodViews.edit_session, name="edit_session"),
    path('edit_session_save/', HodViews.edit_session_save, name="edit_session_save"),
    path('delete_session/<session_id>/', HodViews.delete_session, name="delete_session"),
    path('add_student/', HodViews.add_student, name="add_student"),
    #path('add_student_save/', HodViews.add_student_save, name="add_student_save"),
    path('edit_student/<student_id>', HodViews.edit_student, name="edit_student"),
    path('edit_student_save/', HodViews.edit_student_save, name="edit_student_save"),
    path('manage_student/', HodViews.manage_student, name="manage_student"),
    path('delete_student/<student_id>/', HodViews.delete_student, name="delete_student"),
    path('add_subject/', HodViews.add_subject, name="add_subject"),
    path('manage_subject/', HodViews.manage_subject, name="manage_subject"),
    path('manage_subject/<int:class_id>/', HodViews.manage_subject, name="manage_this_subject"),
    path('edit_subject/<subject_id>/', HodViews.edit_subject, name="edit_subject"),
    path('edit_subject_save/', HodViews.edit_subject_save, name="edit_subject_save"),
    path('delete_subject/<subject_id>/', HodViews.delete_subject, name="delete_subject"),
    path('manage_this_subject/<int:subject_id>/', HodViews.manage_this_subject, name='manage_this_subject'),
    path('delete_subclass_subject/<int:subclass_subject_id>/', HodViews.delete_subclass_subject, name='delete_subclass_subject'),
    path('check_email_exist/', HodViews.check_email_exist, name="check_email_exist"),
    path('check_username_exist/', HodViews.check_username_exist, name="check_username_exist"),
    path('student_feedback_message/', HodViews.student_feedback_message, name="student_feedback_message"),
    path('student_feedback_message_reply/', HodViews.student_feedback_message_reply, name="student_feedback_message_reply"),
    path('staff_feedback_message/', HodViews.staff_feedback_message, name="staff_feedback_message"),
    path('staff_feedback_message_reply/', HodViews.staff_feedback_message_reply, name="staff_feedback_message_reply"),
    path('student_leave_view/', HodViews.student_leave_view, name="student_leave_view"),
    path('student_leave_approve/<leave_id>/', HodViews.student_leave_approve, name="student_leave_approve"),
    path('student_leave_reject/<leave_id>/', HodViews.student_leave_reject, name="student_leave_reject"),
    path('staff_leave_view/', HodViews.staff_leave_view, name="staff_leave_view"),
    path('staff_leave_approve/<leave_id>/', HodViews.staff_leave_approve, name="staff_leave_approve"),
    path('staff_leave_reject/<leave_id>/', HodViews.staff_leave_reject, name="staff_leave_reject"),
    path('admin_view_attendance/', HodViews.admin_view_attendance, name="admin_view_attendance"),
    path('admin_get_attendance_dates/', HodViews.admin_get_attendance_dates, name="admin_get_attendance_dates"),
    path('admin_get_attendance_student/', HodViews.admin_get_attendance_student, name="admin_get_attendance_student"),
    path('admin_profile/', HodViews.admin_profile, name="admin_profile"),
    path('admin_profile_update/', HodViews.admin_profile_update, name="admin_profile_update"),
    #URLS for for classes management
    path('get_classes_for_level/', HodViews.get_classes_for_level, name='get_classes_for_level'),
    #path('get-subclasses-for-class/', HodViews.get_subclasses_for_class, name='get-subclasses-for-class'),
    path('add_class/', HodViews.add_class, name="add_class"),
    path('add_class_save/', HodViews.add_class_save, name="add_class_save"),
    path('manage_class/', HodViews.manage_class, name="manage_class"),
    path('edit_class/<class_id>/', HodViews.edit_class, name="edit_class"),
    path('delete_class/<class_id>/', HodViews.delete_class, name="delete_class"),
    path('classes/<int:class_id>/subclasses/', HodViews.manage_subclass, name='manage_subclass'),
    path('subclasses/add/<int:class_id>/', HodViews.add_subclass, name='add_subclass'),
    path('subclasses/<int:subclass_id>/edit/', HodViews.edit_subclass, name='edit_subclass'),
    path('get-subclasses/<int:class_id>/', HodViews.get_subclasses, name='get_subclasses'),
    path('get-subclasses-for-class/', HodViews.get_subclasses_for_class, name='get_subclasses_for_class'),
    path('get_classes_or_subclasses/', HodViews.get_classes_or_subclasses, name = 'get-classes-or-subclasses'),
    path('get-classes-for-level/', HodViews.get_classes_for_levels, name='get-classes-for-level'),
    path('get-subclasses-for-class/', HodViews.get_subclasses_for_classs, name='get-subclasses-for-class'),
    path('check_subclass_existence/<int:class_id>/', HodViews.check_subclass_existence, name='check-subclass-existence'),
    path('subclasses/<int:subclass_id>/delete/', HodViews.delete_subclass, name='delete_subclass'),
    #URLS FOR  managing grades by admin
    path('grades/add/', HodViews.add_grade, name='add_grade'),
    path('grades/edit/<int:grade_id>/', HodViews.edit_grade, name='edit_grade'),
    path('grades/delete/<int:grade_id>/', HodViews.delete_grade, name='delete_grade'),
    path('grades/manage/', HodViews.manage_grades, name='manage_grades'),
    path('grades/search/', HodViews.search_grades, name='search_grades'),
    # URLS for Staff
    path('staff_home/', StaffViews.staff_home, name="staff_home"),
    path('staff_take_attendance/', StaffViews.staff_take_attendance, name="staff_take_attendance"),
    path('get_students/', StaffViews.get_students, name="get_students"),
    path('save_attendance_data/', StaffViews.save_attendance_data, name="save_attendance_data"),
    path('staff_update_attendance/', StaffViews.staff_update_attendance, name="staff_update_attendance"),
    path('get_attendance_dates/', StaffViews.get_attendance_dates, name="get_attendance_dates"),
    path('get_attendance_student/', StaffViews.get_attendance_student, name="get_attendance_student"),
    path('update_attendance_data/', StaffViews.update_attendance_data, name="update_attendance_data"),
    path('staff_apply_leave/', StaffViews.staff_apply_leave, name="staff_apply_leave"),
    path('staff_apply_leave_save/', StaffViews.staff_apply_leave_save, name="staff_apply_leave_save"),
    path('staff_feedback/', StaffViews.staff_feedback, name="staff_feedback"),
    path('staff_feedback_save/', StaffViews.staff_feedback_save, name="staff_feedback_save"),
    path('staff_profile/', StaffViews.staff_profile, name="staff_profile"),
    path('staff_profile_update/', StaffViews.staff_profile_update, name="staff_profile_update"),
    path('staff_add_result/', StaffViews.staff_add_result, name="staff_add_result"),
    path('staff_add_result_save/', StaffViews.staff_add_result_save, name="staff_add_result_save"),

    # URSL for Student
    path('student_home/', StudentViews.student_home, name="student_home"),
    path('student_view_attendance/', StudentViews.student_view_attendance, name="student_view_attendance"),
    path('student_view_attendance_post/', StudentViews.student_view_attendance_post, name="student_view_attendance_post"),
    path('student_apply_leave/', StudentViews.student_apply_leave, name="student_apply_leave"),
    path('student_apply_leave_save/', StudentViews.student_apply_leave_save, name="student_apply_leave_save"),
    path('student_feedback/', StudentViews.student_feedback, name="student_feedback"),
    path('student_feedback_save/', StudentViews.student_feedback_save, name="student_feedback_save"),
    path('student_profile/', StudentViews.student_profile, name="student_profile"),
    path('student_profile_update/', StudentViews.student_profile_update, name="student_profile_update"),
    path('student_view_result/', StudentViews.student_view_result, name="student_view_result"),
]
