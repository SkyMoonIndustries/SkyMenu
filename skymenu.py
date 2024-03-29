#!/usr/bin/python3

# SkyMoon Industries Raspberry Pi Project Center
# -*- coding:utf-8 -*-


#imports 
from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.core.sprite_system import framerate_regulator
from luma.core import lib
from luma.oled.device import sh1106
import RPi.GPIO as GPIO
import datetime, time, subprocess
from PIL import Image, ImageDraw, ImageFont
import socket, sys, os, base64, struct, smbus, io, random
from contextlib import redirect_stdout

SCNTYPE = 1 # 1= OLED #2 = TERMINAL MODE BETA TESTS VERSION
bus = smbus.SMBus(1)  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
GPIO.setwarnings(False)


# Load default font.
font = ImageFont.load_default()
# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = 128
height = 64
image = Image.new('1', (width, height))
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
line1 = top
line2 = top+8
line3 = top+16
line4 = top+25
line5 = top+34
line6 = top+43
line7 = top+52
brightness = 255 #Max
fichier=""
# Move left to right keeping track of the current x position for drawing shapes.
x = 0
RST = 25
CS = 8
DC = 24

#GPIO define and OLED configuration
RST_PIN        = 25 #waveshare settings
CS_PIN         = 8  #waveshare settings
DC_PIN         = 24 #waveshare settings
KEY_UP_PIN     = 6  #stick up
KEY_DOWN_PIN   = 19 #stick down
KEY_LEFT_PIN   = 5      #5  #sitck left // go back
KEY_RIGHT_PIN  = 26 #stick right // go in // validate
KEY_PRESS_PIN  = 13 #stick center button
KEY1_PIN       = 21 #key 1 // up
KEY2_PIN       = 20  #20 #key 2 // cancel/goback
KEY3_PIN       = 16 #key 3 // down
USER_I2C = 0        #set to 1 if your oled is I2C or  0 if use SPI interface
#init GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(KEY_UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Input with pull-up
GPIO.setup(KEY_DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY_PRESS_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
screensaver = 0
#SPI
#serial = spi(device=0, port=0, bus_speed_hz = 8000000, transfer_size = 4096, gpio_DC = 24, gpio_RST = 25)
if SCNTYPE == 1:
    if  USER_I2C == 1:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RST,GPIO.OUT)
        GPIO.output(RST,GPIO.HIGH)
        serial = i2c(port=1, address=0x3c)
    else:
        serial = spi(device=0, port=0, bus_speed_hz = 8000000, transfer_size = 4096, gpio_DC = 24, gpio_RST = 25)
if SCNTYPE == 1:
    device = sh1106(serial, rotate=2) #sh1106

def DisplayText(l1,l2,l3,l4,l5,l6,l7):
    # simple routine to display 7 lines of text
    if SCNTYPE == 1:
        with canvas(device) as draw:
            draw.text((0, line1), l1,  font=font, fill=255)
            draw.text((0, line2), l2, font=font, fill=255)
            draw.text((0, line3), l3,  font=font, fill=255)
            draw.text((0, line4), l4,  font=font, fill=255)
            draw.text((0, line5), l5, font=font, fill=255)
            draw.text((0, line6), l6, font=font, fill=255)
            draw.text((0, line7), l7, font=font, fill=255)
    if SCNTYPE == 2:
            os.system('clear')
            print(l1)
            print(l2)
            print(l3)
            print(l4)
            print(l5)
            print(l6)
            print(l7)

def switch_menu(argument):
    switcher = {
        0: "_Connection Settings",
        1: "_**testing**",
        2: "_",
        3: "_",
        4: "_Screen OFF",
        5: "_System Settings",
        6: "_Power",
        7: "_System info", #menu 1 (System Menu)
        8: "_OLED brightness",
        9: "_Key Test",
        10: "_",
        11: "_",
        12: "_",
        13: "_",
        14: "_show Logo", # menu 2 (Testing Menu)
        15: "_sys infos",
        16: "_update",
        17: "_",
        18: "_",
        19: "_",
        20: "_",
        21: "_go blank", # menu 3
        22: "_",
        23: "_",
        24: "_",
        25: "_",
        26: "_",
        27: "_",
        28: "_go blank", # menu 4
        29: "_",
        30: "_",
        31: "_",
        32: "_",
        33: "_",
        34: "_",
        35: "_About", # menu 5
        36: "_",
        37: "_",
        38: "_",
        39: "_",
        40: "_",
        41: "_",
        42: "_Restart GUI", # menu 6 (Power)
        43: "_Reboot Device",
        44: "_Shutdown Device",
        45: "_",
        46: "_",
        47: "_",
        48: "_",
        49: "_SSH Settings", # menu 7 (Connection Settings)
        50: "_VNC Settings",
        51: "_",
        52: "_",
        53: "_",
        54: "_",
        55: "_",
        56: "_Start SSH", # menu 8 (SSH Settings)
        57: "_Stop SSH",
        58: "_Credentials",
        59: "_",
        60: "_",
        61: "_",
        62: "_",
        63: "_Start VNC (testing)", # menu 9 (VNC Settings)
        64: "_Stop VNC",
        65: "_Credentials",
        66: "_",
        67: "_",
        68: "_",
        69: "_",

}
    return switcher.get(argument, "Invalid")

