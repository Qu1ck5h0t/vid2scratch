# vid2scratch

### Here's a demonstration video
https://www.youtube.com/watch?v=n7H7HrzbOZc&t=438s

### How do I use this?
Clone the repo into a folder (ensure that all the files are in the same folder). After running install_dependencies.py, run main.py and follow the prompts.

### What does this do?
This tool converts any mp4 video into a scratch project that effectively acts as a runtime for a 720p 30fps video, with frames and audio included in the project file. The resolution is fitted through black bars, which is handled by the script.

### How does this work?
It converts a given video into 30fps, extracts each frame from the converted video then gets the MD5 hash each frame in order, renaming each frame to its hash and adding the hashes in an array to retain order. This is done due to how scratch handles assets, as it identifies assets based on their MD5 hashes in the project's json file rather than conventional naming. Hence, there exists a challenge in hashing the files and formatting them into the json should one want to manually add assets to a scratch project. My tool effectively handles this through the aforementioned logic, then copies the hashed audio and base json into the same folder as the frames, with the hashed json objects appended into the copied project.json. Finally the whole thing is zipped, with the extension changed to .sb3 as scratch projects are literally just zip files with renamed extensions. It cleans up the intermediary folders and temp files in the end, ensuring that only the converted scratch project remains. Within the project, the playback logic is handled by a single script that simply loops "switch to next costume" as scratch's tickrate is tied to its framerate which is 30fps by default, meaning that tick based updates works just fine for 30fps animation.

### Limitations
Since this uses frame by frame extraction, video compression does not apply to the file. This means that files will get very big very fast, making the conversion or display of longer videos unviable.
