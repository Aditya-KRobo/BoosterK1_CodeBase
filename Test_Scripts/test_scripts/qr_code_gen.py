import qrcode

data = "Dragon"
img = qrcode.make(data)
img.save("~Workspace/BoosterK1_CodeBase/Test_Scripts/res/dragon.png")