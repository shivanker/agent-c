#! /usr/bin/python3

import re
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url):
    """
    Function to extract the video id from a YouTube URL.
    """

    # Standard YouTube URLs (e.g., "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    match = re.search(r"youtube\.com.*v=([^&]*)", url)
    if match:
        return match.group(1)

    # Shortened YouTube URLs (e.g., "https://youtu.be/dQw4w9WgXcQ")
    match = re.search(r"youtu\.be/([^?/]*)", url)
    if match:
        return match.group(1)

    # Embedded YouTube URLs (e.g., "https://www.youtube.com/embed/dQw4w9WgXcQ")
    match = re.search(r"youtube\.com/embed/([^?/]*)", url)
    if match:
        return match.group(1)

    # Live YouTube URLs (e.g., "https://www.youtube.com/live/dQw4w9WgXcQ")
    match = re.search(r"youtube\.com/live/([^?/]*)", url)
    if match:
        return match.group(1)

    return None


def yt_transcript(url: str) -> str:
    """Function to fetch the transcript of a YouTube video, given the URL."""
    video_id = extract_video_id(url)
    if video_id:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        if transcript:
            return " ".join(f"[{segment['start']:.2f}] {segment['text']}" for segment in transcript)
    return "Unable to fetch transcript."
