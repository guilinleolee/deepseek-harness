#!/usr/bin/env python3
"""
YouTube Ultimate - Zero-quota YouTube transcript extraction + search + comments + download
Version: 4.2.2
Source: https://github.com/openclaw/skills/tree/main/skills/globalcaos/youtube-ultimate
"""

import argparse
import json
import os
import pickle
import sys
from pathlib import Path
from typing import Optional

# Configuration paths
CONFIG_DIR = Path.home() / ".config" / "youtube-skill"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
TOKEN_FILE = CONFIG_DIR / "token.pickle"

# Fallback path for gogcli compatibility
GOGCLI_CREDENTIALS = Path.home() / ".config" / "gogcli" / "credentials.json"


def setup_dependencies():
    """Check and install dependencies if needed."""
    try:
        import youtube_transcript_api
        import googleapiclient
        import google_auth_oauthlib
    except ImportError:
        print("Installing dependencies...")
        import subprocess
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "youtube-transcript-api",
            "google-api-python-client",
            "google-auth-oauthlib",
            "google-auth-httplib2"
        ])


def get_credentials():
    """Get OAuth credentials, prompting for auth if needed."""
    from google_auth_oauthlib import flow
    from google.auth.transport import requests
    from google.oauth2 import credentials as oauth_credentials

    # Check for credentials file
    creds_path = CREDENTIALS_FILE if CREDENTIALS_FILE.exists() else GOGCLI_CREDENTIALS
    if not creds_path.exists():
        print(f"Error: No credentials found at {CREDENTIALS_FILE} or {GOGCLI_CREDENTIALS}")
        print("\nPlease:")
        print("1. Go to https://console.cloud.google.com/apis/credentials")
        print("2. Create an OAuth 2.0 Client ID (Desktop app)")
        print("3. Download the JSON file")
        print(f"4. Save it to {CREDENTIALS_FILE}")
        sys.exit(1)

    # Load client config
    with open(creds_path) as f:
        client_config = json.load(f)

    client_id = client_config.get("installed", client_config).get("client_id")
    client_secret = client_config.get("installed", client_config).get("client_secret")

    # Check for existing token
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

        # Refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(requests.Request())
            with open(TOKEN_FILE, "wb") as f:
                pickle.dump(creds, f)

        return creds

    # Need to authenticate
    app_flow = flow.InstalledAppFlow.from_client_secrets_file(
        str(creds_path),
        scopes=["https://www.googleapis.com/auth/youtube.readonly"]
    )
    creds = app_flow.run_local_server(port=18090)

    # Save token
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_FILE, "wb") as f:
        pickle.dump(creds, f)

    return creds


def get_youtube_service():
    """Build YouTube API service."""
    from googleapiclient import discovery

    creds = get_credentials()
    return discovery.build("youtube", "v3", credentials=creds)


# ============== Transcript Functions (Zero Quota!) ==============

def get_transcript(video_id: str, language: str = "en", timestamps: bool = False, json_output: bool = False):
    """
    Get transcript with zero API quota.
    Uses youtube-transcript-api which accesses YouTube frontend directly.
    """
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)

        # Try requested languages in order
        languages = [l.strip() for l in language.split(",")]
        transcript = None

        for lang in languages:
            try:
                transcript = transcript_list.find_transcript([lang])
                break
            except NoTranscriptFound:
                continue

        # Fallback to auto-generated
        if not transcript:
            try:
                transcript = transcript_list.find_generated_transcript(languages)
            except NoTranscriptFound:
                print(f"Error: No transcript found for video {video_id}")
                sys.exit(1)

        fetched = transcript.fetch()

        if json_output:
            print(json.dumps(fetched, ensure_ascii=False, indent=2))
            return

        for entry in fetched:
            if timestamps:
                start = entry.get("start", 0)
                mins, secs = divmod(int(start), 60)
                print(f"[{mins:02d}:{secs:02d}] {entry['text']}")
            else:
                print(entry["text"])

    except TranscriptsDisabled:
        print(f"Error: Transcripts are disabled for video {video_id}")
        sys.exit(1)
    except Exception as e:
        print(f"Error getting transcript: {e}")
        sys.exit(1)


