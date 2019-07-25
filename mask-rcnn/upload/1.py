import base64
p_name=1 
with open("tulip.jpg", "rb") as imageFile:
    str = base64.b64encode(imageFile.read())
    print(str)
p_name=p_name+1
with open("%03d.jpg"%p_name, "wb") as f:
    #f.write(base64.b64decode(str[n+1]))
    f.write(base64.b64decode(str))