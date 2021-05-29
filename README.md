# drf-auth

Painless token authentication for django restframework. Built on top of rest_framework.auth_token. It's meant to provide a ready to use authentication for your **SPAs** and other **Mobile Apps**

[![Build Status](https://travis-ci.com/abiiranathan/drf-authtoken.svg?branch=master)](https://travis-ci.com/abiiranathan/drf-authtoken)


## Installation
```bash pip install drf-restauth```

## Homepage
The project homepage on: [Github](https://github.com/abiiranathan/drf-authtoken)


### Usage
```python
INSTALLED_APPS=[
    'rest_framework',
    'rest_framework.authtoken',
    'drf_auth'
]
```

Configure project urls.py:

Subsequent examples assume, you are using "/api/auth/ as the path prefix.

```python
urlpatterns = [
    path("api/auth/", include("drf_auth.urls"))
]

# settings.py

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ]
}

# drf-specific settings for password reset

DRF_AUTH_SETTINGS = {
    "SITE_NAME": "My Site Title",
    "PASSWORD_RESET_REDIRCT_URL": "/",
    "PASSWORD_CHANGE_TEMPLATE": "drf_auth/password_change_form.html",
    "EMAIL_HOST_USER": "youremail@gmail.com",
    "EMAIL_HOST_PASSWORD": "yourpassword",
    "EMAIL_HOST": "smtp.gmail.com",
    "EMAIL_PORT": 587,
}

```

**These settings can be ignored if you don't plan to do password reset by email!**

Endpoints:

1. ```/POST api/auth/register/```


```json
{
    "username": "string",
    "password":"string",
    "email":"string",
    "first_name": "string",
    "last_name":"string"
}

response:{
    "token": "string",
    "user":{
        "username": "string",
        "password":"string",
        "email":"string",
        "first_name": "string",
        "last_name":"string"
    }
}
```

2. ```/POST api/auth/login/```
   
```json
body:
{
    "username": "string",
    "password":"string"
}

response:{
    "token": "string",
    "user":{
        "username": "string",
        "password":"string",
        "email":"string",
        "first_name": "string",
        "last_name":"string"
    }
}
```

3. ```/POST api/auth/logout/```
```
body: null
response:{
    "success": true
}
```

4. ```/GET api/auth/user/ (Protected Route)```

```json
response:
{
    "username": "string",
    "password":"string",
    "email":"string",
    "first_name": "string",
    "last_name":"string"
}
```

5. ```GET /api/auth/users (Protected route, must be admin)```
- Retrieves a json array of all users unpaginated

6. ```/api/auth/update-user/ (Protected route)```

```json

body:{
    "email":"string",
    "first_name": "string",
    "last_name":"string"
}

response:
{
    "username": "string",
    "password":"string",
    "email":"string",
    "first_name": "string",
    "last_name":"string"
}

```

7. ```POST /api/auth/change-password/ (Protected route)```

```json

body:{
    "old_password":"string",
    "new_password": "string",
}

response:
{
    "username": "string",
    "password":"string",
    "email":"string",
    "first_name": "string",
    "last_name":"string"
}

```

8. ```POST /api/auth/reset-password/```

For restting forgotten passwords. An email will be sent
using the settings provided in settings.DRF_AUTH_SETTINGS
dictionary.

```json

body:{
    "email":"string",
}

status: 200 - OK(Email sent)
status: 400 - Email not sent
status: 500 - Internal server error

response:
{
    "message": "string"
}

```

### Handle user email confirmation

9. ```/GET /api/auth/reset_password_confirmation/<uidb64>/<token>/"

This route handles navigations/get requests when the user clicks the password reset link.

For a complete workflow, provide a template to render in DRF_AUTH_SETTINGS(see above) and make sure that
the new password is **POSTED** to the same route.

The following variables are passed to you in the context for customization:
 - user
 - site_name


1.  ```/POST /api/auth/reset_password_confirmation/<uidb64>/<token>/```

**Note that the token expires after 30 minutes after the email is sent**

```json

body:
{
    "password": "string"
}

```

### Required Headers
- Authorization: Token xxxxxxxx (required for protected routes)
- Content-Type: application/json
- X-Requested-With: XMLHttpRequest (Desirable)

### Practical examples using typescript

```ts
import axios from "axios";


// Add content-type header on every request
axios.interceptors.request.use(function (config) {
  const token = localStorage.getItem("token");

  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }

  config.headers["Content-Type"] = "application/json";
  return config;
});

const handleLogin = async (username:string, password:string)=>{
    const body = JSON.stringify({
        username,
        password
    });

    const res = await axios.post("/api/auth/login/", body);
    const {user, token} = res.data;

    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));
}

interface User{
    username:string,
    first_name:string,
    last_name:string,
    password:string,
    email:string
}

const handleRegister = async (user:User):Promise<User> =>{
    const body = JSON.stringify(user);

    const res = await axios.post("/api/auth/login/", body);
    const {user, token} = res.data;

    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));
    return user
}

type LogoutResponse = {
    success: boolean
}

const handleLogout = ():Promise<LogoutResponse>=>{
    const res = await axios.post("/api/auth/logout/", null)
    return res.data
}

const getLoggedInUser = ():Promise<User>=>{
    const res = await axios.get("/api/auth/user/")
    return res.data
}
```

Submit an issue at [Github](https://github.com/abiiranathan/drf-authtoken/issues "Click to submit an issue")

Feel free to add your voice but be gentle, this is my first open source Django package!
