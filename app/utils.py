# coding=utf-8
import base64
import hashlib
import random
import string
import uuid
from io import BytesIO

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from decimal import Decimal

from app import app


def tobytes(s):
    if isinstance(s, bytes):
        return s
    else:
        if isinstance(s, str):
            return s.encode('utf-8')
        else:
            return bytes(s)

def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError

def generate_captcha(size, font_size):
    font = ImageFont.truetype('DejaVuSans.ttf', font_size)
    image = Image.new('RGB', size, (255,) * 4)
    draw = ImageDraw.Draw(image)

    n = 4
    padding = 10
    x, y = size
    xi = (x - padding * 2) / n
    yi = (y - font_size) / 2

    captcha = ''.join(str(random.randint(0, 9)) for i in range(n))
    i = 0
    for c in captcha:
        color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        x = padding + i * xi + random.randint(0, 5)
        y = yi + random.randint(0, 5)
        draw.text((x, y), c, fill=color, font=font)
        i += 1

    return captcha, image

def genereate_uuid():
    return base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes + uuid.uuid4().bytes).decode()

def genereate_random_string(a, b):
    n = random.randint(a, b)
    return ''.join(random.choice(string.digits + string.ascii_letters) for i in range(n))


def decrypt_password(password):
    privkey = RSA.importKey(open('private_key.pem').read())
    cipher = PKCS1_v1_5.new(privkey)
    plaintext = cipher.decrypt(base64.b64decode(password), None)
    app.logger.info(plaintext)
    return plaintext.decode()


def encrypt_password(password, salt):
    if len(password) == 32:
        return hashlib.md5(tobytes(salt) + tobytes(password)).hexdigest()
    return hashlib.sha256(tobytes(password) + tobytes(salt)).hexdigest()
