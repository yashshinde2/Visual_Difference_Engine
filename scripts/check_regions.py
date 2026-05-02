from PIL import Image
import glob
for p in glob.glob('backend/backend/outputs/*region*.png'):
    try:
        im=Image.open(p)
        print(p, im.size, im.mode)
    except Exception as e:
        print('ERR',p,e)
