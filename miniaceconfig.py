'''
MiniAcePlayer configuration script
'''

class MiniAceConfig(object):
    # ----------------------------------------------------
    # configuration
    # ----------------------------------------------------
    #
    # Ace Stream API key (None uses remote key generator)
    # You probably shouldn't touch this
    acekey = None
    #acekey = 'kjYX790gTytRaXV04IvC-xZH3A18sj5b1Tf3I-J5XVS1xsj-j0797KwxxLpBl26HPvWMm'
    # Ace Stream Engine host
    # Change this if you use remote Ace Stream Engine
    # Remember that by default Ace Stream Engine listens only
    # Local host, so start it with --bind-all parameter
    acehost = 'localhost'
    # Ace Stream Engine port (autodetect for Windows)
    aceport = 62062
    # Ace Stream age parameter (LT_13, 13_17, 18_24, 25_34, 35_44, 45_54,
    # 55_64, GT_65)
    aceage = 3
    # Ace Stream sex parameter (MALE or FEMALE)
    acesex = 1
    # Ace Stream Engine connection timeout
    aceconntimeout = 5
    # Ace Stream Engine authentication result timeout
    aceresulttimeout = 10
    # Ace Stream Engine timeout value when waiting for buffering to progress
    acebuffernoprogresstimeout = 70
    # external player to use
    aceplayer = 'vlc-wrapper'
