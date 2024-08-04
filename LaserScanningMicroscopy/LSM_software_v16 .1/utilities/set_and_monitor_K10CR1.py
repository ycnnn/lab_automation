from external_instrument_drivers.K10CR1 import K10CR1_stage

if __name__ == '__main__':


    stage = K10CR1_stage(serial_no=55425494)
    stage.initialize_instrument()

    stage.home_device()
    stage.move(30)

    stage.quit()