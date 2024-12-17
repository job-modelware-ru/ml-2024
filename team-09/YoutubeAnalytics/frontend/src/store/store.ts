import { makeAutoObservable } from "mobx";
import AuthService from "../services/AuthService";
import axios from "axios";
import { AuthResponse } from "../models/response/AuthResponse";
import { API_URL } from "../http";
import ProfileService from "../services/ProfileService";
import { IProfile } from "../models/IProfile";
import GroupService from "../services/GroupService";
import { IVideoGroup } from "../models/IVideoGroup";
import { IChannelGroup } from "../models/IChannelGroup";
import { IVideo } from "../models/IVideo";
import { IChannel } from "../models/IChannel";

export default class Store {
  isAuth = false;
  isLoading = false;
  profile = {} as IProfile;
  videoGroups = [] as Array<IVideoGroup>;
  channelGroups = [] as Array<IChannelGroup>;
  choosed_type = "" as string;
  choosed_group_id = -1 as number;
  videos = {} as { [key: string]: IVideo };
  channels = {} as { [key: string]: IChannel };
  choosed_element_id = -1 as number;

  constructor() {
    makeAutoObservable(this);
  }

  setAuthState(state: boolean) {
    this.isAuth = state;
  }

  setLoading(state: boolean) {
    this.isLoading = state;
  }

  setProfile(profile: IProfile) {
    this.profile = profile;
  }

  setChannelGroups(channelGroups: Array<IChannelGroup>) {
    this.channelGroups = channelGroups;
  }

  setVideoGroups(videoGroups: Array<IVideoGroup>) {
    this.videoGroups = videoGroups;
  }

  addChannelGroup(channelGroup: IChannelGroup) {
    this.channelGroups.push(channelGroup);
  }

  addVideoGroup(videoGroup: IVideoGroup) {
    this.videoGroups.push(videoGroup);
  }

  async login(emailOrUsername: string, password: string) {
    try {
      const response = await AuthService.login(emailOrUsername, password);
      console.log(response);
      localStorage.setItem("token", response.data.token);
      this.setAuthState(true);
    } catch (e: any) {
      console.log(e.response?.data?.message);
    }
  }

  async signup(email: string, username: string, password: string) {
    try {
      await AuthService.signup(email, username, password);
    } catch (e: any) {
      console.log(e.response?.data?.message);
    }
  }

  async logout() {
    try {
      await AuthService.logout();
      localStorage.removeItem("token");
      this.setAuthState(false);
    } catch (e: any) {
      console.log(e.response?.data?.message);
    }
  }

  async checkAuth() {
    this.setLoading(true);

    try {
      const response = await axios.post<AuthResponse>(
        `${API_URL}/refresh/`,
        {},
        {
          withCredentials: true,
        }
      );
      localStorage.setItem("token", response.data.token);
      this.setAuthState(true);
    } catch (e: any) {
      console.log(e.response?.data?.message);
    } finally {
      this.setLoading(false);
    }
  }

  async getProfile() {
    try {
      const response = await ProfileService.profile();
      this.setProfile({
        email: response.data.email,
        username: response.data.username,
      });
    } catch (e: any) {
      console.log(e.response?.data?.message);
    }
  }

  async changePassword(oldPass: string, newPass: string) {
    try {
      await ProfileService.changePassword(oldPass, newPass);
    } catch (e: any) {
      console.log(e.response?.data?.message);
    }
  }

  async createGroup(title: string, type: string) {
    try {
      const response = await GroupService.createGroup(title, type);

      if (type === "channel") this.addChannelGroup(response.data);
      else if (type === "video") this.addVideoGroup(response.data);
    } catch (e: any) {
      console.log(e.response?.data?.message);
    }
  }

  async getGroups(type: string) {
    try {
      if (type === "channel") {
        const response = await GroupService.getChannelGroups();
        this.setChannelGroups(response.data);
      } else if (type === "video") {
        const response = await GroupService.getVideoGroups();
        this.setVideoGroups(response.data);
      }
    } catch (e: any) {
      console.log(e.response?.data?.message);
    }
  }

  async addVideoToGroup(videoId: string) {
    try {
      const response = await GroupService.addVideoToGroup(
        this.choosed_group_id,
        videoId
      );

      this.videos[response.data.id] = response.data;
    } catch (e: any) {
      const response = e;
      if (response.response.status === 400) {
        await GroupService.downloadVideo(videoId);
        alert(
          "Создан запрос на скачивание видео. Попробуйте добавить его в группу позже"
        );
      }
    }
  }

  async getVideosInGroup() {
    try {
      const response = await GroupService.getVideosInGroup(
        this.choosed_group_id
      );

      this.videos = response.data["videos"];
    } catch (e: any) {
      console.log(e.response?.data?.message);
    }
  }

  async addChannelToGroup(customUrl: string) {
    try {
      const reg =
        "(?:https?:\\/\\/)?(?:www\\.)?youtube\\.com\\/(@?[a-zA-Z0-9_]+)";
      const matches = customUrl.match(reg);
      if (!matches || matches.length < 2) return;

      const response = await GroupService.addChannelToGroup(
        this.choosed_group_id,
        matches[1].toLowerCase()
      );

      this.channels[response.data.id] = response.data;
    } catch (e: any) {
      const response = e;
      if (response.response.status === 400) {
        await GroupService.downloadChannel(customUrl);
        alert(
          "Создан запрос на скачивание канала. Попробуйте добавить его в группу позже"
        );
      }
    }
  }

  async getChannelsInGroup() {
    try {
      const response = await GroupService.getChannelsInGroup(
        this.choosed_group_id
      );

      this.channels = response.data["channel"];
    } catch (e: any) {
      console.log(e.response?.data?.message);
    }
  }
}
