import { UserCircleIcon } from "@heroicons/react/24/solid";
import type { User } from "../../components/context/AuthProvider";

export const UserDropdown = ({
  user,
  logout,
}: {
  user: User | undefined;
  logout: () => void;
}) => {
  const isLoggedIn = !!user?.username;
  return (
    <div className="flex items-center h-full gap-2">
      {!isLoggedIn && <>
          <a
            href="/register"
            className="py-2 px-4 border-2 border-gray-400 rounded-md hover:border-secondary hover:bg-secondary hover:text-white"
          >
            Sign Up
          </a>
          <a
            href="/login"
            className="py-2 px-4 bg-gray-500 hover:bg-secondary text-white rounded-md"
          >
            Log In
          </a>
        </>
      }
      {isLoggedIn && <>
        <details className="relative">
          <summary className="px-2 py-2 rounded-xl flex flex-row gap-x-2 w-min cursor-pointer">
            <UserCircleIcon className="h-8 w-8  mr-2" />
          </summary>
          <div className="flex flex-col min-w-64 border-1 border-gray-300 absolute bg-white p-4 rounded-xl w-max right-0 gap-3">
            <p>{user?.username}</p>
            <button
              type="button"
              className="p-2 bg-gray-500 hover:bg-secondary text-white rounded-md"
              onClick={logout}
            >
              Log Out
            </button>
          </div>
        </details>
      </>}
    </div>
  );
};
