import { useContext, useEffect } from "react";
import { useNavigate } from "react-router";
import { AuthContext } from "../../components/context/AuthContext";
import Logo from "../../components/ui/logo";
import { UserDropdown } from "../auth/UserDropdown";

const AppBar = ({ children }: { children: React.ReactNode }) => (
  <div
    id="app-bar"
    className="w-full p-3 pl-5 flex items-center justify-between border-b-gray-200 border-b-2"
  >
    <div className="flex items-center">
      <Logo />
      <h1 className="ml-3 mr-16 text-xl font-bold">Convergent</h1>
    </div>
    <div className="flex justify-end w-1/6">{children}</div>
  </div>
);

const CoreBase = ({
  children,
  requiresLogin = false,
}: {
  children: React.ReactNode;
  requiresLogin?: boolean;
}) => {
  const { userStatus, logout } = useContext(AuthContext);

  const navigate = useNavigate();

  useEffect(() => {
    if (userStatus?.isError && requiresLogin) {
      navigate("/login");
    }
  }, [navigate, requiresLogin, userStatus?.isError]);

  return (
    <div
      id="core-base"
      className="h-screen w-screen flex flex-col items-center"
    >
      <div className="w-full h-16">
        <AppBar>
          <UserDropdown user={userStatus?.data} logout={logout} />
        </AppBar>
      </div>
      <div className="grow w-full overflow-y-auto pt-4">
        {userStatus?.isLoading ? <>Loading...</> : children}
      </div>
    </div>
  );
};

export default CoreBase;
