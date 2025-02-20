from CNN.cnn_xai import get_heatmap, save_and_display_gradcam

from django.template.response import TemplateResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.http import JsonResponse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.storage import FileSystemStorage
from django.conf import settings

import os

class CustomFileSystemStorage(FileSystemStorage):
  def get_available_name(self, name, max_length=None):
    self.delete(name)
    return name

def index(req):
  prediction = ''
  confident = ''
  fss = CustomFileSystemStorage()

  try:
    # save the image
    image = req.FILES["image"]
    if image.content_type not in ['image/jpeg', 'image/png','image/jepg']:
      return TemplateResponse(req, 'index.html', {
        'Error': 'Only JPEG and PNG files are allowed',
      })
    _image = fss.save(image.name, image)
    path = str(settings.MEDIA_ROOT) + "/" + image.name
    image_url = fss.url(_image)
    
    result = get_heatmap(path)
    visualized = save_and_display_gradcam(path, result[0], cam_path=path)
    
    return TemplateResponse(req, 'index.html',{
      'prediction': result[1][0],
      'confident': result[1][1],
      'image_url': image_url,
    })
    
  except MultiValueDictKeyError:
    return TemplateResponse(req, 'index.html',{
      'title': 'Error',
    })