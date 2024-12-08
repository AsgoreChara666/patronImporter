# How to use?

1. Create a "keys.py" in folder, example like this:
```
#FANBOXSESSID in cookie
fanbox = ""

#_session_id in cookie
fantia = ""

#token in local storage
unifans = ""

#auth_token in cookie
afdian = ""
```

2. Use it as you want, example like this:
```
import fanbox

print(fanbox.run(
    "msmspc", //Creator ID

    0         //Post type that you need
              //0: all post
              //1: paid post only
))
```
