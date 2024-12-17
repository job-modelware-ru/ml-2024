import $api from "../http";
import { AxiosResponse } from "axios";
import { ChannelGroupResponse } from "../models/response/ChannelGroupResponse";
import { VideoGroupResponse } from "../models/response/VideogroupResponse";
import { IVideo } from "../models/IVideo";
import { IChannel } from "../models/IChannel";

export default class GroupService {
  static async createGroup(
    title: string,
    type: string
  ): Promise<AxiosResponse> {
    if (type === "video")
      return $api.post(`video-group/`, { title, videos: [] });

    return $api.post(`channel-group/`, { title, channel: [] });
  }

  static async getChannelGroups(): Promise<
    AxiosResponse<Array<ChannelGroupResponse>>
  > {
    return $api.get(`channel-group/`);
  }

  static async getVideoGroups(): Promise<
    AxiosResponse<Array<VideoGroupResponse>>
  > {
    return $api.get(`video-group/`);
  }

  static async addVideoToGroup(
    groupId: number,
    videoId: string
  ): Promise<AxiosResponse<IVideo>> {
    return $api.post(`add-video-to-group/`, {
      video_group_id: groupId,
      video_yt_id: videoId,
    });
  }

  static async downloadVideo(videoId: string): Promise<AxiosResponse> {
    return $api.post("request/", {
      type: 6,
      data: `{"id": "${videoId}"}`,
    });
  }

  static async getVideosInGroup(groupId: number): Promise<AxiosResponse> {
    return $api.get(`video-group/${groupId}/`);
  }

  static async addChannelToGroup(
    groupId: number,
    custom_url: string
  ): Promise<AxiosResponse<IChannel>> {
    return $api.post(`add-channel-to-group/`, {
      channel_group_id: groupId,
      custom_url: custom_url,
    });
  }

  static async downloadChannel(channelUrl: string): Promise<AxiosResponse> {
    return $api.post("request/", {
      type: 5,
      data: `{"url": "${channelUrl}"}`,
    });
  }

  static async getChannelsInGroup(groupId: number): Promise<AxiosResponse> {
    return $api.get(`channel-group/${groupId}/`);
  }
}
