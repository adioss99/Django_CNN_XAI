from CNN.cnn_xai import get_heatmap, save_and_display_gradcam

from django.template.response import TemplateResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.http import JsonResponse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.storage import FileSystemStorage
from django.conf import settings

import os
import io
from PIL import Image  # Import Pillow

class CustomFileSystemStorage(FileSystemStorage):
  def get_available_name(self, name, max_length=None):
    self.delete(name)
    return name

def compress_image(image):
  img = Image.open(image)
  img = img.convert('RGB')  # Ensure image is in RGB mode
  output_io_stream = io.BytesIO()
  img.save(output_io_stream, format='JPEG', quality=70)  # Adjust quality as needed
  output_io_stream.seek(0)
  return InMemoryUploadedFile(output_io_stream, 'ImageField', image.name, 'image/jpeg', output_io_stream.getbuffer().nbytes, None)
  
def index(req):
  prediction = ''
  confident = ''
  fss = CustomFileSystemStorage()

  try:
    # save the image
    image = req.FILES["image"]
    print('print========')
    if image.content_type not in ['image/jpeg', 'image/png', 'image/jepg']:
        return TemplateResponse(req, 'index.html', {
            'Error': 'Only JPEG and PNG files are allowed',
        })

    # Compress the image
    compressed_image = compress_image(image)

    _image = fss.save(compressed_image.name, compressed_image)
    path = str(settings.MEDIA_ROOT) + "/" + compressed_image.name
    image_url = fss.url(_image)

    result = get_heatmap(path)
    visualized = save_and_display_gradcam(path, result[0], cam_path=path)

    return TemplateResponse(req, 'index.html', {
        'prediction': result[1][0],
        'confident': result[1][1],
        'image_url': image_url,
      })

  except MultiValueDictKeyError:
    return TemplateResponse(req, 'index.html', {
        'title': 'Error',
    })