# ============== Search Functions ==============

def search_videos(query: str, limit: int = 10, order: str = "relevance",
                  duration: Optional[str] = None, published_after: Optional[str] = None,
                  json_output: bool = False):
    """Search YouTube videos."""
    youtube = get_youtube_service()

    params = {
        "q": query,
        "part": "id,snippet",
        "maxResults": min(limit, 50),
        "type": "video",
        "order": order
    }

    if duration:
        params["videoDuration"] = duration
    if published_after:
        from datetime import datetime
        dt = datetime.strptime(published_after, "%Y-%m-%d")
        params["publishedAfter"] = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    response = youtube.search().list(**params).execute()

    results = []
    for item in response.get("items", []):
        video = {
            "id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "channel": item["snippet"]["channelTitle"],
            "published": item["snippet"]["publishedAt"],
            "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        }
        results.append(video)

    if json_output:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for i, v in enumerate(results, 1):
            print(f"\n{i}. {v['title']}")
            print(f"   ID: {v['id']}")
            print(f"   Channel: {v['channel']}")
            print(f"   URL: {v['url']}")


# ============== Video Details ==============

def get_video_details(video_ids: list, json_output: bool = False):
    """Get video details (supports batch up to 50)."""
    youtube = get_youtube_service()

    # Batch in groups of 50
    all_results = []

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(batch)
        ).execute()

        for item in response.get("items", []):
            stats = item.get("statistics", {})
            snippet = item.get("snippet", {})
            content = item.get("contentDetails", {})

            video = {
                "id": item["id"],
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "channel": snippet.get("channelTitle"),
                "channelId": snippet.get("channelId"),
                "published": snippet.get("publishedAt"),
                "duration": content.get("duration"),
                "views": stats.get("viewCount", "0"),
                "likes": stats.get("likeCount", "0"),
                "comments": stats.get("commentCount", "0"),
                "tags": snippet.get("tags", []),
                "url": f"https://www.youtube.com/watch?v={item['id']}"
            }
            all_results.append(video)

    if json_output:
        print(json.dumps(all_results, ensure_ascii=False, indent=2))
    else:
        for v in all_results:
            print(f"\n{'='*60}")
            print(f"Title: {v['title']}")
            print(f"ID: {v['id']}")
            print(f"Channel: {v['channel']}")
            print(f"Views: {int(v['views']):,} | Likes: {int(v['likes']):,} | Comments: {int(v['comments']):,}")
            print(f"Duration: {v['duration']}")
            print(f"URL: {v['url']}")


# ============== Comments ==============

def get_comments(video_id: str, limit: int = 20, replies: bool = False, json_output: bool = False):
    """Get video comments."""
    youtube = get_youtube_service()

    results = []
    next_page = None

    while len(results) < limit:
        params = {
            "part": "snippet",
            "videoId": video_id,
            "maxResults": min(100, limit - len(results)),
            "order": "relevance",
            "textFormat": "plainText"
        }
        if next_page:
            params["pageToken"] = next_page

        response = youtube.commentThreads().list(**params).execute()

        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]
            result = {
                "id": item["id"],
                "author": comment.get("authorDisplayName"),
                "text": comment.get("textDisplay"),
                "likes": comment.get("likeCount", 0),
                "published": comment.get("publishedAt"),
                "replies": []
            }

            # Get replies if requested
            if replies and item.get("snippet", {}).get("totalReplyCount", 0) > 0:
                reply_response = youtube.comments().list(
                    part="snippet",
                    parentId=item["id"],
                    maxResults=100
                ).execute()

                for reply in reply_response.get("items", []):
                    reply_snippet = reply["snippet"]
                    result["replies"].append({
                        "id": reply["id"],
                        "author": reply_snippet.get("authorDisplayName"),
                        "text": reply_snippet.get("textDisplay"),
                        "likes": reply_snippet.get("likeCount", 0),
                        "published": reply_snippet.get("publishedAt")
                    })

            results.append(result)

        next_page = response.get("nextPageToken")
        if not next_page:
            break

    results = results[:limit]

    if json_output:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for i, c in enumerate(results, 1):
            print(f"\n{i}. {c['author']} (👍 {c['likes']})")
            print(f"   {c['text'][:200]}{'...' if len(c['text']) > 200 else ''}")
            if c['replies']:
                print(f"   └── {len(c['replies'])} replies")


