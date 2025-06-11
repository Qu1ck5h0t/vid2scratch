import av
import os
import cv2
import shutil
import ffmpeg
import json
import zipfile
import numpy as np
import hashlib


def vidconvert(input_path):
    import tempfile

    output_folder = 'project'
    temp_video = 'temp.mp4'
    target_width, target_height = 960, 720

    os.makedirs(output_folder, exist_ok=True)

    (
        ffmpeg
        .input(input_path)
        .output(temp_video, r=30, vsync='cfr')
        .run(quiet=True, overwrite_output=True)
    )

    # Read fixed frame-rate video and extract all frames
    container = av.open(temp_video)
    stream = container.streams.video[0]
    stream.thread_type = 'AUTO'

    saved_count = 0
    for frame in container.decode(stream):
        img = frame.to_ndarray(format='bgr24')
        h, w = img.shape[:2]
        scale = min(target_width / w, target_height / h)
        resized = cv2.resize(img, (int(w * scale), int(h * scale)))
        canvas = cv2.copyMakeBorder(
            resized,
            top=(target_height - resized.shape[0]) // 2,
            bottom=(target_height - resized.shape[0] + 1) // 2,
            left=(target_width - resized.shape[1]) // 2,
            right=(target_width - resized.shape[1] + 1) // 2,
            borderType=cv2.BORDER_CONSTANT,
            value=[0, 0, 0]
        )
        filename = os.path.join(output_folder, f'frame_{saved_count:05d}.png')
        cv2.imwrite(filename, canvas)
        saved_count += 1



def audioextract(input_path):
    output_path='audio.wav'
    (
        ffmpeg
        .input(input_path)
        .output(output_path, format='wav', acodec='pcm_s16le', ar=44100, ac=2)
        .run()
    )


file = input('Enter filename: ')

vidconvert(file)
audioextract('temp.mp4')
os.remove('temp.mp4')
shutil.copyfile("project.json", "project/project.json")
shutil.copyfile("audio.wav", "project/audio.wav")

folder = 'project'
json_path = os.path.join(folder, 'project.json')
audio_path = os.path.join(folder, 'audio.wav')
hashes = []

with open(audio_path, 'rb') as f:
    data = f.read()
    audio_hash = hashlib.md5(data).hexdigest()

new_audio_name = f'{audio_hash}.wav'
new_audio_path = os.path.join(folder, new_audio_name)
os.rename(audio_path, new_audio_path)

with open(json_path, 'r') as f:
    project_data = json.load(f)

files = sorted([f for f in os.listdir(folder) if f.startswith('frame_') and f.endswith('.png')])

for filename in files:
    path = os.path.join(folder, filename)
    with open(path, 'rb') as f:
        data = f.read()
        md5 = hashlib.md5(data).hexdigest()
        hashes.append(md5)
    new_path = os.path.join(folder, md5 + '.png')
    os.rename(path, new_path)

costumes = []
for index, h in enumerate(hashes):
    costumes.append({
        "assetId": h,
        "name": str(index),
        "bitmapResolution": 2,
        "md5ext": f"{h}.png",
        "dataFormat": "png",
        "rotationCenterX": 480,
        "rotationCenterY": 360
    })

project_data['targets'][0]['costumes'] = costumes

repeat_block_id = "+}Oo:`XH.%,K}fxbye7%"
repeat_block = project_data['targets'][0]['blocks'][repeat_block_id]
repeat_block['inputs']['TIMES'][1][1] = str(len(hashes))

project_data['targets'][0]['sounds'][0]['assetId'] = audio_hash
project_data['targets'][0]['sounds'][0]['md5ext'] = f'{audio_hash}.wav'

with open(json_path, 'w') as f:
    json.dump(project_data, f, separators=(',', ':'))

zf = zipfile.ZipFile("project.zip", "w")
for dirname, subdirs, files in os.walk("project"):
    for filename in files:
        filepath = os.path.join(dirname, filename)
        arcname = os.path.relpath(filepath, "project")
        zf.write(filepath, arcname=arcname)
zf.close()

os.rename('project.zip', 'project.sb3')
os.remove('audio.wav')
shutil.rmtree('project')