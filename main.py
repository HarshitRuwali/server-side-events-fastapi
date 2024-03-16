from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import StreamingResponse
import asyncio
import uvicorn
from base64 import b64encode
from typing import List
import os
from sse_starlette.sse import EventSourceResponse

app = FastAPI()

IMAGE_DIRECTORY = "images"
COUNTER = 0
MESSAGE_STREAM_DELAY = 1  # second
MESSAGE_STREAM_RETRY_TIMEOUT = 15000  # milisecond

def get_message():
	global COUNTER
	COUNTER += 1
	return COUNTER, COUNTER < 21


async def image_stream():
	while True:
		# Open an image file, or fetch it from a source
		with open("image.jpg", "rb") as file:
			# Read the image data
			image_data = file.read()

		image_data = b64encode(image_data)
		# Yield the image data
		yield "data: " + str(image_data)

		await asyncio.sleep(1)
		# return # this will stop the streaming TESTING ONLY


def get_image_batch(page: int = 1, size: int = 10) -> List[str]:
	start_index = (page - 1) * size
	end_index = start_index + size
	image_files = os.listdir(IMAGE_DIRECTORY)
	return image_files[start_index:end_index]


@app.get("/")
def hello():
	response = {
		"body": "hello there, try the endpoint, /stream/images, /stream/messages",
	}
	return response


@app.get("/stream/images")
async def stream_images(request: Request):
	response = StreamingResponse(
		image_stream(), media_type="text/event-stream"
	)
	response.headers["Cache-Control"] = "no-cache"
	return response


@app.get("/images/")
async def get_images(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=20)):
	image_batch = get_image_batch(page, size)
	if not image_batch:
		raise HTTPException(status_code=404, detail="No images found.")
	return {"images": image_batch}


@app.get("/stream/message")
async def message_stream(request: Request):
	async def event_generator():
		while True:
			if await request.is_disconnected():
				print("Request disconnected")
				break

		# Checks for new messages and return them to client if any
		counter, exists = get_message()
		if exists:
			yield {
				"event": "new_message",
				"id": "message_id",
				"retry": MESSAGE_STREAM_RETRY_TIMEOUT,
				"data": f"Counter value {counter}",
			}
		else:
			yield {
				"event": "end_event",
				"id": "message_id",
				"retry": MESSAGE_STREAM_RETRY_TIMEOUT,
				"data": "End of the stream",
			}

			await asyncio.sleep(MESSAGE_STREAM_DELAY)

	return EventSourceResponse(event_generator())

if __name__ == "__main__":
	uvicorn.run(app, host="127.0.0.1", port=8000)
