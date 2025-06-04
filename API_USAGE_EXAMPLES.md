# JSON2Video API Usage Examples

This API allows you to create videos from JSON configurations and combine video/audio files. Here are comprehensive examples of how to use each endpoint.

## Base URL
```
https://your-domain.com
```

## Authentication

This API uses API key authentication via the `X-API-Key` header. You must include your API key in all requests.

**Required Header:**
```
X-API-Key: your_api_key_here
```

**Setting up your API key:**
1. Set the `API_KEY` environment variable in your `.env` file
2. If no API key is configured, authentication is disabled (for development only)

**Authentication Errors:**
- `401 Unauthorized`: Invalid or missing API key

## Endpoints

### 1. `/render` - Create Video from JSON Configuration

This endpoint creates a video based on a JSON configuration that defines images, text overlays, effects, and audio.

#### Request Method: `POST`
#### Content-Type: `application/json`

#### Basic Example - Simple Image Slideshow

```bash
curl -X POST "https://your-domain.com/render" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "timeline": [
      {
        "type": "image",
        "url": "https://example.com/image1.jpg",
        "duration": 3.0
      },
      {
        "type": "image", 
        "url": "https://example.com/image2.jpg",
        "duration": 2.5
      }
    ]
  }'
```

#### Advanced Example - With Effects, Text Overlays, and Audio

```bash
curl -X POST "https://your-domain.com/render" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "timeline": [
      {
        "type": "image",
        "url": "https://example.com/intro.jpg",
        "duration": 4.0,
        "effects": {
          "zoom": 1.2,
          "rotate": 5.0
        }
      },
      {
        "type": "split",
        "top_url": "https://example.com/top_image.jpg", 
        "bot_url": "https://example.com/bottom_image.jpg",
        "duration": 3.0,
        "effects": {
          "slidein": 1.0
        }
      },
      {
        "type": "image",
        "url": "https://example.com/finale.jpg",
        "duration": 2.0
      }
    ],
    "audio": "https://example.com/background_music.mp3",
    "transition": {
      "type": "crossfade",
      "duration": 0.8
    },
    "text_overlays": [
      {
        "text": "Welcome to Our Video!",
        "start": 0.5,
        "end": 3.5,
        "position": "center",
        "fontsize": 48,
        "color": "white"
      },
      {
        "text": "Split Screen Demo", 
        "start": 4.0,
        "end": 6.5,
        "position": "center",
        "fontsize": 36,
        "color": "yellow"
      }
    ]
  }'
```

#### Python Example

```python
import requests
import json

# Basic video creation
payload = {
    "timeline": [
        {
            "type": "image",
            "url": "https://picsum.photos/800/600?random=1",
            "duration": 3.0,
            "effects": {
                "zoom": 1.1
            }
        },
        {
            "type": "image", 
            "url": "https://picsum.photos/800/600?random=2",
            "duration": 2.5,
            "effects": {
                "rotate": -2.0
            }
        }
    ],
    "text_overlays": [
        {
            "text": "Sample Video Creation",
            "start": 0.0,
            "end": 5.5,
            "fontsize": 42,
            "color": "white",
            "position": "center"
        }
    ],
    "transition": {
        "type": "crossfade",  
        "duration": 0.5
    }
}

response = requests.post(
    "https://your-domain.com/render",
    headers={
        "Content-Type": "application/json",
        "X-API-Key": "your_api_key_here"
    },
    json=payload
)

if response.status_code == 200:
    result = response.json()
    video_url = result["url"]
    print(f"Video created successfully: {video_url}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

#### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const videoConfig = {
  timeline: [
    {
      type: "image",
      url: "https://example.com/photo1.jpg", 
      duration: 4.0,
      effects: {
        zoom: 1.15,
        slidein: 0.8
      }
    },
    {
      type: "split",
      top_url: "https://example.com/before.jpg",
      bot_url: "https://example.com/after.jpg", 
      duration: 3.5
    }
  ],
  audio: "https://example.com/soundtrack.mp3",
  text_overlays: [
    {
      text: "Before & After Comparison",
      start: 4.0,
      end: 7.5,
      fontsize: 40,
      color: "cyan"
    }
  ]
};

axios.post('https://your-domain.com/render', videoConfig, {
  headers: {
    'X-API-Key': 'your_api_key_here'
  }
})
  .then(response => {
    console.log('Video URL:', response.data.url);
  })
  .catch(error => {
    console.error('Error:', error.response?.data || error.message);
  });
```

