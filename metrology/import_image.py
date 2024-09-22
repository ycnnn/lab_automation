import pya
import os
import json
path = "/Users/ycn/Desktop/LayoutDesign"
os.chdir(path)


def open_layout(layout_name):

    app = pya.Application.instance()
    main_window = app.main_window()
    view_index = main_window.create_view()
    cv = main_window.view(view_index)
    cv.load_layout(layout_name)
    return app, main_window, cv

def setup_image(cv, image_path, magification_text_identifier='100x'):

    
    mag = 100 if magification_text_identifier in image_path else 10
    micron_conversion_factor = 0.29072 * 10 / mag
    
    # transform_params = np.load(img_path.split('.')[0] + '.npy')
    with open(img_path.split('.')[0] + '.json', 'r') as file:
        transform_params = json.load(file)
    x_center, y_center, rotation = transform_params
    
    image_raw = pya.Image().new(image_path)
    t = pya.CplxTrans.new(micron_conversion_factor, rotation, False, x_center, y_center)    
    image = image_raw.transformed(t)
    cv.insert_image(image)
    return image


layout_name = "L0LONG.gds"
app, main_window, cv = open_layout(layout_name)


img_path = 'clean.jpg'
setup_image(cv=cv, 
            image_path=img_path, )

            
# img_path = 'noisy.jpg'
# setup_image(cv=cv, 
#             image_path=img_path, 
#             rotation=1.29686366, 
#             x_center=-927.38361082, y_center=12884.86185968)
            
# img_path = '100x.jpg'
# setup_image(cv=cv, 
#             image_path=img_path, 
#             rotation= 2.6630008220672607, 
#             x_center=-5550.869002235031, y_center=-22243.621066253218,
#             micron_conversion_factor=0.02907)





