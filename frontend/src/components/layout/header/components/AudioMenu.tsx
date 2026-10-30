import { NavLink } from "react-router-dom";

const EmployeeMenu = () => {
  return (
    <NavLink
      to="/audio-tools"
      className={({ isActive }) =>
        `rounded-md px-3 py-2 text-sm font-medium transition-colors ${
          isActive
            ? "bg-accent text-accent-foreground"
            : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
        }`
      }
    >
      Audio Tools
    </NavLink>
  );
};

export default EmployeeMenu;
