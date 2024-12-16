import $api from "../http";
import { AxiosResponse } from "axios";
import { AuthResponse } from "../models/response/AuthResponse";

export default class AuthService {
  static async login(
    emailOrUsername: string,
    password: string
  ): Promise<AxiosResponse<AuthResponse>> {
    return $api.post<AuthResponse>("login/", {
      username: emailOrUsername,
      password,
    });
  }

  static async signup(
    email: string,
    username: string,
    password: string
  ): Promise<AxiosResponse> {
    return $api.post("/signup/", {
      email,
      username,
      password,
    });
  }

  static async logout(): Promise<void> {
    return $api.post("logout/");
  }
}
