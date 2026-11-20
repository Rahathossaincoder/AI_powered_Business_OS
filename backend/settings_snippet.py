# Merge these into an existing Django settings module if reusing the catalog app.
# This repository already includes these settings in config/settings.py.

INSTALLED_APPS += [
    "rest_framework",
    "corsheaders",
]

# CorsMiddleware must be listed before CommonMiddleware.
MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")

CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]  # the Vite dev server

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}

# The custom User model uses `user_id` as its primary key.
SIMPLE_JWT = {
    "USER_ID_FIELD": "user_id",
    "USER_ID_CLAIM": "user_id",
}

# Add the JWT endpoints to your root urls.py:
#   from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
#   urlpatterns += [
#       path("api/auth/token/", TokenObtainPairView.as_view()),
#       path("api/auth/token/refresh/", TokenRefreshView.as_view()),
#       path("api/", include("catalog.urls")),
#   ]
