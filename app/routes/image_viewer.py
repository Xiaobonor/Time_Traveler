from flask import Blueprint, send_file, abort, render_template
import base64
import io

from app.models.journeys import Journeys

image_viewer_bp = Blueprint('image_viewer_bp', __name__)


@image_viewer_bp.route('/view/<uuid>/<int:page>')
def serve_image(uuid, page):
    journey = Journeys.get_journey_by_id(uuid)
    if not journey:
        abort(404, description="Property not found")

    if page < 1 or page > len(journey.images):
        abort(404, description="Image not found")

    base64_image = journey.images[page - 1]
    print(base64_image)
    print(len(base64_image))

    if base64_image.startswith('data:image/png;base64,'):
        base64_image_cleaned = base64_image[len('data:image/png;base64,'):]
        mimetype = 'image/png'
    elif base64_image.startswith('data:image/jpeg;base64,') or base64_image.startswith('data:image/jpg;base64,'):
        base64_image_cleaned = base64_image.split('base64,')[1]
        mimetype = 'image/jpeg'
    elif base64_image.startswith('data:image/webp;base64,'):
        base64_image_cleaned = base64_image[len('data:image/webp;base64,'):]
        mimetype = 'image/webp'
    elif base64_image.startswith('data:image/gif;base64,'):
        base64_image_cleaned = base64_image[len('data:image/gif;base64,'):]
        mimetype = 'image/gif'
    else:
        abort(400, description="Unsupported image type")

    missing_padding = len(base64_image_cleaned) % 4
    if missing_padding:
        print("Missing padding")
        base64_image_cleaned += '=' * (4 - missing_padding)

    image_data = base64.b64decode(base64_image_cleaned)
    image_io = io.BytesIO(image_data)
    return send_file(image_io, mimetype=mimetype, as_attachment=False, download_name='image.png')
