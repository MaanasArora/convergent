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
    <>
      {!isLoggedIn && (
        <div className="flex gap-2">
          <a
            href="/register"
            className="mb-8 p-2 border-2 rounded-md hover:border-secondary hover:bg-secondary hover:text-white"
          >
            Sign Up
          </a>
          <a
            href="/login"
            className="mb-8 p-2 bg-gray-500 hover:bg-secondary text-white rounded-md"
          >
            Log In
          </a>
        </div>
      )}
      {isLoggedIn && (
        <details className="relative">
          <summary className="px-2 py-2 rounded-xl flex flex-row gap-x-2 w-min cursor-pointer">
            <UserCircleIcon className="h-8 w-8  mr-2" />
          </summary>
          <div className="flex flex-col border-2 absolute bg-white p-4 rounded-xl w-max right-0 gap-2">
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
      )}
    </>
  );
};
