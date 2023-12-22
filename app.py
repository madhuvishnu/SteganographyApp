from flask import Flask, render_template, request, redirect,  send_file
from PIL import Image


app = Flask(__name__)

def encode_message(image_path, message):
    img = Image.open(image_path)
    binary_message = ''.join(format(ord(char), '08b') for char in message)

    print(binary_message);

      # Add a delimiter to the binary message
    delimiter = '1111111100000000'  # Example delimiter: eight 1s followed by eight 0s
    binary_message += delimiter

    if len(binary_message) > img.width * img.height * 3:
        raise ValueError("Message is too long to be encoded in the given image")

    pixels = list(img.getdata())
    encoded_pixels = []
    binary_message_iter = iter(binary_message)

    for r, g, b in pixels:
        try:
            encoded_pixel = ((r & 0xFE) | int(next(binary_message_iter), 2),
                             (g & 0xFE) | int(next(binary_message_iter), 2),
                             (b & 0xFE) | int(next(binary_message_iter), 2))
        except StopIteration:
            encoded_pixel = (r, g, b)

        encoded_pixels.append(encoded_pixel)

    encoded_img = Image.new(img.mode, img.size)
    encoded_img.putdata(encoded_pixels)
    encoded_img.save("encoded_image.png")

def decode_message(image_path):
    img = Image.open(image_path)
    binary_message = ""

    for r, g, b in img.getdata():
        binary_message += format(r, '08b')[-1]
        binary_message += format(g, '08b')[-1]
        binary_message += format(b, '08b')[-1]

    # Find the index of the delimiter in the binary message
    delimiter_index = binary_message.find('1111111100000000')

    if delimiter_index != -1:
        binary_message = binary_message[:delimiter_index]

    decoded_message = ""
    current_byte = ""

    for bit in binary_message:
        current_byte += bit
        if len(current_byte) == 8:
            decoded_message += chr(int(current_byte, 2))
            current_byte = ""

    print("Decoded Message:", decoded_message)

    return decoded_message




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/encode', methods=['POST'])
def encode():
    if 'image' not in request.files:
        return redirect(request.url)

    image = request.files['image']
    message = request.form['message']

    if image.filename == '':
        return redirect(request.url)

    image_path = 'uploaded_image.png'
    image.save(image_path)

    # Call the encode_message function with the correct arguments
    encode_message(image_path, message)

    return render_template('index.html', encoded_image='encoded_image.png')

@app.route('/decode', methods=['POST'])
def decode():
    if 'image' not in request.files:
        return redirect(request.url)

    image = request.files['image']

    if image.filename == '':
        return redirect(request.url)

    image_path = 'uploaded_image.png'
    image.save(image_path)

    decoded_message = decode_message(image_path)

    return render_template('index.html', decoded_message=decoded_message, decoded_image=image_path)

@app.route('/download/<filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
