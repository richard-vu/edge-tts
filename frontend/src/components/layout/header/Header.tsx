import {
  EmployeeMenu,
  Theme
} from "./components";

const Header = () => {
  return (
    <div className="bg-background border-b w-full">
      {/* Top Row */}
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-2">
          <EmployeeMenu />
        </div>

        <div className="flex items-center gap-2">
          <Theme />
        </div>
      </div>
    </div>
  );
};

export default Header;
