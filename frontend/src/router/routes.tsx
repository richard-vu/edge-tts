import { MainLayout } from "@/components/layout";
import Audio from "@/features/audio/pages/Audio";
import { Navigate, type RouteObject } from "react-router-dom";

export type AppRouteObject = RouteObject & {
  id?: string;
  label?: string;
  children?: AppRouteObject[];
};

export const routes: AppRouteObject[] = [
  {
    path: "/",
    element: <MainLayout />,
    children: [
      { index: true, element: <Navigate to="/audio-tools" replace /> },
      { path: "audio-tools", element: <Audio /> },
    ],
  },
];
