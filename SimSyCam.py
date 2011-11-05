# SimSyCam - Simple Symbian Camera

import appuifw

appuifw.app.orientation='landscape' # must be called before importing camera
appuifw.app.screen='full'

from key_codes import *
import e32, time, camera, globalui, graphics

# variables used for mode change messages
info = u""
start_time = 0

# supportet modes
flash_modes = camera.flash_modes()
exposure_modes = camera.exposure_modes()
white_modes = camera.white_balance_modes()

# default mode values
if 'forced' in flash_modes:
	flash_mode = flash_modes.index('forced')
else:
	flash_mode = 0
exposure_mode = 0
white_mode = 0

# applicaton lock
app_lock = e32.Ao_lock()

# exit function
def quit():
	camera.stop_finder()
	camera.release()
	app_lock.signal()

appuifw.app.exit_key_handler = quit

# display message on screen
def message(img):
	img.rectangle((5, 3, 195, 28), fill=0)
	img.text((10, 20), info, 0xff0000, (None, None, graphics.FONT_BOLD))

# displaying viewfinder
def viewfinder(img):
	if time.time() <= start_time + 5:
		message(img)
	appuifw.app.body.blit(img)

# start viewfinder function
def start_view():
	camera.start_finder(viewfinder, backlight_on = 1, size=(320, 240))

# take dummy photo - viewfinder will start to show image in current exposure
# and white balance mode
def new_view():
	camera.stop_finder()
	message(appuifw.app.body)
	camera.take_photo(
		mode="JPEG_Exif",
		size=camera.image_sizes()[-1], # should be the smallest available
		exposure=exposure_modes[exposure_mode],
		white_balance=white_modes[white_mode])
	start_view()

# event callback
def callback(event):
	global flash_mode, exposure_mode, white_mode
	if event['type'] == appuifw.EEventKey:
		ev = event['keycode']
		if ev == EKeySelect:
			photo()
		elif ev == EKey5:
			flash_mode = new(flash_modes, flash_mode, "Flash")
		elif ev == EKey4:
			exposure_mode = new(exposure_modes, exposure_mode, "Exposure")
			new_view()
		elif ev == EKey6:
			white_mode = new(white_modes, white_mode, "White balance")
			new_view()

# take photo
def photo():
	global info
	info = u"Taking photo..."
	start_time = time.time()
	camera.stop_finder()
	message(appuifw.app.body)
	p = camera.take_photo(
		mode="JPEG_Exif",
		size=(1600, 1200),
		flash=flash_modes[flash_mode],
		exposure=exposure_modes[exposure_mode],
		white_balance=white_modes[white_mode])
	filename = time.strftime("E:\\Images\\%d%m%y-%H%M%S.jpg")
	f = open(filename, "w")
	f.write(p)
	f.close()
	appuifw.app.body.blit(graphics.Image.open(filename), scale=1)
	time.sleep(2)
	start_time = 0
	start_view()

# returns the new mode of given property
def new(modes, mode, string):
	global info, start_time
	mode += 1
	mode %= len(modes)
	info = unicode(string) + ": " + modes[mode]
	start_time = time.time()
	return mode

# start
appuifw.app.body = appuifw.Canvas(event_callback=callback)
start_view()
app_lock.wait()