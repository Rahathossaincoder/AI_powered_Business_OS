# Merge these into your existing config/settings.py (do not replace the file).

INSTALLED_APPS += [
    "rest_framework",
    "corsheaders",
]

# CorsMiddleware must be listed as high as possible, before CommonMiddleware.
MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")

CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]  # the Vite dev server

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",  # DEV ONLY: remove when login issues real tokens
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}

# In your root urls.py:
#   from django.urls import include, path
#   urlpatterns += [path("api/", include("catalog.urls"))]
