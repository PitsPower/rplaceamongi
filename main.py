from collections import Counter
from io import BytesIO
import json
import math
from PIL import Image, ImageEnhance
import requests
import ssl
from websocket import create_connection

token = "[PUT REDDIT TOKEN HERE]"


def get_place_urls():
    ws = create_connection("wss://gql-realtime-2.reddit.com/query", sslopt={"cert_reqs": ssl.CERT_NONE})
    ws.send('{"type":"connection_init","payload":{"Authorization":"%s"}}' % token)

    ws.send('{"id":"2","type":"start","payload":{"variables":{"input":{"channel":{"teamOwner":"AFD2022","category":"CANVAS","tag":"0"}}},"extensions":{},"operationName":"replace","query":"subscription replace($input: SubscribeInput!) {\\n  subscribe(input: $input) {\\n    id\\n    ... on BasicMessage {\\n      data {\\n        __typename\\n        ... on FullFrameMessageData {\\n          __typename\\n          name\\n          timestamp\\n        }\\n        ... on DiffFrameMessageData {\\n          __typename\\n          name\\n          currentTimestamp\\n          previousTimestamp\\n        }\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}}')
    ws.send('{"id":"3","type":"start","payload":{"variables":{"input":{"channel":{"teamOwner":"AFD2022","category":"CANVAS","tag":"1"}}},"extensions":{},"operationName":"replace","query":"subscription replace($input: SubscribeInput!) {\\n  subscribe(input: $input) {\\n    id\\n    ... on BasicMessage {\\n      data {\\n        __typename\\n        ... on FullFrameMessageData {\\n          __typename\\n          name\\n          timestamp\\n        }\\n        ... on DiffFrameMessageData {\\n          __typename\\n          name\\n          currentTimestamp\\n          previousTimestamp\\n        }\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}}')
    ws.send('{"id":"4","type":"start","payload":{"variables":{"input":{"channel":{"teamOwner":"AFD2022","category":"CANVAS","tag":"2"}}},"extensions":{},"operationName":"replace","query":"subscription replace($input: SubscribeInput!) {\\n  subscribe(input: $input) {\\n    id\\n    ... on BasicMessage {\\n      data {\\n        __typename\\n        ... on FullFrameMessageData {\\n          __typename\\n          name\\n          timestamp\\n        }\\n        ... on DiffFrameMessageData {\\n          __typename\\n          name\\n          currentTimestamp\\n          previousTimestamp\\n        }\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}}')
    ws.send('{"id":"5","type":"start","payload":{"variables":{"input":{"channel":{"teamOwner":"AFD2022","category":"CANVAS","tag":"3"}}},"extensions":{},"operationName":"replace","query":"subscription replace($input: SubscribeInput!) {\\n  subscribe(input: $input) {\\n    id\\n    ... on BasicMessage {\\n      data {\\n        __typename\\n        ... on FullFrameMessageData {\\n          __typename\\n          name\\n          timestamp\\n        }\\n        ... on DiffFrameMessageData {\\n          __typename\\n          name\\n          currentTimestamp\\n          previousTimestamp\\n        }\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}}')

    ack = json.loads(ws.recv())
    if ack["type"] != "connection_ack":
        return None, None

    ws.recv()

    responses = [json.loads(ws.recv()), json.loads(ws.recv()), json.loads(ws.recv()), json.loads(ws.recv())]

    ws.close()

    responses.sort(key=lambda r: int(r["id"]))
    responses = [r["payload"]["data"]["subscribe"]["data"]["name"] for r in responses]

    return responses[0], responses[1], responses[2], responses[3]


url1, url2, url3, url4 = get_place_urls()

img1 = Image.open(BytesIO(requests.get(url1).content))
img2 = Image.open(BytesIO(requests.get(url2).content))
img3 = Image.open(BytesIO(requests.get(url3).content))
img4 = Image.open(BytesIO(requests.get(url4).content))

img = Image.new("RGB", (img1.width + img2.width, img1.height + img3.height))
img.paste(img1, (0, 0))
img.paste(img2, (img1.width, 0))
img.paste(img3, (0, img3.height))
img.paste(img4, (img1.width, img3.height))

img.save("./img/place_new.png")

# img = Image.open("./img/place_new.png")

map_img = img.copy()
enhancer = ImageEnhance.Brightness(map_img)
map_img = enhancer.enhance(0.2)
map_img_pixels = map_img.load()


