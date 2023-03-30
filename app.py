from flask import Flask, request, jsonify
import youtube_dl
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)



@app.route('/vimeo', methods=['GET'])
def get_download_link():
    vimeo_url = request.args.get('video_url')
    access_token = "c79042f73f91a02b8cb8274be1adf740"
    video_id = vimeo_url.split("/")[-1]
    print("video ID", video_id)
    url = f"https://api.vimeo.com/videos/{video_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    video_data = response.json()
    download_link = video_data["embed"]["html"]
    print("Vimeo Link", download_link)
    if download_link:
    # Modify iframe src
        iframe_src = download_link.replace('&amp;badge=0&amp;autopause=0&amp;player_id=0&amp;', '&amp;title=0&amp;controls=0&amp;loop=1&amp;background=1&amp;')

        # Set width and height attributes
        iframe_src = iframe_src.replace('width="1280" height="720"', 'width="640" height="360" data-ready="true"')

        return jsonify({'video_iframe': iframe_src})
    else:
        return jsonify({'error': 'Could not find any video '})


@app.route('/youtube', methods=['GET'])
def get_video_playback_link():
    video_url = request.args.get('video_url')
    with youtube_dl.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        formats = info_dict.get('formats', None)
        # print(info_dict)
        video_format = None
        format_list = []
        for f in formats:
            format_dict = {}
            format_dict['format_id'] = f.get('format_id')
            format_dict['resolution'] = f.get('height')
            format_dict['url'] = f.get('url')
            format_list.append(format_dict)
            if f.get('height') == 720:
                video_format = f
        if video_format:
            playback_url = video_format.get('url')
            return jsonify({'playback_url': playback_url, 'formats': format_list})
        else:
            if format_list:
                playback_url = format_list[0].get('url')
                return jsonify({'playback_url': playback_url, 'formats': format_list})
            else:
                return jsonify({'error': 'Could not find any video formats.'})



if __name__ == '__main__':
    app.run(debug=True)
