import { createContext } from "react";
import { type UseQueryResult } from "@tanstack/react-query";
import { type User } from "./AuthProvider";

export const AuthContext = createContext<{
  userStatus: UseQueryResult<User, Response> | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}>({
  userStatus: null,
  login: async () => {},
  logout: async () => {},
});
