import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { Toaster } from "sonner";
import { routes } from "./router/routes";

const router = createBrowserRouter(routes);

function App() {
  return (
    <>
      <RouterProvider router={router} />
      <Toaster richColors position="top-right" closeButton />
    </>
  );
}

export default App;
