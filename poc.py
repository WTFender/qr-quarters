from io import BytesIO
from PIL import Image
from sys import argv
import base64
import qrcode


def parse_args() -> tuple[str, int]:
    if any([arg for arg in argv if arg in ['-h', '--help']]):
        print("Usage: python poc.py [url] [size]")
        exit()
    url = "https://wtfender.com"
    size = 10
    if len(argv) > 1:
        url = argv[1]
    if len(argv) > 2:
        size = int(argv[2])
    return url, size


def generate_qr_code(link: str, size: int) -> Image:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=4,
    )
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img


def quarter_image(img: Image) -> list[Image]: # type: ignore
    image = img.get_image()
    image.convert('L')
    # get image size
    width, height = image.size
    # split image into quarters
    quarters = []
    for i in range(2):
        for j in range(2):
            left = i * width // 2
            upper = j * height // 2
            right = (i + 1) * width // 2
            lower = (j + 1) * height // 2
            quarter = image.crop((left, upper, right, lower))
            quarters.append(quarter)
    return quarters


def convert_to_base64_uris(quarters: list[Image]) -> list[str]: # type: ignore
    quarters_b64 = []
    for quarter in quarters:
        buffered = BytesIO()
        quarter.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        quarters_b64.append('data:image/jpeg;base64,' + img_str)
    return quarters_b64


def create_html_table(quarters_b64: list[str]) -> str:
    html = f'''<table style="border: none; border-spacing: 0px;">
    <tr>
        <td><img src="{quarters_b64[0]}"></td>
        <td><img src="{quarters_b64[2]}"></td>
    </tr>
    <tr>
        <td><img src="{quarters_b64[1]}"></td>
        <td><img src="{quarters_b64[3]}"></td>
    </tr>
</table>'''
    return html

if __name__ == '__main__':
    url, size = parse_args()
    qr = generate_qr_code(url, size)
    quarters = quarter_image(qr) # [ TopLeft, BL, TR, BR ]
    quarters_b64 = convert_to_base64_uris(quarters)
    table_html = create_html_table(quarters_b64)
    print(table_html)
