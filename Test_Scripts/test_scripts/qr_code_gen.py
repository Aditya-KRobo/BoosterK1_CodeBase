import qrcode

data = "Crocodile"
img = qrcode.make(data)
img.save("/home/booster/Workspace/BoosterK1_CodeBase/Test_Scripts/res/qrcodes/Crocodile.png")