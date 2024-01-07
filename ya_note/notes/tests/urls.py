from django.urls import reverse


NOTE_SLUG = 'Slug'
# NOTE_SLUG = ''
EMPTY_NOTE_SLUG = ''

NOTES_ADD = reverse('notes:add')
NOTES_DELETE = reverse('notes:delete', args=(NOTE_SLUG,))
NOTES_DETAIL = reverse('notes:detail', args=(NOTE_SLUG,))
NOTES_EDIT = reverse('notes:edit', args=(NOTE_SLUG,))
NOTES_HOME = reverse('notes:home')
NOTES_LIST = reverse('notes:list')
NOTES_SUCCESS = reverse('notes:success')

USERS_LOGIN = reverse('users:login')
USERS_LOGOUT = reverse('users:logout')
USERS_SIGNUP = reverse('users:signup')

# NOTES_ADD = 'add/'
# NOTES_DELETE = 'delete/' + NOTE_SLUG + '/'
# NOTES_DETAIL = 'detail/' + NOTE_SLUG + '/'
# NOTES_EDIT = 'edit/' + NOTE_SLUG + '/'
# NOTES_HOME = ''
# NOTES_LIST = 'notes/'
# NOTES_SUCCESS = 'done/'

# USERS_LOGIN = 'auth/login/'
# USERS_LOGOUT = 'auth/logout/'
# USERS_SIGNUP = 'auth/signup/'