# ============== Channel ==============

def get_channel(channel_id: Optional[str] = None, json_output: bool = False):
    """Get channel information."""
    youtube = get_youtube_service()

    if channel_id:
        response = youtube.channels().list(
            part="snippet,statistics,contentDetails",
            id=channel_id
        ).execute()
    else:
        # Get authenticated user's channel
        response = youtube.channels().list(
            part="snippet,statistics,contentDetails",
            mine=True
        ).execute()

    results = []
    for item in response.get("items", []):
        stats = item.get("statistics", {})
        snippet = item.get("snippet", {})

        channel = {
            "id": item["id"],
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "customUrl": snippet.get("customUrl"),
            "published": snippet.get("publishedAt"),
            "subscribers": stats.get("subscriberCount", "0"),
            "views": stats.get("viewCount", "0"),
            "videoCount": stats.get("videoCount", "0"),
            "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url"),
            "url": f"https://www.youtube.com/channel/{item['id']}"
        }
        results.append(channel)

    if json_output:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for ch in results:
            print(f"\n{'='*60}")
            print(f"Channel: {ch['title']}")
            print(f"ID: {ch['id']}")
            print(f"Subscribers: {int(ch['subscribers']):,}")
            print(f"Total Views: {int(ch['views']):,}")
            print(f"Videos: {ch['videoCount']}")
            print(f"URL: {ch['url']}")


def get_subscriptions(json_output: bool = False):
    """Get authenticated user's subscriptions."""
    youtube = get_youtube_service()

    results = []
    next_page = None

    while True:
        params = {"part": "snippet", "maxResults": 50}
        if next_page:
            params["pageToken"] = next_page

        response = youtube.subscriptions().list(**params).execute()

        for item in response.get("items", []):
            snippet = item["snippet"]
            results.append({
                "id": snippet["resourceId"]["channelId"],
                "title": snippet["title"],
                "url": f"https://www.youtube.com/channel/{snippet['resourceId']['channelId']}"
            })

        next_page = response.get("nextPageToken")
        if not next_page:
            break

    if json_output:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"Total subscriptions: {len(results)}")
        for i, sub in enumerate(results, 1):
            print(f"{i}. {sub['title']}")


def get_playlists(json_output: bool = False):
    """Get authenticated user's playlists."""
    youtube = get_youtube_service()

    response = youtube.playlists().list(
        part="snippet,contentDetails",
        mine=True,
        maxResults=50
    ).execute()

    results = []
    for item in response.get("items", []):
        snippet = item["snippet"]
        results.append({
            "id": item["id"],
            "title": snippet["title"],
            "videoCount": item["contentDetails"]["itemCount"],
            "url": f"https://www.youtube.com/playlist?list={item['id']}"
        })

    if json_output:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"Total playlists: {len(results)}")
        for i, pl in enumerate(results, 1):
            print(f"{i}. {pl['title']} ({pl['videoCount']} videos)")


# ============== Download ==============

def download_video(video_id: str, resolution: str = "best", subtitles: Optional[str] = None):
    """Download video using yt-dlp."""
    import subprocess

    url = f"https://www.youtube.com/watch?v={video_id}"

    cmd = ["yt-dlp", "-f", f"bestvideo[height<={resolution}]+bestaudio/best" if resolution != "best" else "best"]

    if subtitles:
        cmd.extend(["--write-subs", "--sub-langs", subtitles])

    cmd.append(url)

    print(f"Downloading: {url}")
    subprocess.run(cmd)


def download_audio(video_id: str, format: str = "mp3"):
    """Download audio only."""
    import subprocess

    url = f"https://www.youtube.com/watch?v={video_id}"

    cmd = [
        "yt-dlp",
        "-x", "--audio-format", format,
        url
    ]

    print(f"Downloading audio: {url}")
    subprocess.run(cmd)


# ============== Auth ==============

def authenticate():
    """Run OAuth authentication flow."""
    print("Starting OAuth authentication...")
    get_credentials()
    print(f"Authentication successful! Token saved to {TOKEN_FILE}")


