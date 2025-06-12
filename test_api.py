from src.core.youtube_client import YouTubeClient

def main():
    client = YouTubeClient()
    result = client.get_stream_details('cb12KmMMDJA')
    print("Resultado:", result)

if __name__ == "__main__":
    main() 