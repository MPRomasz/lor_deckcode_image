import sys
from lor_deckcodes import LoRDeck, CardCodeAndCount
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageFilter
import requests
from io import BytesIO
from card import Card

font = ImageFont.truetype("./fonts/Roboto-Bold.ttf", 14)
font2 = ImageFont.truetype("./fonts/Roboto-Black.ttf", 12)
header_font = ImageFont.truetype("./fonts/Roboto-Black.ttf", 26)

region_color_mapping = {
	'Demacia': '#bfb083',
	'Freljord': '#5ab8da',
	'Ionia': '#cf829b',
	'Noxus': '#a0524f',
	'PiltoverZaum': '#e29f76',
	'ShadowIsles': '#3b7d6f',
	'Bilgewater': '#b4563a'
}

def get_concat_v(im1, im2, offset=0):
	dst1 = Image.new('RGBA', (im1.width, im1.height + im2.height + offset), (0, 0, 0, 0))
	dst2 = Image.new('RGBA', (im1.width, im1.height + im2.height + offset), (0, 0, 0, 0))
	dst1.paste(im1.convert('RGBA'), (0, 0))
	dst2.paste(im2.convert('RGBA'), (0, im1.height + offset))
	dst = Image.alpha_composite(dst1, dst2)
	return dst

def get_concat_h(im1, im2, offset=0):
    dst1 = Image.new('RGBA', (im1.width + im2.width + offset, im1.height if im1.height > im2.height else im2.height), (0, 0, 0, 0))
    dst2 = Image.new('RGBA', (im1.width + im2.width + offset, im1.height if im1.height > im2.height else im2.height), (0, 0, 0, 0))
    dst1.paste(im1.convert('RGBA'), (0, 0), im1)
    dst2.paste(im2.convert('RGBA'), (im1.width + offset, 0))
    dst = Image.alpha_composite(dst1, dst2)
    return dst
#    return dst

def color_from_region(card):
	region = card.split(':')[1][2:4]
	color = 0
	if region == 'DE': color = '#bfb083'
	elif region == 'FR': color = '#5ab8da'
	elif region == 'IO': color = '#cf829b'
	elif region == 'NX': color = '#a0524f'
	elif region == 'PZ': color = '#e29f76'
	elif region == 'SI': color = '#3b7d6f'
	elif region == 'BW': color = '#b4563a'
	return color

def add_corners(im, rad):
	circle = Image.new('L', (rad * 2, rad * 2), 0)
	draw = ImageDraw.Draw(circle)
	draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
	alpha = Image.new('L', im.size, 255)
	w, h = im.size
	alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
	alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
	alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
	alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
	im.putalpha(alpha)
	return im