#system information sub routine
def sysinfos():
    while GPIO.input(KEY_LEFT_PIN):
          
        cmd = "hostname -I"  
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        IP = ps.communicate()[0].decode('utf-8').strip()  
   
        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"  
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        CPU = ps.communicate()[0].decode('utf-8').strip()  
   
        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"  
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        MemUsage = ps.communicate()[0].decode('utf-8').strip()  
   
        cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"  
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        Disk = ps.communicate()[0].decode('utf-8').strip()  
   
        cmd = """/sbin/ifconfig wlan0 | grep "RX packets" | awk '{print $6" " $7}' | sed 's/[()]//g'"""  
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        network_rx = ps.communicate()[0].decode('utf-8').strip()  
   
        cmd = """/sbin/ifconfig wlan0 | grep "TX packets" | awk '{print $6" " $7}' | sed 's/[()]//g'"""  
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        network_tx = ps.communicate()[0].decode('utf-8').strip()    
   
        cmd = "date '+%Y-%m-%d %H:%M:%S'"  
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        date_time = ps.communicate()[0].decode('utf-8').strip()  
   
        cmd = "vcgencmd measure_temp | sed 's/temp=//g'"  
        ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)  
        temp = ps.communicate()[0].decode('utf-8').strip()  

# system information page
        DisplayText(
           "" + str(CPU),
           "" + str(MemUsage),
           "" + str(Disk),
           "Temp: " + str(temp),
           " ",
           "IP: " + str(IP),
           " " + str(network_rx) + "/" + str(network_tx),
            )
        time.sleep(0.1)

# OLED contrast page
def OLEDContrast(contrast):
    #set contrast 0 to 255
    if SCNTYPE == 1:
        while GPIO.input(KEY_LEFT_PIN):
            #loop until press left to quit
            with canvas(device) as draw:
                if GPIO.input(KEY_UP_PIN): # button is released
                        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  #Up
                else: # button is pressed:
                        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=1)  #Up filled
                        contrast = contrast +5
                        if contrast>255:
                            contrast = 255

                if GPIO.input(KEY_DOWN_PIN): # button is released
                        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0) #down
                else: # button is pressed:
                        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=1) #down filled
                        contrast = contrast-5
                        if contrast<0:
                            contrast = 0
                device.contrast(contrast)
                draw.text((54, line4), "Value : " + str(contrast),  font=font, fill=255)
    return(contrast)        

def about():
    # Main IP Address (WiFi)
    cmd = "hostname -I | cut -d\' \' -f1"
    ips = subprocess.run(
    cmd, shell=True, capture_output=True, check=True, universal_newlines=True)
    ipout = (ips.stdout)
    # secondary IP address (ETH0)
    cmd = "hostname -I"
    ipeth = subprocess.run(
    cmd, shell=True, capture_output=True, check=True, universal_newlines=True)
    eth = (ipeth.stdout).split(" ")[1]
    # simple sub routine to show an About
    DisplayText(
        "  SkyMoon Industries",
        "      SkyMenu",
        "    EXPERIMENTAL",
        "",
        " IP: " + str(ipout),
        "Eth: " + str(eth),
        "",

        )
    while GPIO.input(KEY_LEFT_PIN):
        #wait
        menu = 1
        page = 0

def blank():
    # simple sub routine to show a page
    DisplayText(
        " ",
        " : blank for test :",
        " ",
        " ",
        " ",
        " ",
        " "
        )
    while GPIO.input(KEY_LEFT_PIN):
        #wait
        menu = 1
        page = 0


def logo():

    img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'images', 'skymoon.bmp'))
    logo = Image.open(img_path) \
        .transform((device.width, device.height), Image.AFFINE, (1, 0, 0, 0, 1, 0), Image.BILINEAR) \
        .convert(device.mode)
    device.display(logo)

    while GPIO.input(KEY_LEFT_PIN):
        #wait
        menu = 3
        page = 0
        #wait