def list_accounts():
    """List authenticated accounts."""
    if TOKEN_FILE.exists():
        print(f"Token found: {TOKEN_FILE}")
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)
        print(f"  Expired: {creds.expired}")
        print(f"  Valid: {creds.valid}")
    else:
        print("No token found. Run 'auth' to authenticate.")


# ============== Main ==============

def main():
    parser = argparse.ArgumentParser(
        description="YouTube Ultimate - Zero-quota transcript + search + comments + download"
    )
    parser.add_argument("--account", help="Use specific account")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Transcript (zero quota!)
    trans_parser = subparsers.add_parser("transcript", help="Get video transcript (ZERO QUOTA)")
    trans_parser.add_argument("video_id", help="YouTube video ID")
    trans_parser.add_argument("-l", "--language", default="en", help="Language(s), comma-separated (default: en)")
    trans_parser.add_argument("-t", "--timestamps", action="store_true", help="Include timestamps")
    trans_parser.add_argument("--json", action="store_true", help="JSON output")

    # Search
    search_parser = subparsers.add_parser("search", help="Search videos")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results")
    search_parser.add_argument("--order", default="relevance",
                               choices=["relevance", "date", "viewCount", "rating"])
    search_parser.add_argument("--duration", choices=["short", "medium", "long"])
    search_parser.add_argument("--published-after", help="YYYY-MM-DD")
    search_parser.add_argument("--json", action="store_true")

    # Video details
    video_parser = subparsers.add_parser("video", help="Get video details")
    video_parser.add_argument("video_ids", nargs="+", help="Video ID(s)")
    video_parser.add_argument("--json", action="store_true")

    # Comments
    comments_parser = subparsers.add_parser("comments", help="Get video comments")
    comments_parser.add_argument("video_id", help="YouTube video ID")
    comments_parser.add_argument("--limit", type=int, default=20)
    comments_parser.add_argument("--replies", action="store_true", help="Include replies")
    comments_parser.add_argument("--json", action="store_true")

    # Channel
    channel_parser = subparsers.add_parser("channel", help="Get channel info")
    channel_parser.add_argument("channel_id", nargs="?", help="Channel ID (default: your channel)")
    channel_parser.add_argument("--json", action="store_true")

    # Subscriptions
    subparsers.add_parser("subscriptions", help="List your subscriptions")

    # Playlists
    subparsers.add_parser("playlists", help="List your playlists")

    # Download video
    dl_parser = subparsers.add_parser("download", help="Download video")
    dl_parser.add_argument("video_id")
    dl_parser.add_argument("-r", "--resolution", default="best", help="Max resolution (e.g., 1080p, 4k)")
    dl_parser.add_argument("-s", "--subtitles", help="Download subtitles (e.g., en,zh)")

    # Download audio
    audio_parser = subparsers.add_parser("download-audio", help="Download audio only")
    audio_parser.add_argument("video_id")
    audio_parser.add_argument("-f", "--format", default="mp3", choices=["mp3", "m4a", "wav"])

    # Auth
    subparsers.add_parser("auth", help="Authenticate with OAuth")
    subparsers.add_parser("accounts", help="List authenticated accounts")

    args = parser.parse_args()

    # Setup dependencies
    setup_dependencies()

    # Execute command
    if args.command == "transcript":
        get_transcript(args.video_id, args.language, args.timestamps, args.json)
    elif args.command == "search":
        search_videos(args.query, args.limit, args.order, args.duration,
                      args.published_after, args.json)
    elif args.command == "video":
        get_video_details(args.video_ids, args.json)
    elif args.command == "comments":
        get_comments(args.video_id, args.limit, args.replies, args.json)
    elif args.command == "channel":
        get_channel(args.channel_id, args.json)
    elif args.command == "subscriptions":
        get_subscriptions()
    elif args.command == "playlists":
        get_playlists()
    elif args.command == "download":
        download_video(args.video_id, args.resolution, args.subtitles)
    elif args.command == "download-audio":
        download_audio(args.video_id, args.format)
    elif args.command == "auth":
        authenticate()
    elif args.command == "accounts":
        list_accounts()


if __name__ == "__main__":
    main()