import pya
import os


path = "/Users/ycn/Desktop/LayoutDesign"
os.chdir(path)


def open_layout(layout_name):

    # Open the KLayout application
    app = pya.Application.instance()
    main_window = app.main_window()
    view_index = main_window.create_view()
    cv = main_window.view(view_index)
    cv.load_layout(layout_name)

    return app, main_window, cv

def setup_image(cv, image_path, rotation, x_center, y_center, micron_conversion_factor=0.28990):
    
    image_raw = pya.Image().new(image_path)
    t = pya.CplxTrans.new(micron_conversion_factor, rotation, False, x_center, y_center)
    image = image_raw.transformed(t)
    cv.insert_image(image)
    return image


layout_name = "L0LONG.gds"
app, main_window, cv = open_layout(layout_name)


img_path = 'noisy.jpg'
setup_image(cv=cv, image_path=img_path, rotation=0, x_center=0, y_center=0)