def splash():
    img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'images', 'skymoon.bmp'))
    splash = Image.open(img_path) \
        .transform((device.width, device.height), Image.AFFINE, (1, 0, 0, 0, 1, 0), Image.BILINEAR) \
        .convert(device.mode)
    device.display(splash)
    time.sleep(5) #5 sec splash boot screen


def ScreenOFF():
    #put screen off until press left
    if SCNTYPE == 1:
        while GPIO.input(KEY_LEFT_PIN):
            device.hide()
            time.sleep(0.1)
        device.show()


def KeyTest():
    if SCNTYPE == 1:
        while GPIO.input(KEY_LEFT_PIN):
            with canvas(device) as draw:
                if GPIO.input(KEY_UP_PIN): # button is released
                        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  #Up
                else: # button is pressed:
                        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=1)  #Up filled

                if GPIO.input(KEY_LEFT_PIN): # button is released
                        draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0)  #left
                else: # button is pressed:
                        draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=1)  #left filled

                if GPIO.input(KEY_RIGHT_PIN): # button is released
                        draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0) #right
                else: # button is pressed:
                        draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=1) #right filled

                if GPIO.input(KEY_DOWN_PIN): # button is released
                        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0) #down
                else: # button is pressed:
                        draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=1) #down filled

                if GPIO.input(KEY_PRESS_PIN): # button is released
                        draw.rectangle((20, 22,40,40), outline=255, fill=0) #center 
                else: # button is pressed:
                        draw.rectangle((20, 22,40,40), outline=255, fill=1) #center filled

                if GPIO.input(KEY1_PIN): # button is released
                        draw.ellipse((70,0,90,20), outline=255, fill=0) #A button
                else: # button is pressed:
                        draw.ellipse((70,0,90,20), outline=255, fill=1) #A button filled

                if GPIO.input(KEY2_PIN): # button is released
                        draw.ellipse((100,20,120,40), outline=255, fill=0) #B button
                else: # button is pressed:
                        draw.ellipse((100,20,120,40), outline=255, fill=1) #B button filled
                        
                if GPIO.input(KEY3_PIN): # button is released
                        draw.ellipse((70,40,90,60), outline=255, fill=0) #A button
                else: # button is pressed:
                        draw.ellipse((70,40,90,60), outline=255, fill=1) #A button filled


#restart OLED UI
def restart():
    DisplayText(
    "",
    "",
    "SkyMenu updated",
    "system restarting",
    "",
    "",
    ""
    )
    time.sleep(5)
    subprocess.run(['python3','/home/skymoon/SkyMenu/skymenu.py','&'])
 #   print(stdout)
    return()   
    DisplayText(
    "",
    "",
    "SkyMenu updated",
    "system restarting",
    "",
    "",
    ""
    )                        

def rebootpi():
    DisplayText(
    "",
    "",
    "",
    "PLEASE WAIT ...",
    "",
    "",
    ""
    )
    cmd = "sudo shutdown -r now"
    reboot = subprocess.run(
    cmd, shell=True, capture_output=True, check=True, universal_newlines=True)

    DisplayText(
    "",
    "   Rebooting now",
    "",
    "",
    "  allow 5 minutes ",
    "  for device start",
    ""
    )     
    time.sleep(30)   
    return()

def shutdownpi():
    DisplayText(
    "",
    "",
    "",
    "PLEASE WAIT ...",
    "",
    "",
    ""
    )
    cmd = "sudo shutdown now"
    reboot = subprocess.run(
    cmd, shell=True, capture_output=True, check=True, universal_newlines=True)
     
    DisplayText(
    "",
    "  turning off now",
    "",
    "",
    "    wait for LED ",
    "    to turn off",
    ""
    )     
    time.sleep(30)   
    return(

    )

def update():
    subprocess.run('./update.sh', shell=True, check=True, timeout=60)
    time.sleep(90)
    restart()

def runsh():
    subprocess.run('./exp.sh', shell=True, check=True, timeout=10)

def sshstart():
    cmd = "sudo systemctl start ssh"
    subprocess.run(cmd, shell=True, check=True, timeout=15)

def sshstop():
    cmd = "sudo systemctl stop ssh"
    subprocess.run(cmd, shell=True, check=True, timeout=15)

def vncstart():
    cmd = "sudo systemctl start vnc"
    subprocess.run(cmd, shell=True, check=True, timeout=15)