class AmogusTemplate:
    def __init__(self, data):
        self.data = data
        self.width = len(data[0])
        self.height = len(data)

        self.origin_x = data[-1].index("O")
        self.origin_y = len(data) - 1

    def __eq__(self, other):
        return self.data == other.data

    def __hash__(self):
        return hash(tuple(self.data))

    def flip_h(self):
        data = [row[::-1] for row in self.data]
        return AmogusTemplate(data)

    def flip_v(self):
        data = self.data[::-1]
        return AmogusTemplate(data)

    def rotate_c(self):
        data = list(zip(*self.data[::-1]))
        return AmogusTemplate(data)

    def rotate_cc(self):
        data = list(zip(*self.data))[::-1]
        return AmogusTemplate(data)

    def at(self, x, y):
        body_color = img.getpixel((x + self.data[0].index("X"), y))
        visor_color = None

        mismatched_body_pixels = 0
        mismatched_body_pixels_max = 0

        for i in range(len(self.data)):
            for j in range(len(self.data[0])):
                if self.data[i][j] == " ":
                    if img.getpixel((x+j, y+i)) == body_color:
                        return False, None, None

                if self.data[i][j] == "X" or self.data[i][j] == "O":
                    if img.getpixel((x+j, y+i)) != body_color:
                        if mismatched_body_pixels >= mismatched_body_pixels_max:
                            return False, None, None
                        else:
                            mismatched_body_pixels += 1

                if self.data[i][j] == "V":
                    if visor_color:
                        if img.getpixel((x+j, y+i)) != visor_color:
                            return False, None, None
                    else:
                        visor_color = img.getpixel((x+j, y+i))
                        if visor_color == body_color:
                            return False, None, None

        return True, body_color, visor_color


class Amogus:
    def __init__(self, template, body_color, visor_color):
        self.template = template
        self.body_color = body_color
        self.visor_color = visor_color

    def __eq__(self, other):
        return self.template == other.template and self.body_color == other.body_color and self.visor_color == other.visor_color

    def __hash__(self):
        return hash((self.template, self.body_color, self.visor_color))

    def draw(self, pixels, x, y):
        for i in range(len(self.template.data)):
            for j in range(len(self.template.data[0])):
                if self.template.data[i][j] == "X" or self.template.data[i][j] == "O":
                    pixels[x + j, y + i] = self.body_color

                if self.template.data[i][j] == "V":
                    pixels[x + j, y + i] = self.visor_color

    def get_img(self):
        image = Image.new("RGB", (self.template.width, self.template.height))
        image.paste((40, 40, 40), (0, 0, image.size[0], image.size[1]))
        image_pixels = image.load()

        self.draw(image_pixels, 0, 0)

        return image

    def get_img_fixed(self, scale):
        img_orig = self.get_img()

        max_amogus_width = 5
        max_amogus_height = 5

        x = 1 - self.template.origin_x
        y = max_amogus_height - 1 - self.template.origin_y

        img = Image.new("RGB", (max_amogus_width, max_amogus_height))
        img.paste((40, 40, 40), (0, 0, img.size[0], img.size[1]))
        img.paste(img_orig, (x, y))

        img = img.resize((img.size[0] * scale, img.size[1] * scale), Image.Resampling.NEAREST)

        return img


class AmogusDetector:
    def __init__(self, template):
        self.template = AmogusTemplate(template)

        self.body_color = None
        self.visor_color = None

        self.all_amongi = []

        self.width = self.template.width
        self.height = self.template.height

        self.count = 0

    def flip_h(self):
        self.template = self.template.flip_h()

    def flip_v(self):
        self.template = self.template.flip_v()

    def rotate_c(self):
        self.template = self.template.rotate_c()

    def rotate_cc(self):
        self.template = self.template.rotate_cc()

    def find(self):
        self.all_amongi = []
        self.count = 0

        for x in range(img.width - self.width + 1):
            for y in range(img.height - self.height + 1):
                if self.at(x, y):
                    self.count += 1

                    amogus = Amogus(self.template, self.body_color, self.visor_color)
                    self.all_amongi.append(amogus)

                    amogus.draw(map_img_pixels, x, y)

    def at(self, x, y):
        success, body_color, visor_color = self.template.at(x, y)

        if success:
            self.body_color = body_color
            self.visor_color = visor_color

        return success