### 2. `/combine` - Combine Video and Audio Files

This endpoint combines separate video and audio files into a single video file.

#### Request Method: `POST`
#### Content-Type: `multipart/form-data`

#### cURL Example

```bash
curl -X POST "https://your-domain.com/combine" \
  -H "X-API-Key: your_api_key_here" \
  -F "video=@video_file.webm" \
  -F "audio=@audio_file.webm"
```

#### Python Example

```python
import requests

# Combine video and audio files
files = {
    'video': ('my_video.webm', open('path/to/video.webm', 'rb'), 'video/webm'),
    'audio': ('my_audio.webm', open('path/to/audio.webm', 'rb'), 'audio/webm')
}

response = requests.post(
    "https://your-domain.com/combine",
    headers={"X-API-Key": "your_api_key_here"},
    files=files
)

if response.status_code == 200:
    # Save the combined video
    with open('combined_output.webm', 'wb') as f:
        f.write(response.content)
    print("Combined video saved as combined_output.webm")
else:
    print(f"Error: {response.status_code} - {response.text}")

# Don't forget to close file handles
files['video'][1].close()
files['audio'][1].close()
```

#### JavaScript/Browser Example

```javascript
// HTML form upload
const formData = new FormData();
const videoFile = document.getElementById('videoInput').files[0];
const audioFile = document.getElementById('audioInput').files[0];

formData.append('video', videoFile);
formData.append('audio', audioFile);

fetch('https://your-domain.com/combine', {
  method: 'POST',
  headers: {
    'X-API-Key': 'your_api_key_here'
  },
  body: formData
})
.then(response => {
  if (response.ok) {
    return response.blob();
  }
  throw new Error('Upload failed');
})
.then(blob => {
  // Create download link
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'combined_video.webm';
  a.click();
  window.URL.revokeObjectURL(url);
})
.catch(error => {
  console.error('Error:', error);
});
```

## Configuration Options

### Timeline Items

#### Image Item
```json
{
  "type": "image",
  "url": "https://example.com/image.jpg",
  "duration": 3.0,
  "effects": {
    "zoom": 1.2,        // Scale factor (1.0 = no zoom)
    "rotate": 15.0,     // Rotation in degrees
    "slidein": 1.0      // Slide-in animation duration
  }
}
```

#### Split Screen Item
```json
{
  "type": "split", 
  "top_url": "https://example.com/top.jpg",
  "bot_url": "https://example.com/bottom.jpg",
  "duration": 4.0,
  "effects": {
    "zoom": 1.1
  }
}
```

### Transitions
```json
{
  "type": "crossfade",  // "crossfade", "slide", or "blink"
  "duration": 0.5       // Transition duration in seconds
}
```

### Text Overlays
```json
{
  "text": "Your text here",
  "start": 1.0,         // Start time in seconds
  "end": 4.0,           // End time in seconds (optional)
  "position": "center", // Text position
  "fontsize": 32,       // Font size in pixels
  "color": "white"      // Text color
}
```

## Response Format

### Successful Video Render Response
```json
{
  "url": "https://cloud-storage-url.com/generated-video.mp4"
}
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Tips and Best Practices

1. **Image URLs**: Ensure all image URLs are publicly accessible
2. **Audio Files**: Supported formats include MP3, WAV, AAC
3. **Duration**: Plan your timeline durations to match your audio length
4. **Effects**: Use effects sparingly for better performance
5. **Text Overlays**: Keep text concise and ensure good contrast
6. **File Sizes**: Larger images may take longer to process

## Error Handling

Common error scenarios:
- Invalid image URLs (404 errors)
- Unsupported file formats
- Network timeouts for large files
- Invalid JSON structure
- Missing required fields

Always check the response status code and handle errors appropriately in your application.
