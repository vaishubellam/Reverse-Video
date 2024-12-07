import cv2
import numpy as np
from scipy.io import wavfile
import moviepy.editor as mp
import os
import time

def reverse_video(input_path, output_path):
    try:
        # Generate unique temporary file names
        timestamp = int(time.time())
        temp_audio = f"temp_audio_{timestamp}.wav"
        temp_reversed_audio = f"temp_reversed_audio_{timestamp}.wav"
        temp_video = f"temp_video_{timestamp}.mp4"

        try:
            # Extract audio from the original video
            print("Extracting audio...")
            video = mp.VideoFileClip(input_path)
            if video.audio is not None:
                video.audio.write_audiofile(temp_audio)
            video.close()

            # Open the video
            print("Loading video...")
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                raise Exception("Error: Could not open video file")

            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Create VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))

            # Read and reverse frames
            print("Reading and reversing frames...")
            frames = []
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)

            print(f"Writing {len(frames)} frames in reverse...")
            for frame in reversed(frames):
                out.write(frame)

            # Release video objects
            cap.release()
            out.release()
            cv2.destroyAllWindows()

            # Handle audio if it exists
            if os.path.exists(temp_audio):
                print("Reversing audio...")
                sample_rate, audio_data = wavfile.read(temp_audio)
                reversed_audio = audio_data[::-1]
                wavfile.write(temp_reversed_audio, sample_rate, reversed_audio)

                # Combine video and audio
                print("Combining video and audio...")
                video = mp.VideoFileClip(temp_video)
                audio = mp.AudioFileClip(temp_reversed_audio)
                final_clip = video.set_audio(audio)
                
                # Write final video with proper codec settings
                final_clip.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile=f"temp_audio_final_{timestamp}.m4a",
                    remove_temp=True,
                    fps=fps
                )
                
                # Close clips
                video.close()
                audio.close()
                final_clip.close()
            else:
                # If no audio, just rename the temp video
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(temp_video, output_path)

            print("Video reversal completed successfully!")

        finally:
            # Cleanup temporary files
            print("Cleaning up temporary files...")
            time.sleep(1)  # Small delay to ensure files are released
            for temp_file in [temp_audio, temp_reversed_audio, temp_video]:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception as e:
                    print(f"Warning: Could not remove temporary file {temp_file}: {str(e)}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise
