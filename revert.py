path = 'frontend/dist/assets/index-2lvChEfV.js'
with open(path, 'r') as f:
    text = f.read()

new_str = "function ot({children:n}){const{userData:s}=en(),a=Qt();if(!s){window._auth_wait=(window._auth_wait||0)+1;if(window._auth_wait<30)return null;}return s?n:o.jsx(mt,{to:\"/signin/\",replace:!0,state:{from:`${a.pathname}${a.search}`}})}"
orig = "function ot({children:n}){const{userData:s}=en(),a=Qt();return s?n:o.jsx(mt,{to:\"/signin/\",replace:!0,state:{from:`${a.pathname}${a.search}`}})}"

if new_str in text:
    text = text.replace(new_str, orig)
    with open(path, 'w') as f:
        f.write(text)
    print("Reverted patch!")
else:
    print("Patch not found.")
