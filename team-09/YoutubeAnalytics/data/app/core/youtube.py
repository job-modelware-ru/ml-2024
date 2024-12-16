import googleapiclient.discovery


class Youtube():
    def __init__(self, youtube_api_key) -> None:
        self.videos: dict = None
        self.youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=youtube_api_key)

    def search_channels(self, category: str) -> list:
        request = self.youtube.search().list(
            part="snippet",
            maxResults=50,
            order="videoCount",
            q=category,
            type="channel"
        )

        response = request.execute()

        channels = list()

        for channel in response["items"]:
            channels.append(channel["id"]["channelId"])

        return channels

    def get_channel(self, channel_id: str) -> dict:
        request = self.youtube.channels().list(
            part="snippet,contentDetails,statistics,brandingSettings",
            id=channel_id
        )

        response = request.execute()

        response_channel = response["items"][0]

        channel = {
            "id": response_channel["id"],
            "title": response_channel["snippet"]["title"] if "title" in response_channel["snippet"] else None,
            "description": response_channel["snippet"]["description"] if "description" in response_channel["snippet"] else None,
            "customUrl": response_channel["snippet"]["customUrl"] if "customUrl" in response_channel["snippet"] else None,
            "publishedAt": response_channel["snippet"]["publishedAt"] if "publishedAt" in response_channel["snippet"] else None,
            "country": response_channel["snippet"]["country"] if "country" in response_channel["snippet"] else None,
            "viewCount": response_channel["statistics"]["viewCount"] if "viewCount" in response_channel["statistics"] else None,
            "subscriberCount": response_channel["statistics"]["subscriberCount"] if "subscriberCount" in response_channel["statistics"] else None,
            "hiddenSubscriberCount": response_channel["statistics"]["hiddenSubscriberCount"] if "hiddenSubscriberCount" in response_channel["statistics"] else None,
            "videoCount": response_channel["statistics"]["videoCount"] if "videoCount" in response_channel["statistics"] else None,
            "keywords": response_channel["brandingSettings"]["channel"]["keywords"] if "keywords" in response_channel["brandingSettings"]["channel"] else None
        }

        return channel

    def get_channel_by_url(self, url: str) -> dict:
        request = self.youtube.search().list(
            q=url,
            part='id',
            type='channel',
            fields='items(id(channelId))',
            maxResults=1
        )

        response = request.execute()

        channel_id = response["items"][0]["id"]["channelId"]

        return self.get_channel(channel_id)

    def get_channel_by_video_id(self, video_id: str) -> dict:
        request = self.youtube.videos().list(
            part="snippet",
            id=video_id,
            fields="items(snippet(channelId))",
            maxResults=1
        )

        response = request.execute()

        channel_id = response["items"][0]["snippet"]["channelId"]

        return self.get_channel(channel_id)

    def get_videos(self, playlist_id: str, page_token: str):
        request = self.youtube.playlistItems().list(
            part="snippet,contentDetails",
            maxResults=50,
            pageToken=page_token,
            playlistId=playlist_id
        )
        response = request.execute()

        next_page_token = response["nextPageToken"] if "nextPageToken" in response else None

        response_videos = response["items"]

        videos_ids = list()
        for video in response_videos:
            videos_ids.append(video["contentDetails"]["videoId"])

        return (next_page_token, videos_ids)

    def get_video(self, video_id: str):
        request = self.youtube.videos().list(
            part="snippet,contentDetails,statistics,topicDetails",
            id=video_id
        )
        response = request.execute()

        if len(response["items"]) == 0:
            return

        response_video = response["items"][0]

        video = {
            "publishedAt": response_video["snippet"]["publishedAt"] if "publishedAt" in response_video["snippet"] else None,
            "channelId": response_video["snippet"]["channelId"] if "channelId" in response_video["snippet"] else None,
            "title": response_video["snippet"]["title"] if "title" in response_video["snippet"] else None,
            "description": response_video["snippet"]["description"] if "description" in response_video["snippet"] else None,
            "tags": response_video["snippet"]["tags"] if "tags" in response_video["snippet"] else None,
            "categoryId": response_video["snippet"]["categoryId"] if "categoryId" in response_video["snippet"] else None,
            "liveBroadcastContent": response_video["snippet"]["liveBroadcastContent"] if "liveBroadcastContent" in response_video["snippet"] else None,
            "defaultLanguage": response_video["snippet"]["defaultLanguage"] if "defaultLanguage" in response_video["snippet"] else None,
            "defaultAudioLanguage": response_video["snippet"]["defaultAudioLanguage"] if "defaultAudioLanguage" in response_video["snippet"] else None,
            "duration": response_video["contentDetails"]["duration"] if "duration" in response_video["contentDetails"] else None,
            "dimension": response_video["contentDetails"]["dimension"] if "dimension" in response_video["contentDetails"] else None,
            "definition": response_video["contentDetails"]["definition"] if "definition" in response_video["contentDetails"] else None,
            "caption": response_video["contentDetails"]["caption"] if "caption" in response_video["contentDetails"] else None,
            "licensedContent": response_video["contentDetails"]["licensedContent"] if "licensedContent" in response_video["contentDetails"] else None,
            "contentRating": response_video["contentDetails"]["contentRating"] if "contentRating" in response_video["contentDetails"] else None,
            "projection": response_video["contentDetails"]["projection"] if "projection" in response_video["contentDetails"] else None,
            "viewCount": response_video["statistics"]["viewCount"] if "viewCount" in response_video["statistics"] else None,
            "likeCount": response_video["statistics"]["likeCount"] if "likeCount" in response_video["statistics"] else None,
            "favoriteCount": response_video["statistics"]["favoriteCount"] if "favoriteCount" in response_video["statistics"] else None,
            "commentCount": response_video["statistics"]["commentCount"] if "commentCount" in response_video["statistics"] else None,
            "topicCategories": response_video["topicDetails"]["topicCategories"] if "topicDetails" in response_video and "topicCategories" in response_video["topicDetails"] else None,
        }

        return video

    def get_comments(self, video_id: str, pageToken: str):
        request = self.youtube.commentThreads().list(
            part="snippet,replies",
            maxResults=100,
            videoId=video_id,
            pageToken=pageToken
        )
        response = request.execute()

        next_page_token = response["nextPageToken"] if "nextPageToken" in response else None

        response_comments = response["items"]

        comments = list()
        for response_comment in response_comments:
            tmp = response_comment["snippet"]["topLevelComment"]["snippet"]
            comment = {
                "id": response_comment["id"] if "id" in response_comment else None,
                "videoId": video_id,
                "textDisplay": tmp["textDisplay"] if "textDisplay" in tmp else None,
                "textOriginal": tmp["textOriginal"] if "textOriginal" in tmp else None,
                "authorDisplayName": tmp["authorDisplayName"] if "authorDisplayName" in tmp else None,
                "authorProfileImageUrl": tmp["authorProfileImageUrl"] if "authorProfileImageUrl" in tmp else None,
                "authorChannelUrl": tmp["authorChannelUrl"] if "authorChannelUrl" in tmp else None,
                "authorChannelId": tmp["authorChannelId"]["value"] if "authorChannelId" in tmp else None,
                "viewerRating": tmp["viewerRating"] if "viewerRating" in tmp else None,
                "likeCount": tmp["likeCount"] if "likeCount" in tmp else None,
                "publishedAt": tmp["publishedAt"] if "publishedAt" in tmp else None,
                "updatedAt": tmp["updatedAt"] if "updatedAt" in tmp else None,
                "totalReplyCount": response_comment["snippet"]["totalReplyCount"] if "totalReplyCount" in response_comment["snippet"] else None,
                "isReply": False
            }

            comments.append(comment)

            if 'replies' in response_comment:
                for resp_reply in response_comment['replies']['comments']:
                    reply = {
                        "id": resp_reply["id"] if "id" in resp_reply else None,
                        "videoId": video_id,
                        "textDisplay": resp_reply["snippet"]["textDisplay"] if "textDisplay" in resp_reply["snippet"] else None,
                        "textOriginal": resp_reply["snippet"]["textOriginal"] if "textOriginal" in resp_reply["snippet"] else None,
                        "parentId": resp_reply["snippet"]["parentId"] if "parentId" in resp_reply["snippet"] else None,
                        "authorDisplayName": resp_reply["snippet"]["authorDisplayName"] if "authorDisplayName" in resp_reply["snippet"] else None,
                        "authorProfileImageUrl": resp_reply["snippet"]["authorProfileImageUrl"] if "authorProfileImageUrl" in resp_reply["snippet"] else None,
                        "authorChannelUrl": resp_reply["snippet"]["authorChannelUrl"] if "authorChannelUrl" in resp_reply["snippet"] else None,
                        "authorChannelId": resp_reply["snippet"]["authorChannelId"]["value"] if "authorChannelId" in resp_reply["snippet"] else None,
                        "canRate": resp_reply["snippet"]["canRate"] if "canRate" in resp_reply["snippet"] else None,
                        "viewerRating": resp_reply["snippet"]["viewerRating"] if "viewerRating" in resp_reply["snippet"] else None,
                        "likeCount": resp_reply["snippet"]["likeCount"] if "likeCount" in resp_reply["snippet"] else None,
                        "publishedAt": resp_reply["snippet"]["publishedAt"] if "publishedAt" in resp_reply["snippet"] else None,
                        "updatedAt": resp_reply["snippet"]["updatedAt"] if "updatedAt" in resp_reply["snippet"] else None,
                        "isReply": True
                    }
                    comments.append(reply)

        return (next_page_token, comments)

    def __del__(self) -> None:
        self.youtube.close()
