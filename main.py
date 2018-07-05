# coding=UTF-8

def get_corridor_lut():
        # Console version
    CORRIDOR_LUT = {'usd_ntd' : True,
                    'usd_thb' : True,
                    'usd_khr' : True,
                    'usd_cny' : True,
                    'usd_php' : True,
                    'usd_inr' : True,
                    'usd_idr' : True}
    return CORRIDOR_LUT

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process arguments.')
    parser.add_argument('-s', default='usd', dest='src', help='Source currency, default:usd')
    parser.add_argument('-d', default='ntd', dest='dst', help='Destination currency, default:ntd')
    parser.add_argument('-app', default=False, type=bool, dest='app', help='Run as web app')
    args = parser.parse_args()
    
    corridorName = args.src + '_' + args.dst

    if args.app:
        from app import start_app
        start_app()
    else:
        lut = get_corridor_lut()
        if lut.get(corridorName, False):
            corridor = __import__(corridorName)
            corridor.get_current_forex_price()