def add_gradient_h(card, im):
	width, height = im.size
	new_size = (width + 56, height + 2)

	new_im = Image.new("RGBA", new_size, (0, 0, 0, 255))
	new_im.paste(im, (56,1))
	width, height = new_im.size

	im = new_im

	gradient=2.
	initial_opacity=1.

	alpha_gradient = Image.new('L', (width, 1), color=0xFF)

	for x in range(width//3, 2*width//3):
		a = int((initial_opacity * 255.) * (1. - gradient * (float(x)-(width//3))/(2*width/3)  ))
		if a > 0:
			alpha_gradient.putpixel((x, 0), a)
		else:
			alpha_gradient.putpixel((x, 0), 0)
	for x in range(2*width//3, width):
		alpha_gradient.putpixel((x, 0), 0)
	alpha = alpha_gradient.resize(im.size)
	gradient_im = Image.new('RGBA', (width, height), color=region_color_mapping.get(card.regionRef)) # i.e. black
	gradient_im.putalpha(alpha)

	im = Image.alpha_composite(im, gradient_im)
	#im.save(card.cardCode + '.png', 'png')
	return im

def add_gradient_v(card, im):
	width, height = im.size
	gradient=4.
	initial_opacity=0.15

	alpha_gradient = Image.new('L', (1, height), color=0xFF)

	for x in range(height):
		a = int((initial_opacity * 255.) * (1. - gradient * float(height-x)/height))
		if a > 0:
			alpha_gradient.putpixel((0, x), a)
		else:
			alpha_gradient.putpixel((0, x), 0)
	alpha = alpha_gradient.resize(im.size)
	gradient_im = Image.new('RGBA', (width, height), color=0)
	gradient_im.putalpha(alpha)

	im = Image.alpha_composite(im, gradient_im)
	return im

def add_gradient(card, im):
	if im.mode != 'RGBA':
		im = im.convert('RGBA')
	im = add_gradient_h(card, im)
	im = add_gradient_v(card, im)
	return im

def add_name(card, im):
	shadowcolor = (0, 0, 0, 100)
	x, y = 44, 12
	
	shadow = Image.new('RGBA', im.size, (255,255,255,0))
	sdraw = ImageDraw.Draw(shadow)
	sdraw.text((x+1, y), card, font=font, fill=shadowcolor)
	sdraw.text((x, y+1), card, font=font, fill=shadowcolor)
	sdraw.text((x+1, y+1), card, font=font, fill=shadowcolor)
	sdraw.text((x+1, y+2), card, font=font, fill=shadowcolor)
	sdraw.text((x+2, y+1), card, font=font, fill=shadowcolor)
	sdraw.text((x+2, y+2), card, font=font, fill=shadowcolor)
#	shadow = shadow.filter(ImageFilter.BLUR)
	
	im = Image.alpha_composite(im, shadow)
	draw = ImageDraw.Draw(im)	
	draw.text((x, y),card,(255,255,255), font=font)
	return im

def add_count(count, im):
#	im2 = Image.open('./img/qtd_{}.png'.format(count))
#	im2 = im2.resize((30, 28)).convert('RGBA')
	im2 = Image.open('./img/quantity_empty.png')
	text = 'x{}'.format(count)
	draw = ImageDraw.Draw(im2)
	w, h = draw.textsize(text)
	W, H = im2.size
	draw.text(((W-w)/2,(H-h)/2 -2),text,(255,255,255), font=font2)
	im3 = Image.new('RGBA', im.size, (0,0,0,0))
	x, y = (im.width - im2.width - 7), (im.height - im2.height)//2

	draw = ImageDraw.Draw(im3)
	draw.rectangle((x, y, x+im2.width, y+im2.height), fill=(0, 0, 0, 100))
	for i in range(3):
		im3 = im3.filter(ImageFilter.BLUR)

	im3.paste(im2, (x, y), im2)
	im = Image.alpha_composite(im, im3) 
	return im

def add_cost(cost, im):
	im2 = Image.open('./img/mana_empty.png')
	im2 = im2.resize((26,26))#.convert('RGBA')
	draw = ImageDraw.Draw(im2)
	w, h = draw.textsize(str(cost))
	W, H = im2.size
	draw.text(((W-w)/2 -1,(H-h)/2 -1),str(cost),(255,255,255), font=font2)
#	im.paste(im2, ((im.height - im2.height)//2 -2, (im.height - im2.height)//2), im2)
	im3 = Image.new('RGBA', im.size, (0,0,0,0))

	x, y = (im.height - im2.height)//2 -2, (im.height - im2.height)//2

	draw = ImageDraw.Draw(im3)
	draw.ellipse((x, y, x+im2.width, y+im2.height), fill=(0, 0, 0, 100))
	for i in range(5):
		im3 = im3.filter(ImageFilter.BLUR)

	im3.paste(im2, (x, y), im2)
	im = Image.alpha_composite(im, im3)
	return im

def make_card_image(card):
	response = requests.get(card.preview_image_online)
	im = Image.open(BytesIO(response.content))
	im = add_gradient(card, im)
	im = add_corners(im, 8)
	im = add_name(card.name, im)
	im = add_count(card.count, im)
	im = add_cost(card.cost, im)
	return im

def concat_all_v(images):
	width, height = images[0].size
	final = Image.new("RGBA", (width, 0), (0,0,0,0))
	for image in images:
		final = get_concat_v(final, image)
	return final

def make_header(size, count, type):
	W, H = size[0], size[1] + 12
	im = Image.new('RGBA', (W, H), (54, 57, 63, 0))
	draw = ImageDraw.Draw(im)
	icon = Image.open(f"./img/{type}.png").resize((42,42)).convert('RGBA')
#	full_w, full_h = draw.textsize(f"{type}  {count}", font=header_font)
#	full_w += icon.width
#	full_h = icon.height
#	w, h = draw.textsize(f"{type}  ", font=header_font)

	full_w, full_h = draw.textsize(f"{count}", font=header_font)
	full_w += icon.width
	full_h = icon.height

#	draw.text(((W-full_w)//2 + (icon.width), (H-full_h)//2 + (icon.height//3)),f"{type}",(255, 255, 255), font=header_font)
#	draw.text((((W-full_w)//2 + (icon.width)) + w,(H-full_h)//2 + (icon.height//3)),f"{count}",(204, 173, 112), font=header_font)
	draw.text((((W-full_w)//2 + (icon.width)),(H-full_h)//2 +8 ),f"{count}",(204, 173, 112), font=header_font)
	im3 = Image.new('RGBA', (W, H), (0,0,0,0))
	im3.paste(icon, ((W-full_w)//2 ,(H-full_h)//2), icon)
	im = Image.alpha_composite(im, im3)
	return im

def make_final_image(champion_images, unit_images, spell_images):
	if len(champion_images) > 1:
		size = champion_images[1].size
	elif len(unit_images) > 1:
		size = unit_images[1].size
	elif len(spell_images) > 1:
		size = spell_images[1].size
	
	champion_images[0] = make_header(size, champion_images[0], 'CHAMPIONS')
	unit_images[0] = make_header(size, unit_images[0], 'FOLLOWERS')
	spell_images[0] = make_header(size, spell_images[0], 'SPELLS')

	champion = concat_all_v(champion_images)
	unit = concat_all_v(unit_images)
	spell = concat_all_v(spell_images)
	final = get_concat_h(get_concat_h(champion, unit, offset=10), spell, offset=10)
	return final

def deck_to_image(deckcode):
	unit_images = [0]
	champion_images = [0]
	spell_images = [0]
	deck = LoRDeck.from_deckcode(deckcode)
	newdeck = [Card(CardCode=card_string.split(':')[1], count=card_string.split(':')[0]) for card_string in deck]
	newdeck.sort(key=lambda x: x.cost, reverse=False)
	for card in newdeck:
		if card.cardType == 'Unit':
			if card.isChampion:
				champion_images[0] += card.count
				champion_images.append(make_card_image(card))
			else:
				unit_images[0] += card.count
				unit_images.append(make_card_image(card))
		else:
			spell_images[0] += card.count
			spell_images.append(make_card_image(card))
		#im.save(card.cardCode + '.png', 'png')

	final = make_final_image(champion_images, unit_images, spell_images)
	return final

def deck_to_BytesIO(deckcode):
	with BytesIO() as image_binary:
		deck_to_image(deckcode).save(image_binary, 'png')
		image_binary.seek(0)
		return image_binary

if len(sys.argv)>1:
	im = deck_to_image(sys.argv[1])
	im.save('teste.png', 'png')