def generate_amongi_grid(amongi, grid_width=40):
    colors = [(a.body_color, a.visor_color) for a in amongi]
    color_count = Counter(colors)

    amongi.sort(reverse=True, key=lambda a: (color_count[(a.body_color, a.visor_color)], a.body_color[0], a.body_color[1], a.body_color[2], a.visor_color[0], a.visor_color[1], a.visor_color[2]))

    max_amogus_width = 5
    max_amogus_height = 5

    rows = math.ceil(len(amongi) / grid_width)

    grid = Image.new("RGB", (grid_width * (max_amogus_width + 1), rows * (max_amogus_height + 2)))
    grid.paste((40, 40, 40), (0, 0, grid.size[0], grid.size[1]))

    for i in range(rows):
        for j in range(grid_width):
            if len(amongi) <= i * grid_width + j:
                break

            amogus = amongi[i * grid_width + j]

            x = j * (max_amogus_width + 1)
            y = i * (max_amogus_height + 2)

            amogus_img = amogus.get_img_fixed(1)
            grid.paste(amogus_img, (x, y))

    grid = grid.resize((grid.size[0] * 4, grid.size[1] * 4), Image.Resampling.NEAREST)

    return grid


templates = {
    "Normal Right": [
        " XXX",
        "XXVV",
        "XXXX",
        " XXX",
        " O X",
    ],
    "Normal Left": [
        "XXX ",
        "VVXX",
        "XXXX",
        "XXX ",
        "O X ",
    ],
    "3-High Backpack Right": [
        " XXX",
        "XXVV",
        "XXXX",
        "XXXX",
        " O X",
    ],
    "3-High Backpack Left": [
        "XXX ",
        "VVXX",
        "XXXX",
        "XXXX",
        "O X ",
    ],
    "No Backpack Right": [
        " XXX",
        " XVV",
        " XXX",
        " XXX",
        " O X",
    ],
    "No Backpack Left": [
        "XXX ",
        "VVX ",
        "XXX ",
        "XXX ",
        "O X ",
    ],
    "Minimongus Right": [
        " XXX",
        "XXVV",
        "XXXX",
        " O X",
    ],
    "Minimongus Left": [
        "XXX ",
        "VVXX",
        "XXXX",
        "O X ",
    ],
    "No Backpack Minimongus Right": [
        " XXX",
        " XVV",
        " XXX",
        " O X",
    ],
    "No Backpack Minimongus Left": [
        "XXX ",
        "VVX ",
        "XXX ",
        "O X ",
    ],
    "Upside-down Right": [
        " X X",
        " XXX",
        "XXXX",
        "XXVV",
        " OXX",
    ],
    "Upside-down Left": [
        "X X ",
        "XXX ",
        "XXXX",
        "VVXX",
        "OXX ",
    ],
}

all_amongi = []
amongi_variants = []

grid_html = ""

for (name, template) in templates.items():
    detector = AmogusDetector(template)
    detector.find()

    for amogus in detector.all_amongi:
        all_amongi.append(amogus)

    print(name + " Count: " + str(detector.count))

    if detector.count > 0:
        grid_img_path = "./img/grid/" + name.lower().replace(" ", "_") + ".png"

        grid_img = generate_amongi_grid(detector.all_amongi)
        grid_img.save(grid_img_path)

        amongi_variants.append({
            "name": name,
            "count": detector.count,
            "template": template,
            "grid_img_path": grid_img_path,
        })

amongi_variants.sort(reverse=True, key=lambda v: v["count"])

print("Total Count: " + str(len(all_amongi)))

amongi_counts = Counter(all_amongi)
count_values = sorted(amongi_counts.values(), reverse=True)
unique_amongi = list(set(all_amongi[:]))
unique_amongi.sort(reverse=True, key=lambda a: amongi_counts[a])

for i in range(10):
    amogus = unique_amongi[i]
    img = amogus.get_img_fixed(20)
    img.save("./img/amongi/%s.png" % (i+1))

for variant in amongi_variants:
    template = variant["template"]
    amogus = Amogus(AmogusTemplate(template), (255, 0, 0), (0, 255, 255))
    img = amogus.get_img_fixed(20)

    img_path = "./img/variants/%s.png" % variant["name"].lower().replace(" ", "_")
    img.save(img_path)

    grid_html += '<div class="container"><img class="icon" src="%s"><h1>%s - %s</h1><br>\n<img src="%s"></div>\n' % (img_path, variant["name"], variant["count"], variant["grid_img_path"])

grid_html = ('<div class="container"><h1>All Amongi - %s</h1><br>\n<img src="img/grid.png"></div>\n' % len(all_amongi)) + grid_html

map_img.save("./img/amogus_map_new.png")

grid_img = generate_amongi_grid(all_amongi)
grid_img.save("./img/grid.png")

with open("base.html", "r") as f:
    base_html = f.read()
    index_html = base_html.replace("[[GRID]]", grid_html)

    for i in range(10):
        index_html = index_html.replace("[[TOP10_COUNT%s]]" % (i+1), str(count_values[i]))

with open("index.html", "w") as f:
    f.write(index_html)