def vncstop():
    cmd = "sudo systemctl stop vnc"
    subprocess.run(cmd, shell=True, check=True, timeout=15)

def credentials():
    # Main IP Address (WiFi)
    cmd = "hostname -I | cut -d\' \' -f1"
    ips = subprocess.run(
    cmd, shell=True, capture_output=True, check=True, universal_newlines=True)
    ipout = (ips.stdout)
    DisplayText(
        "  SSH Credentials",
        "",
        " IP: " + str(ipout),
        "",
        "",
        "",
        "",

        )
    while GPIO.input(KEY_LEFT_PIN):
        #wait
        menu = 1
        page = 0


######################################################## MENU SYSTEM BELOW ##################

#init vars 
curseur = 1
page=0  
menu = 1
ligne = ["","","","","","","",""]
selection = 0
if SCNTYPE == 1:
    splash()  # display boot splash image ---------------------------------------------------------------------
    device.contrast(2)
while 1:
    if GPIO.input(KEY_UP_PIN): # button is released
        menu = 1
    else: # button is pressed:
        curseur = curseur -1
        if curseur<1:
            curseur = 7     
    if GPIO.input(KEY_LEFT_PIN): # button is released
        menu = 1
    else: # button is pressed:
                # back to main menu on Page 0
        page = 0    
    if GPIO.input(KEY_RIGHT_PIN): # button is released
        menu = 1
    else: # button is pressed:
        selection = 1
    if GPIO.input(KEY_DOWN_PIN): # button is released
        menu = 1
    else: # button is pressed:
        curseur = curseur + 1
        if curseur>7:
            curseur = 1
#-----------
    if selection == 1:
        # display pages --------------------------------------------------------------
            if page == 7: # System Menu
                if curseur == 1:
                    sysinfos()
                if curseur == 2:
                    brightness = OLEDContrast(brightness)
                if curseur == 3:
                    KeyTest()
            if page == 14: # Testing Menu
                if curseur == 1:
                    logo()
                if curseur == 2:
                    sysinfos()
                if curseur == 3:
                    update()
            if page == 21: # ???
                if curseur == 1:
                   #blank page
                    logo()
            if page == 28: # ???
                    #trigger section
                if curseur == 1:
                    #blank page
                    blank()
            if page == 35: # ???
                #template section menu
                if curseur == 1:
                    #blank page
                   about()
                if curseur == 2:
                    #blank page
                    blank()
            if page == 42: # Power Menu
                if curseur == 1:
                    restart()
                if curseur == 2:
                    rebootpi()
                if curseur == 3:
                    shutdownpi()
            if page == 49: # Connection Menu
                if curseur == 1:
                    page = 56
                    curseur = 1
                if curseur == 2:
                    page = 63
                    curseur = 1
            if page == 56: # SSH Menu
                if curseur == 1:
                    sshstart()
                if curseur == 2:
                    sshstop()
                if curseur == 3:
                    credentials()
            if page == 63:
                if curseur == 1:
                    vncstart()
                if curseur == 2:
                    vncstop()
                if curseur == 3:
                    credentials()
            
  

############# MAIN MENU ############## -----------------------------------

            if page == 0:
            #we are in main menu
                if curseur == 1:
                    # Connection Settings
                    page = 49
                    curseur = 1
                if curseur == 2:
                   #testing
                    page = 14
                    curseur = 1
                if curseur == 5:
                    ScreenOFF()
                if curseur == 6:
                    # System Settings
                    page = 7
                    curseur = 1
                if curseur == 7:
                    # Power
                    page = 42
                    curseur = 1                                  
                print(page+curseur)
    ligne[1]=switch_menu(page)
    ligne[2]=switch_menu(page+1)
    ligne[3]=switch_menu(page+2)
    ligne[4]=switch_menu(page+3)
    ligne[5]=switch_menu(page+4)
    ligne[6]=switch_menu(page+5)
    ligne[7]=switch_menu(page+6)




    #add curser on front on current selected line
    for n in range(1,8):
        if page+curseur == page+n:
            if page == 1:
                if readCapacity(bus) < 16:
                    ligne[n] = ligne[n].replace("_","!")
                else:
                    ligne[n] = ligne[n].replace("_",">")
            else:
                ligne[n] = ligne[n].replace("_",">")
        else:
            ligne[n] = ligne[n].replace("_"," ")
    DisplayText(ligne[1],ligne[2],ligne[3],ligne[4],ligne[5],ligne[6],ligne[7])
    #print(page+curseur) #debug trace menu value
    time.sleep(0.1)
    selection = 0
GPIO.cleanup()


