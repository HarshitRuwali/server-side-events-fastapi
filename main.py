from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
import asyncio
import uvicorn
from base64 import b64encode

app = FastAPI()


async def image_stream():
	# Simulated image streaming, replace with your actual image streaming logic
	while True:
		# Open an image file, or fetch it from a source
		with open("image.jpg", "rb") as file:
			# Read the image data
			image_data = file.read()

		image_data = b64encode(image_data)
		# Yield the image data
		yield "data: " + str(image_data)

		# Adjust sleep time as needed to control the rate of streaming
		await asyncio.sleep(1)
		return


@app.get("/")
def hello():
	response = {
		"body": "hello there, try the endpoint, /stream-images",
	}
	return response


@app.get("/stream-images")
async def stream_images(request: Request):
	response = StreamingResponse(
		image_stream(), media_type="text/event-stream"
	)
	response.headers["Cache-Control"] = "no-cache"
	return response


if __name__ == "__main__":
	uvicorn.run(app, host="127.0.0.1", port=8000)
