from pytubefix import YouTube

def _timestamp_to_seconds(timestamp: str) -> float:
    """Convert SRT timestamp to seconds."""
    if ',' in timestamp:
        timestamp = timestamp.replace(',', '.')
    
    parts = timestamp.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
    return 0

def _parse_srt_captions(srt_captions: str):
    """Parse SRT format captions into segments."""
    segments = []
    current_segment = {}
    
    for line in srt_captions.split('\n'):
        line = line.strip()
        
        if line.isdigit():  # Segment number
            if current_segment:
                segments.append(current_segment)
            current_segment = {}
        elif '-->' in line:  # Timestamp
            start, end = line.split('-->')
            current_segment['start'] = _timestamp_to_seconds(start.strip())
            current_segment['end'] = _timestamp_to_seconds(end.strip())
        elif line:  # Text content
            if 'text' in current_segment:
                current_segment['text'] += ' ' + line
            else:
                current_segment['text'] = line
    
    if current_segment:
        segments.append(current_segment)
    
    return segments

def combine_text(segments):
    """Combine text from all segments."""
    return " ".join(info['text'] for info in segments)

def get_youtube_caption(video_url):
    """Extract captions from YouTube video."""
    yt = YouTube(url=video_url)

    if yt.captions and 'a.en' in yt.captions:
        caption = yt.captions['a.en']
    elif yt.captions and 'en' in yt.captions:
        caption = yt.captions['en']
    else:
        raise ValueError("No English captions found for this video")

    raw_captions = caption.generate_srt_captions()
    segments = _parse_srt_captions(raw_captions)
    return combine_text(segments) 