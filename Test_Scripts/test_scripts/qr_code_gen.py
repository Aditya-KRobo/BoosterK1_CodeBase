import qrcode

data = "Dragon"
img = qrcode.make(data)
img.save("Dragon.png")