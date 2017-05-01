from PIL import Image
white_ball = Image.open('white_ball.png')
white_img = white_ball.convert("RGBA")
bands = white_img.split()

black_img = Image.new("RGBA", white_ball.size, (0, 0, 0))
other_bands = black_img.split()

red_ball = Image.merge("RGBA", (bands[0], other_bands[1], other_bands[2], bands[3]))
red_ball.save("red_ball.png", 'png')
