import { Outlet } from "react-router-dom";
import Header from "./header/Header";

const MainLayout = () => {
  return (
    <div className="flex h-dvh w-full flex-col overflow-hidden">
      <Header />
      <main className="min-h-0 w-full flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
};

export default MainLayout;
