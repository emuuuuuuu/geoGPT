import pyautogui, time, base64, math, os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
  api_key=os.environ["OPENAI_API_KEY"],
)

pyautogui.FAILSAFE = False

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def lat_lng_to_pixels(lat, lng, map_width, map_height):
    x = (lng + 180) * (map_width / 360)
    lat_rad = lat * math.pi / 180
    merc_n = math.log(math.tan((math.pi / 4) + (lat_rad / 2)))
    y = (map_height / 2) - (map_width * merc_n / (2 * math.pi))
    return x, y

def call_gpt_vision(prompt):
    message = {
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}", "detail": "high"}}
        ]
    }
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[message]
    )
    return response.choices[0].message.content

def call_gpt_4(prompt):
    message = {
        "role": "user",
        "content": [{"type": "text", "text": prompt}]
    }
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[message]
    )
    return response.choices[0].message.content

first_prompt = """Guess which city/region of the world you are in given this image. It is very important that you are be specific,
don't just answer with "Australia" or be vague, be confident. Make an educated guess even though you aren't certain. 
Don't explain your answer, just write the name of the location."""

map_width, map_height = 567, 402
screenWidth, screenHeight = pyautogui.size()
i = 0

while True:
    pixel_color = pyautogui.pixel(20,27)
    if pixel_color == (204, 48, 46):
        i += 1
        screenshot = pyautogui.screenshot()
        filename = f"screenshot_{i}.png"
        screenshot.save(filename)
        base64_image = encode_image(filename)
        answer = call_gpt_vision(first_prompt)
        print(answer)
        second_prompt = f"""What's the coordinates for the middle of {answer}, 
        don't explain your answer just write the coordinates like this: 41.40338, 2.17403"""
        answer2 = call_gpt_4(second_prompt)
        print(answer2)
        try:
            x,y = lat_lng_to_pixels(float(answer2.split(",")[0]), float(answer2.split(",")[1]), map_width, map_height)
        except:
            x,y = lat_lng_to_pixels(29.976480, 31.131302, map_width, map_height)
        pyautogui.moveTo(screenWidth - 200, screenHeight - 200)
        time.sleep(.2)
        pyautogui.click(screenWidth - 41 - (map_width-x), screenHeight - 70 - (map_height - y))
        time.sleep(.2)
        pyautogui.click(screenWidth - 200, screenHeight - 50)
        time.sleep(2.5)
        pyautogui.click(screenWidth - 960, screenHeight - 100)
    time.sleep(.1)