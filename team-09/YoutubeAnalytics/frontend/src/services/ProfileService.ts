import $api from "../http";
import { AxiosResponse } from "axios";
import { ProfileResponse } from "../models/response/ProfileResponse";

export default class ProfileService {
  static async profile(): Promise<AxiosResponse<ProfileResponse>> {
    return $api.get("profile/");
  }

  static async changePassword(oldPass: string, newPass: string) {
    return $api.post("reset-password/", {
      old_password: oldPass,
      new_password: newPass,
    });
  }
}
