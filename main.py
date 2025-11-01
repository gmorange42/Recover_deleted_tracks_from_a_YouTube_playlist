from yt_dlp import YoutubeDL
import requests
import regex as re
import time


#url_test = "https://www.youtube.com/playlist?list=PLEpUZRCgPsBwDoOuK8LRBisfOzOta6EYx"


def enter_url():
    """Ask the user to enter the playlist URL."""
    return input("Enter the URL of your playlist:")


def get_removed_video_id():
    """Return a list of IDs for deleted videos in the playlist."""
    while True:
        try:
            url = enter_url()
            # Extract playlist info without downloading any videos
            ydl_opts = {'extract_flat': True, 'quiet': True}
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                # Keep only entries where the title is '[Deleted video]'
                ids = [entry['id'] for entry in info['entries'] if entry['title'] == '[Deleted video]']

            return ids
        
        except:
            # Ask again if the URL is invalid or extraction fails
            print("Invalid URL, please enter the URL of your playlist.")


def main():
    # Get IDs of deleted videos from the playlist
    ids = get_removed_video_id()

    for id in ids:
        print(f"Searching for the id: {id}")

        # Build CDX API URL to find archived versions on the Wayback Machine
        cdx_api = f"http://web.archive.org/cdx/search/cdx?url=https://www.youtube.com/watch?v={id}&output=json&fl=timestamp,original&collapse=digest"

        # Get the list of snapshots from the archive
        r_json = requests.get(cdx_api).json()

        # Skip if no snapshots were found
        if len(r_json) <= 1:
            print("No records found")
            continue

        # Use the most recent snapshot
        timestamp, url_video = r_json[-1][0], r_json[-1][1]

        try:

            # Fetch the archived YouTube page and extract the video title
            print(re.findall(r'"title"\s*:\s*{[^}]*?"text"\s*:\s*"([^"]+)"', requests.get(f"https://web.archive.org/web/{timestamp}/{url_video}").text)[0])

            # Build the archived thumbnail URL
            print(f'https://web.archive.org/web/{timestamp}im_/https://i.ytimg.com/vi/{id}/maxresdefault.jpg')

        except IndexError:
            # Happens if the regex didn’t find a title
            print("Title not found")
        except Exception as e:
            # Catch any other unexpected error
            print(f"An error has occurred: {e}")

        print('\n\n')

        # Sleep to avoid spamming the Wayback Machine
        time.sleep(1)


if __name__ == '__main__':
    main()