import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createBrowserRouter, RouterProvider } from "react-router";
import LoginPage from "./app/auth/login";
import RegisterPage from "./app/auth/register";
import ConversationConfigPage from "./app/core/ConversationConfigPage";
import ConversationPage from "./app/core/conversation";
import DashboardPage from "./app/core/dashboard";
import { AuthProvider } from "./components/context/AuthProvider";
import ManageComments from "./components/conversation/ManageComments";
import ManageDistribution from "./components/conversation/ManageDistribution";

const queryClient = new QueryClient();

const router = createBrowserRouter([
  {
    path: "/",
    children: [
      { index: true, Component: DashboardPage },
      { path: "login", Component: LoginPage },
      { path: "register", Component: RegisterPage },
      { path: "home", Component: DashboardPage },
      { path: "dashboard", Component: DashboardPage },
      {
        path: "conversation",
        children: [
          { index: true, Component: DashboardPage },
          {
            path: "new",
            Component: ConversationConfigPage,
          },
          {
            path: ":conversationId",
            children: [
              { index: true, Component: ConversationPage },
              {
                path: "edit",
                Component: ConversationConfigPage,
                children: [
                  { index: true, Component: ManageComments },
                  {
                    path: "monitor",
                    Component: () => <></>,
                  },
                  {
                    path: "distribute",
                    Component: ManageDistribution,
                  },
                  {
                    path: "moderate",
                    Component: ManageComments,
                    children: [{ index: true, Component: ManageComments }],
                  },
                ],
              },
            ],
          },
        ],
      },
    ],
  },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </QueryClientProvider>
  </StrictMode>,
);
